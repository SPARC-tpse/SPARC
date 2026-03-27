from datetime import datetime
from typing import Any, cast

from django.db import transaction
from django.db.models import F, Q, Sum
from django.http import JsonResponse, QueryDict
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.request import Request

from ..models import Order, Process, Resource, Worker
from ..serializers.order_serializer import OrderSerializer
from ..serializers.process_serializer import ProcessSerializer
from . import broadcast_db_change


@api_view(['GET'])
def get_order(request: Request, order_id: int) -> JsonResponse:
    """Returns an order for a given order-id"""
    try:
        order = Order.objects.get(id=order_id)
        serializer = OrderSerializer(order)
        return JsonResponse(serializer.data, safe=True)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        print(e, flush=True)
        return JsonResponse({'error': 'Order not found'}, status=500)


@api_view(['GET'])
def get_orders(request: Request) -> JsonResponse:
    """Returns all orders"""
    try:
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        print(e, flush=True)
        return JsonResponse({'error': 'Failed to retrieve orders'}, status=500)


@api_view(['GET'])
def get_order_processes(request: Request, order_id: int) -> JsonResponse:
    """Returns all processes for a given order-id"""
    try:
        process = Process.objects.filter(order__id=order_id)
        serializer = ProcessSerializer(process, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Process.DoesNotExist:
        return JsonResponse({'error': 'Process not found'}, status=404)
    except Exception as e:
        print(e, flush=True)
        return JsonResponse({'error': 'Process not found'}, status=500)


def _parse_order_payload(data: dict[str, Any] | QueryDict) -> tuple[dict[str, Any], str] | tuple[None, str]:
    """Validate and normalise the order fields. Returns (payload, error)."""
    try:
        target_amount = int(data['target_amount'])
    except (KeyError, ValueError):
        return None, 'target_amount must be an integer'

    if target_amount < 0:
        return None, 'target_amount must not be negative'

    try:
        start_date = datetime.fromisoformat(data['start_date'])
        end_date   = datetime.fromisoformat(data['end_date']).date()
    except (KeyError, ValueError):
        return None, 'start_date and end_date must be valid ISO strings'

    if start_date.date() >= end_date:
        return None, 'start_date must be before end_date'

    return {
        'name':          str(data['name']),
        'target_amount': target_amount,
        'start_date':    start_date,
        'end_date':      end_date,
        'product_name':  str(data['product_name']),
        'priority':      int(data['priority']),
        'status':        int(data['status']),
        'comments':      str(data.get('comments', '')),
    }, ''


def _build_order_number(start_date: datetime) -> str | None:
    """
    Generate a zero-padded order number for the given date.
    Uses select_for_update() to prevent race conditions under concurrent requests.
    Returns None if the daily limit is exceeded.
    """
    date_only = start_date.date()
    # Lock the rows so concurrent requests can't grab the same num
    num = (
        Order.objects
        .filter(start_date__date=date_only)
        .select_for_update()
        .count()
    )
    if num > 999:
        return None
    prefix = date_only.strftime('%Y%m%d')
    return f'{prefix}{num:03d}'


def _create_processes(order: Order, processes_data: list) -> str:
    """
    Validate and bulk-create all processes for an order.
    Returns an error string, or '' on success.
    """
    print("hi1", flush=True)
    # 1. collect every worker/resource id we'll need up front
    all_worker_ids   = {w_id for p in processes_data for w_id in p.get('workers', [])}
    print("hi2", flush=True)
    all_resource_ids = {p['resource'] for p in processes_data if p.get('resource')}
    print("hi3", flush=True)
    if not all_worker_ids:
        return 'No worker ids provided for any process'
    print("hi4", flush=True)
    # single query each — avoids per-process DB round trips
    workers_by_id   = Worker.objects.in_bulk(all_worker_ids)
    print("hi5", flush=True)
    resources_by_id = Resource.objects.in_bulk(all_resource_ids)
    print("hi6", flush=True)
    # 2. pre-fetch all existing processes for those resources at once
    #    (one query instead of one per process in the loop)
    existing_resource_procs = (
        Process.objects
        .filter(resource_id__in=all_resource_ids)
        .exclude(order=order)
        .select_related('order')          # avoids per-proc order lookup
        .annotate(
            prior_time=Sum(
                'order__process__approximated_time',
                filter=Q(order__process__id__lt=F('id'))
            )
        )
    )
    print("hi7", flush=True)
    # group by resource for O(1) conflict lookup
    procs_by_resource: dict[int, list] = {}
    for proc in existing_resource_procs:
        if proc.resource is not None:
            procs_by_resource.setdefault(proc.resource.id, []).append(proc)
    print("hi8", flush=True)
    # 3. iterate and validate
    new_processes      = []   # Process instances to bulk_create
    process_worker_map = []   # [(process_index, [Worker, ...]), ...]
    cumulative_seconds = 0    # running total for start-time calculation

    for process_data in processes_data:
        # workers
        worker_ids = process_data.get('workers', [])
        workers = [workers_by_id[w_id] for w_id in worker_ids if w_id in workers_by_id]
        missing = set(worker_ids) - set(workers_by_id)
        if missing:
            return f'Workers not found: {sorted(missing)}'
        if not workers:
            return f'No valid workers provided for process "{process_data.get("name")}"'

        # resource
        resource_id = process_data.get('resource')
        if resource_id is None:
            return 'No resource was given for a process'
        resource = resources_by_id.get(resource_id)
        if not resource:
            return f'No resource exists with id: {resource_id}'

        # timing
        t = process_data['approximated_time']
        approximated_time = (
            int(t['h']) * 3600 + int(t['m']) * 60 + int(t['s'])
        )
        process_start = order.start_date + timezone.timedelta(seconds=cumulative_seconds)
        process_end   = process_start + timezone.timedelta(seconds=approximated_time)

        # conflict check against pre-fetched procs (pure Python, no extra queries)
        for proc in procs_by_resource.get(resource_id, []):
            prior = proc.prior_time or 0
            proc_start_dt = timezone.datetime.combine(
                proc.order.start_date, timezone.datetime.min.time(),
                tzinfo=timezone.get_current_timezone()
            )
            proc_start = proc_start_dt + timezone.timedelta(seconds=prior)
            proc_end   = proc_start + timezone.timedelta(seconds=proc.approximated_time)

            if process_start < proc_end and process_end > proc_start:
                return (
                    f'Resource {resource_id} is busy with "{proc.name}" '
                    f'from {proc_start} to {proc_end}'
                )

        cumulative_seconds += approximated_time
        proc_obj = Process(
            name=process_data['name'],
            approximated_time=approximated_time,
            resource=resource,
            order=order,
        )
        new_processes.append(proc_obj)
        process_worker_map.append(workers)

    print("hi9", flush=True)
    # 4. bulk insert all processes (1 query instead of N)
    created = Process.objects.bulk_create(new_processes)
    print("hi10", flush=True)
    # 5. set M2M workers in bulk
    for proc, workers in zip(created, process_worker_map):
        proc.workers.set(workers)   # set() is more efficient than repeated add()
    print("hi11", flush=True)
    return ''


@api_view(['POST'])
def create_order(request: Request) -> JsonResponse:
    """Create a new order and its associated processes"""

    if not isinstance(request.data, (dict, QueryDict)):
        return JsonResponse({'error': 'Invalid request body'}, status=400)

    data: dict[str, Any] = (
        dict(request.data)
        if isinstance(request.data, QueryDict)
        else request.data
    )

    payload, error = _parse_order_payload(data)
    if error:
        return JsonResponse({'error': error}, status=400)

    assert payload is not None

    processes_data: list[Any] = cast(list[Any], data.get('process', []))
    if not isinstance(processes_data, list):
        return JsonResponse({'error': 'process must be a list'}, status=400)
    #if not processes_data:
    #    return JsonResponse({'error': 'At least one process is required'}, status=400)

    with transaction.atomic():
        order_number = _build_order_number(payload['start_date'])
        if order_number is None:
            return JsonResponse({'error': 'Order limit reached for this date (max 999)'}, status=400)

        new_order = Order.objects.create(**payload, order_number=order_number)

        if processes_data:
            err = _create_processes(new_order, processes_data)
            if err:
                print("Err", flush=True)
                raise ValueError(err)

    serializer = OrderSerializer(new_order)

    broadcast_db_change('order', 'created', serializer.data)

    return JsonResponse(serializer.data, status=201)


def _sync_processes(order: Order, processes_data: list) -> str:
    """
    Upsert processes for an existing order and delete any that were removed.
    Returns an error string, or '' on success.
    """
    # 1. bulk-fetch every worker/resource we'll need
    all_worker_ids   = {w_id for p in processes_data for w_id in p.get('workers', [])}
    all_resource_ids = {p['resource'] for p in processes_data if p.get('resource')}

    workers_by_id   = Worker.objects.in_bulk(all_worker_ids)
    resources_by_id = Resource.objects.in_bulk(all_resource_ids)

    # 2. pre-fetch existing resource conflicts in one query
    existing_resource_procs = (
        Process.objects
        .filter(resource_id__in=all_resource_ids)
        .exclude(order=order)
        .select_related('order')
        .annotate(
            prior_time=Sum(
                'order__process__approximated_time',
                filter=Q(order__process__id__lt=F('id'))
            )
        )
    )
    procs_by_resource: dict[int, list] = {}
    for proc in existing_resource_procs:
        if proc.resource is not None:
            procs_by_resource.setdefault(proc.resource.id, []).append(proc)

    # 3. separate incoming processes into creates vs updates
    incoming_ids        = set()   # process ids present in the payload
    to_create           = []      # (process_data, workers, approximated_time)
    to_update           = []      # (Process instance, process_data, workers, approximated_time)

    cumulative_seconds = 0

    for process_data in processes_data:
        # workers
        worker_ids = process_data.get('workers', [])
        workers    = [workers_by_id[w] for w in worker_ids if w in workers_by_id]
        missing    = set(worker_ids) - set(workers_by_id)
        if missing:
            return f'Workers not found: {sorted(missing)}'
        if not workers:
            return f'No valid workers for process "{process_data.get("name")}"'

        # resource
        resource_id = process_data.get('resource')
        if resource_id is None:
            return 'No resource given for a process'
        resource = resources_by_id.get(resource_id)
        if not resource:
            return f'No resource exists with id: {resource_id}'

        # timing
        t = process_data['approximated_time']
        approximated_time = int(t['h']) * 3600 + int(t['m']) * 60 + int(t['s'])
        process_start = order.start_date + timezone.timedelta(seconds=cumulative_seconds)
        process_end   = process_start + timezone.timedelta(seconds=approximated_time)

        # conflict check (pure Python — no extra queries)
        for proc in procs_by_resource.get(resource_id, []):
            prior = proc.prior_time or 0
            proc_start_dt = timezone.datetime.combine(
                proc.order.start_date, timezone.datetime.min.time(),
                tzinfo=timezone.get_current_timezone()
            )
            proc_start = proc_start_dt + timezone.timedelta(seconds=prior)
            proc_end   = proc_start + timezone.timedelta(seconds=proc.approximated_time)

            if process_start < proc_end and process_end > proc_start:
                return (
                    f'Resource {resource_id} is busy with "{proc.name}" '
                    f'from {proc_start} to {proc_end}'
                )

        cumulative_seconds += approximated_time

        process_id = process_data.get('id')
        if process_id is None:
            to_create.append((process_data, workers, approximated_time, resource))
        else:
            incoming_ids.add(process_id)
            to_update.append((process_id, process_data, workers, approximated_time, resource))

    # 4. delete processes that were removed from the payload
    #    (the original code never did this, leaving stale rows)
    Process.objects.filter(order=order).exclude(id__in=incoming_ids).delete()

    # 5. bulk-create new processes
    if to_create:
        new_objs = [
            Process(
                name=pd['name'],
                approximated_time=secs,
                resource=res,
                order=order,
            )
            for pd, _, secs, res in to_create
        ]
        created = Process.objects.bulk_create(new_objs)
        for proc, (_, workers, _, _) in zip(created, to_create):
            proc.workers.set(workers)   # set() replaces; add() was appending duplicates

    # 6. bulk-update existing processes (2 queries regardless of count)
    if to_update:
        proc_ids    = [pid for pid, *_ in to_update]
        procs_in_db = {p.id: p for p in Process.objects.filter(id__in=proc_ids, order=order)}

        updated_objs = []
        for pid, pd, workers, secs, res in to_update:
            proc = procs_in_db.get(pid)
            if proc is None:
                return f'Process id {pid} not found on this order'
            proc.name              = pd['name']
            proc.approximated_time = secs
            proc.resource          = res
            updated_objs.append(proc)

        # single UPDATE touching only the changed columns
        Process.objects.bulk_update(updated_objs, ['name', 'approximated_time', 'resource'])

        for proc, (_, _, workers, _, _) in zip(updated_objs, to_update):
            proc.workers.set(workers)   # replaces the full M2M set cleanly

    return ''


@api_view(['PUT'])
def update_order(request: Request, order_id: int) -> JsonResponse:
    """Update an order and sync its processes."""
    print("hi1", flush=True)
    # 1. Fixes "type[Empty] is not assignable" — same guard as create_order
    if not isinstance(request.data, (dict, QueryDict)):
        return JsonResponse({'error': 'Invalid request body'}, status=400)
    print("hi2", flush=True)
    data: dict[str, Any] = (
        dict(request.data)
        if isinstance(request.data, QueryDict)
        else request.data
    )
    print("hi3", flush=True)
    payload, error = _parse_order_payload(data)
    if error:
        return JsonResponse({'error': error}, status=400)
    print("hi4", flush=True)
    # 2. Fixes "'items'/'keys' is not a known attribute of None"
    assert payload is not None
    print("hi5", flush=True)
    processes_data: list[Any] = cast(list[Any], data.get('process', []))
    print("hi6", flush=True)
    if not isinstance(processes_data, list):
        return JsonResponse({'error': 'process must be a list'}, status=400)
    if not processes_data:
        return JsonResponse({'error': 'At least one process is required'}, status=400)
    print("hi7", flush=True)
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)
            print("hi8", flush=True)
            for field, value in payload.items():
                setattr(order, field, value)
            order.save(update_fields=list(payload.keys()))
            print("hi9", flush=True)
            err = _sync_processes(order, processes_data)
            print("hi9.1", flush=True)
            if err:
                raise ValueError(err)
            print("hi9.2", flush=True)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    print("hi10", flush=True)
    serializer = OrderSerializer(order)
    print("hi11", flush=True)
    # 4. Fixes "ReturnList is not assignable to Dict[str, Any]"
    broadcast_db_change('order', 'updated', cast(dict[str, Any], serializer.data))
    print("hi12", flush=True)
    return JsonResponse(serializer.data, status=200)


@api_view(['DELETE'])
def delete_order(request: Request, order_id: int) -> JsonResponse:
    """Delete an order by order-id"""
    try:
        order = Order.objects.get(id=order_id)
        order.delete()
        broadcast_db_change('order', 'deleted', {'id': order_id})
        return JsonResponse({'message': 'Order deleted successfully'})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)


@api_view(['GET'])
def get_order_approximated_time(request: Request, order_id: int) -> JsonResponse:
    """Get the approximated time for an order by order-id"""
    try:
        processes = Process.objects.all().filter(order__id=order_id)
        sum: int = 0
        for process in processes:
            sum = sum + process.approximated_time
        return JsonResponse({'approximated_time': sum}, status=200)
    except Process.DoesNotExist:
        return JsonResponse({'error': 'Process not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
