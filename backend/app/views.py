from typing import Dict, Any

from OpenSSL.rand import status
from django.db.models import Sum
from django.utils import timezone
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
from rest_framework.request import Request
from .models import Order, Process, Worker, Resource, OrderFile, ResourceType, Disruption, DisruptionType, Part
from .serializers import OrderSerializer, WorkerSerializer, OrderFileSerializer, ResourceSerializer, \
    DisruptionSerializer, ProcessSerializer, PartSerializer
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime

def broadcast_db_change(model: str, action: str, order_data: Dict[str, Any] = None) -> None:
    """Helper to broadcast database changes via WebSocket"""
    channel_layer = get_channel_layer()
    s = model + '_' + model
    model_type = model + '_message'
    async_to_sync(channel_layer.group_send)(
        s,
        {
            'type': model_type,
            'action': action,
            'data': order_data
        }
    )

# --- ORDER ---
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
        # safe must be set to false because serializer.data is a list of json objects and not a json object itself
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

@api_view(['POST'])
def create_order(request: Request) -> JsonResponse:
    # TODO: this function should be split into create_order and create_processes functions, so each function only has one functionality for good design.
    """Create a new order and its processes"""
    try:
        priority = request.data.get('priority')
        status = request.data.get('status')
        target_amount = int(request.data['target_amount'])
        if target_amount < 0:
            return JsonResponse({'error': f'Target amount is negative'}, status=400)
        start_date = datetime.fromisoformat(request.data['start_date'])
        end_date = datetime.fromisoformat(request.data['end_date'])

        # check if the start date is before the end date
        if not start_date < end_date:
            return JsonResponse({'error': f'Negative date bounds'}, status=400)

        # get number of orders at the same day
        num = Order.objects.filter(start_date=start_date).count()
        if num > 999:
            return JsonResponse({'error': f'Order overflow (for today)'}, status=400)
        order_number = str(start_date)[:-9].replace("-", "") + str(num).zfill(3)

        new_order = Order(
            name = str(request.data['name']),
            order_number = order_number,
            target_amount = target_amount,
            start_date = str(start_date),
            end_date = str(request.data['end_date']),
            product_name = str(request.data['product_name']),
            priority = int(priority),
            status = int(status),
            comments = str(request.data['comments']),
        )
        new_order.save()

        for process in request.data['process']:
            worker_ids = process.get('workers', [])
            workers = []
            for w_id in worker_ids:
                workers.append(Worker.objects.get(pk=w_id))
            # check if any workers where found with that match the list of ids
            if len(workers) == 0:
                return JsonResponse({'error': f'No workers exists with id: {process.get('workers', [])}'}, status=400)

            if process['resource'] == None:
                return JsonResponse({'error': f'No resource was given'}, status=400)
            resource = Resource.objects.get(pk=process['resource'])
            if not resource:
                return JsonResponse({'error': f'No resource exists with id: {process["resource"]}'}, status=400)

            # convert approximated_time into seconds
            approximated_time = int(process['approximated_time']['h']) * 60 * 60 + int(process['approximated_time']['m']) * 60 + int(process['approximated_time']['s'])

            #start_dt = timezone.datetime.combine(new_order.start_date, timezone.datetime.min.time())
            existing_time = Process.objects.filter(order=new_order).aggregate(
                total=Sum('approximated_time')
            )['total'] or 0
            process_start = start_date + timezone.timedelta(seconds=existing_time)
            process_end = process_start + timezone.timedelta(seconds=approximated_time)

            # check if resource isn't already in use
            conflicts = []
            resource_processes = Process.objects.filter(resource_id=process['resource']).exclude(order=new_order)
            for proc in resource_processes:
                proc_order = proc.order
                proc_start_dt = timezone.datetime.combine(proc_order.start_date, timezone.datetime.min.time())
                prior_time = Process.objects.filter(order=proc_order, id__lt=proc.id).aggregate(
                    total=Sum('approximated_time')
                )['total'] or 0
                proc_start = proc_start_dt + timezone.timedelta(seconds=prior_time)
                proc_end = proc_start + timezone.timedelta(seconds=proc.approximated_time)

                if process_start < proc_end and process_end > proc_start:
                    conflicts.append(
                        f"Resource {process['resource']} is busy with process '{proc.name}' from {proc_start} to {proc_end}")

            if len(conflicts) != 0:
                return JsonResponse({'error': f'Resource (id: {process["resource"]}) is already in use at that time.'}, status=400)

            new_process = Process.objects.create(
                name = process['name'],
                approximated_time = approximated_time,
                resource = resource,
                order = new_order
            )
            new_process.save()
            # set Many-to-Many relationship for worker
            for worker in workers:
                new_process.workers.add(worker)

        # broadcast the change
        serializer = OrderSerializer(new_order)
        broadcast_db_change('order','created', serializer.data)

        return JsonResponse({'id': new_order.id, 'message': 'Order created successfully'}, status=201)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except IntegrityError as e:
        return JsonResponse({'error': 'Database integrity error'}, status=400)
    except KeyError as e:
        return JsonResponse({'error': f'Missing field: {str(e)}'}, status=400)
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Failed to create order'}, status=500)

@api_view(['PUT'])
def update_order(request: Request, order_id: int) -> JsonResponse:
    """Update an order by order-id"""
    # TODO: add helper method for redundant code compared to create order(?)
    try:
        # get order
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)

        target_amount = int(request.data['target_amount'])
        if target_amount < 0:
            return JsonResponse({'error': f'Target amount is negative'}, status=400)

        start_date = datetime.fromisoformat(request.data['start_date'])
        end_date = datetime.fromisoformat(request.data['end_date'])
        # check if the start date is before the end date
        if not start_date < end_date:
            return JsonResponse({'error': f'Negative date bounds'}, status=400)

        # base data update
        order.name = request.data.get('name')
        order.target_amount = target_amount
        order.start_date = str(start_date)
        order.end_date = str(request.data.get('end_date'))
        order.product_name = request.data.get('product_name')
        order.priority = int(request.data.get('priority'))
        order.status = int(request.data.get('status'))
        order.comments = request.data.get('comments')
        order.save()

        # process steps update
        for process_data in request.data['process']:
            print(process_data, flush=True)

            worker_ids = process_data.get('workers', [])
            workers = []
            for w_id in worker_ids:
                workers.append(Worker.objects.get(pk=w_id))
            # check if any workers where found with that match the list of ids
            if len(workers) == 0:
                return JsonResponse({'error': f'No workers exists with id: {process_data.get('workers', [])}'},
                                    status=400)

            if process_data['resource'] == None:
                return JsonResponse({'error': f'No resource was given'}, status=400)
            resource = Resource.objects.get(pk=process_data['resource'])
            if not resource:
                return JsonResponse({'error': f'No resource exists with id: {process_data['resource']}'}, status=400)

            # convert approximated_time into seconds
            approximated_time = int(process_data['approximated_time']['h']) * 60 * 60 + int(
                process_data['approximated_time']['m']) * 60 + int(process_data['approximated_time']['s'])

            existing_time = Process.objects.filter(order=order).aggregate(
                total=Sum('approximated_time')
            )['total'] or 0
            process_start = start_date + timezone.timedelta(seconds=existing_time)
            process_end = process_start + timezone.timedelta(seconds=approximated_time)

            # check if resource isn't already in use
            conflicts = []
            resource_processes = Process.objects.filter(resource_id=process_data['resource']).exclude(
                order=order)
            for proc in resource_processes:
                proc_order = proc.order
                proc_start_dt = timezone.datetime.combine(proc_order.start_date, timezone.datetime.min.time())
                prior_time = Process.objects.filter(order=proc_order, id__lt=proc.id).aggregate(
                    total=Sum('approximated_time')
                )['total'] or 0
                proc_start = proc_start_dt + timezone.timedelta(seconds=prior_time)
                proc_end = proc_start + timezone.timedelta(seconds=proc.approximated_time)

                if process_start < proc_end and process_end > proc_start:
                    conflicts.append(
                        f"Resource {process_data['resource']} is busy with process '{proc.name}' from {proc_start} to {proc_end}")

            if len(conflicts) != 0:
                return JsonResponse(
                    {'error': f'Resource (id: {process_data['resource']}) is already in use at that time.'},
                    status=400)

            if process_data['id'] == None:
                # create new process
                new_process = Process.objects.create(
                    name=process_data['name'],
                    approximated_time=approximated_time,
                    resource=resource,
                    order=order
                )
                new_process.save()
                # set Many-to-Many relationship for worker
                for worker in workers:
                    new_process.workers.add(worker)
            else:
                # get process by id and assign the attributes new
                try :
                    process = Process.objects.get(id=process_data['id'])
                    process.name = process_data['name']
                    process.order = order
                    process.resource = resource
                    process.approximated_time = approximated_time
                    process.save()
                    for worker in workers:
                        process.workers.add(worker)
                except Process.DoesNotExist:
                    return JsonResponse({'error': 'Process not found'}, status=404)
                except Exception as e:
                    print(e, flush=True)
                    return JsonResponse({'error': 'Process not found'}, status=500)

        # broadcast the change
        serializer = OrderSerializer(order)
        broadcast_db_change('order', 'updated', serializer.data)
        return JsonResponse({'message': 'Order updated successfully'})
    except Exception as e:
        print(f"Update Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

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

# --- ORDER/FILES ---
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_order_file(request):
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)

        file = request.FILES['file']
        file_type = request.POST.get('type', 'general')
        order_id = request.POST.get('order_id')

        if not order_id:
            return JsonResponse({'error': 'order_id is required'}, status=400)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)

        order_file = OrderFile(order=order, file=file, file_type=file_type)
        order_file.save()
        serializer = OrderFileSerializer(order_file, context={'request': request})
        return JsonResponse(serializer.data, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['DELETE'])
def delete_order_file(request, file_id):
    try:
        order_file = OrderFile.objects.get(id=file_id)
        if order_file.file: order_file.file.delete(save=False)
        order_file.delete()
        return JsonResponse({'success': True, 'message': 'File deleted'})
    except OrderFile.DoesNotExist: return JsonResponse({'error': 'File not found'}, status=404)
    except Exception as e: return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def list_order_files(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        files = order.order_files.all()
        serializer = OrderFileSerializer(files, many=True, context={'request': request})
        return JsonResponse({'order_id': order_id, 'files': serializer.data})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# --- Process ---
@api_view(['GET'])
def get_processes(request: Request) -> JsonResponse:
    try:
        processes = Process.objects.all()
        serializer = ProcessSerializer(processes, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False)
    except Process.DoesNotExist:
        return JsonResponse({'error': 'Process not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['PUT'])
def update_process_timing(request: Request, process_id: int) -> JsonResponse:
    try:
        process = Process.objects.get(id=process_id)
        if 'setup_time' in request.data:
            process.setup_time = int(request.data['setup_time'])
        if 'waiting_time' in request.data:
            process.waiting_time = int(request.data['waiting_time'])
        process.save()
        return JsonResponse({
            'message': 'Process timing updated successfully',
            'setup_time': process.setup_time,
            'waiting_time': process.waiting_time,
        })
    except Process.DoesNotExist:
        return JsonResponse({'error': 'Process not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['DELETE'])
def delete_process(request: Request, process_id: int) -> JsonResponse:
    try:
        process = Process.objects.get(id=process_id)
        process.delete()
        return JsonResponse({'success': True, 'message': 'Process deleted'})
    except Process.DoesNotExist:
        return JsonResponse({'error': 'Process not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
def add_part(request: Request, process_id: int) -> JsonResponse:
    """Add a part to a process with the current process time"""
    try:
        process = Process.objects.get(id=process_id)
        process_time = request.data.get('process_time', 0)
        # Create Part instance
        part = Part.objects.create(
            process=process,
            process_time=process_time
        )
        part.save()
        serializer = PartSerializer(part, many=False)
        return JsonResponse(serializer.data, status=201)
    except Process.DoesNotExist:
        return JsonResponse({'error': 'Process not found'}, status=404)
    except Exception as e:
        print(f"Add part error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def get_parts(request: Request, process_id: int) -> JsonResponse:
    """Get all parts for a process"""
    try:
        parts = Part.objects.filter(process=process_id)
        serializer = PartSerializer(parts, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Part.DoesNotExist:
        return JsonResponse({'error': 'Part not found'}, status=404)
    except Exception as e:
        print(e, flush=True)
        return JsonResponse({'error': 'Failed to retrieve orders'}, status=500)


# --- Worker ---
@api_view(['GET'])
def get_workers(request: Request) -> JsonResponse:
    """Get all workers"""
    try:
        workers = Worker.objects.all()
        serializer = WorkerSerializer(workers, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['DELETE'])
def delete_worker(request: Request, worker_id: int) -> JsonResponse:
    try:
        Worker.objects.get(id=worker_id).delete()
        return JsonResponse({'success': True, 'message': 'Worker deleted'})
    except Worker.DoesNotExist:
        return JsonResponse({'error': 'Worker not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
def create_worker(request: Request) -> JsonResponse:
    """Create a new worker"""
    try:
        serializer = WorkerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def get_worker(request: Request, worker_id: int) -> JsonResponse:
    """Get a single worker by ID"""
    try:
        worker = Worker.objects.get(id=worker_id)
        serializer = WorkerSerializer(worker, many=False)
        return JsonResponse(serializer.data, safe=False)
    except Worker.DoesNotExist:
        return JsonResponse({'error': 'Worker not found'}, status=404)

@api_view(['PUT'])
def update_worker(request: Request, worker_id: int) -> JsonResponse:
    """Update an existing worker"""
    try:
        worker = Worker.objects.get(id=worker_id)
        worker.name = request.data.get('name', worker.name)
        worker.save()
        return JsonResponse({'message': 'Worker updated successfully', 'id': worker.id, 'name': worker.name})
    except Worker.DoesNotExist:
        return JsonResponse({'error': 'Worker not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# --- RESOURCES ---
@api_view(['GET'])
def get_resources(request: Request) -> JsonResponse:
    """Get all resources"""
    try:
        resources = Resource.objects.all()
        serializer = ResourceSerializer(resources, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def get_resource(request: Request, resource_id: int) -> JsonResponse:
    """Get a single resource by ID"""
    try:
        resource = Resource.objects.get(id=resource_id)
        serializer = ResourceSerializer(resource)
        return JsonResponse(serializer.data, safe=True)
    except Resource.DoesNotExist:
        return JsonResponse({'error': 'Resource not found'}, status=404)
    except Exception as e:
        print(e, flush=True)
        return JsonResponse({'error': 'Resource not found'}, status=500)

@api_view(['POST'])
def create_resource(request: Request) -> JsonResponse:
    """Create a new resource"""
    try:
        print(request.data,flush=True)
        name = request.data.get('name')
        type_name = request.data.get('type')
        status = request.data.get('status')

        # ResourceType handling
        r_type_obj, _ = ResourceType.objects.get_or_create(
            name__iexact=type_name,
            defaults={'name': type_name}
        )

        Resource.objects.create(
            name=name,
            type=r_type_obj,
            status=int(status)
        )
        return JsonResponse({'message': 'Resource created'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['PUT'])
def update_resource(request: Request, resource_id: int) -> JsonResponse:
    """Update an existing resource"""
    try:
        r = Resource.objects.get(id=resource_id)
        r.name = request.data.get('name', r.name)
        r.status = int(request.data.get('status', r.status))

        if 'type' in request.data:
            type_name = request.data['type']
            r_type_obj, _ = ResourceType.objects.get_or_create(
                name__iexact=type_name,
                defaults={'name': type_name}
            )
            r.type = r_type_obj

        r.save()
        return JsonResponse({'message': 'Resource updated'})
    except Resource.DoesNotExist:
        return JsonResponse({'error': 'Resource not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['DELETE'])
def delete_resource(request: Request, resource_id: int) -> JsonResponse:
    """Delete an existing resource"""
    try:
        Resource.objects.get(id=resource_id).delete()
        return JsonResponse({'message': 'Resource deleted'})
    except Resource.DoesNotExist:
        return JsonResponse({'error': 'Resource not found'}, status=404)

@api_view(['GET'])
def get_resource_approximated_time(request: Request, resource_id:int) -> JsonResponse:
    """Get all processes a resource is used in"""
    try:
        processes = Process.objects.filter(resource__id=resource_id)
        res = []
        for processes in processes:
            res.append(processes.approximated_time)
        return JsonResponse({'approximated_times': res}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# --- DISRUPTIONS ---
def format_dt(dt):
    """Hilfsfunktion: Macht aus einem Datum einen sauberen String für das Frontend"""
    if not dt: return None

    return dt.strftime('%Y-%m-%dT%H:%M:%S')

@api_view(['GET'])
def get_disruptions(request: Request) -> JsonResponse:
    try:
        disruptions = Disruption.objects.all()
        serializer = DisruptionSerializer(disruptions, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def get_disruption(request: Request, disruption_id: int) -> JsonResponse:
    try:
        disruption = Disruption.objects.get(id=disruption_id)
        serializer = DisruptionSerializer(disruption)
        return JsonResponse(serializer.data, safe=True)
    except Disruption.DoesNotExist:
        return JsonResponse({'error': 'Disruption not found'}, status=404)
    except Exception as e:
        print(e, flush=True)
        return JsonResponse({'error': 'Disruption not found'}, status=500)

@api_view(['GET'])
def get_disruption_types(request: Request) -> JsonResponse:
    """Get all disruption types"""
    try:
        default_types = ['Error', 'Maintenance']

        for t_name in default_types:
            DisruptionType.objects.get_or_create(name=t_name)

        types = DisruptionType.objects.all()
        data = [{'id': t.id, 'name': t.name} for t in types]

        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
def create_disruption(request: Request) -> JsonResponse:
    """create a new disruption
    expected input format:
    {
        name: string,
        type: int,
        resource: int,
        start_date: string,
        end_date: string,
    }
    """
    try:
        type_obj = DisruptionType.objects.get(id=request.data.get('type'))
        resource_obj = Resource.objects.get(id=request.data.get('resource'))

        new_disruption = Disruption.objects.create(
            name=request.data.get('name'),
            type=type_obj,
            resource=resource_obj,
            disruption_time=request.data.get('disruption_time')
        )
        return JsonResponse({'id': new_disruption.id, 'message': 'Disruption created successfully'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['PUT'])
def update_disruption(request: Request, disruption_id: int) -> JsonResponse:
    """update an existing disruption"""
    try:
        d = Disruption.objects.get(id=disruption_id)
        data = request.data

        d.name = data.get('name', d.name)
        d.duration = data.get('disruption_time')

        if 'resource' in data:
            d.resource = Resource.objects.get(id=data['resource'])
        if 'type' in data:
            d.type = DisruptionType.objects.get(id=data['type'])

        d.save()
        return JsonResponse({'message': 'Updated'})
    except Disruption.DoesNotExist:
        return JsonResponse({'error': 'Disruption not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['DELETE'])
def delete_disruption(request: Request, disruption_id: int) -> JsonResponse:
    """Delete an existing disruption"""
    try:
        Disruption.objects.get(id=disruption_id).delete()
        return JsonResponse({'success': True, 'message': 'Disruption deleted'})
    except Disruption.DoesNotExist:
        return JsonResponse({'error': 'Disruption not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def get_disruption_chart(request: Request) -> JsonResponse:
    """Returns a chart of frequent disruption times"""
    try:
        res = [
            {
                "duration": "0–5m",
                "frequency": Disruption.objects.filter(
                    disruption_time__lt=300
                ).count()
            },
            {
                "duration": "5–15m",
                "frequency": Disruption.objects.filter(
                    disruption_time__gte=300,
                    disruption_time__lt=900
                ).count()
            },
            {
                "duration": "15–30m",
                "frequency": Disruption.objects.filter(
                    disruption_time__gte=900,
                    disruption_time__lt=1800
                ).count()
            },
            {
                "duration": "30–60m",
                "frequency": Disruption.objects.filter(
                    disruption_time__gte=1800,
                    disruption_time__lt=3600
                ).count()
            },
            {
                "duration": "1–2h",
                "frequency": Disruption.objects.filter(
                    disruption_time__gte=3600,
                    disruption_time__lt=7200
                ).count()
            },
            {
                "duration": ">2h",
                "frequency": Disruption.objects.filter(
                    disruption_time__gte=7200
                ).count()
            },
        ]

        return JsonResponse(res, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
