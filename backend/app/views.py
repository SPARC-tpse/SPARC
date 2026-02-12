from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
from rest_framework.request import Request
from .models import Order, Process, Worker, Resource, OrderFile
from .serializers import OrderSerializer, WorkerSerializer, OrderFileSerializer
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def broadcast_order_change(action, order_data=None):
    """Helper to broadcast order changes via WebSocket"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'order_order',
        {
            'type': 'order_message',
            'action': action,
            'data': order_data
        }
    )

# Order

@api_view(['GET'])
def get_order(request: Request, order_id: int) -> JsonResponse:
    try:
        order = Order.objects.filter(id=order_id)
        serializer = OrderSerializer(order, many=True)
        return JsonResponse(serializer.data[0], safe=True)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Order not found'}, status=500)

@api_view(['GET'])
def get_orders(request: Request) -> JsonResponse:
    try:
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        return JsonResponse({'error': 'Failed to retrieve orders'}, status=500)

@api_view(['POST'])
def create_order(request: Request) -> JsonResponse:
    try:
        # Mapping helpers
        priority_map = {"Low": 1, "Medium": 2, "High": 3}
        status_map = {"Planned": 1, "Running": 2, "Paused": 3, "Done": 4}

        priority = priority_map.get(request.data.get('priority'), 1)
        status = status_map.get(request.data.get('status'), 1)

        new_entry = Order(
            name = str(request.data['name']),
            target_amount = int(request.data['target']),
            start_date = str(request.data['start']),
            end_date = str(request.data['end']),
            product_name = str(request.data['product']),
            priority = priority,
            status = status,
            comments = str(request.data['comments']),
        )

        process_steps = []
        for process in request.data['process']:

            worker_names = process.get('workers', [])


            workers = Worker.objects.filter(name__in=worker_names)

            resource = Resource.objects.filter(name=process['resource']).first()

            if not resource:
                return JsonResponse({'error': f'No resource exists with name: {process["resource"]}'}, status=400)

            new_process = Process.objects.create(
                name=process['name'],
                resource=resource
            )
            # Many-to-Many Beziehung setzen
            new_process.workers.set(workers)
            process_steps.append(new_process)

        new_entry.save()
        new_entry.processes.set(process_steps)

        # Broadcast the change
        serializer = OrderSerializer(new_entry)
        broadcast_order_change('created', serializer.data)

        return JsonResponse({'id': new_entry.id, 'message': 'Order created successfully'}, status=201)
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
    try:
        # getorder
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)

        # base data update
        order.name = request.data.get('name')
        order.target_amount = int(request.data.get('target_amount'))
        order.start_date = str(request.data.get('start_date'))
        order.end_date = str(request.data.get('end_date'))
        order.product_name = request.data.get('product_name')

        # mapping for prios system
        priority_map = {"Low": 1, "Medium": 2, "High": 3}
        status_map = {"Planned": 1, "Running": 2, "Paused": 3, "Done": 4}

        # no int mapping
        p_val = request.data.get('priority')
        s_val = request.data.get('status')

        if isinstance(p_val, int):
            order.priority = p_val
        else:
            order.priority = priority_map.get(p_val, order.priority)

        if isinstance(s_val, int):
            order.status = s_val
        else:
            order.status = status_map.get(s_val, order.status)

        order.comments = request.data.get('comments')
        order.save()

        # steps update
        if 'process' in request.data:

            order.processes.clear()

            new_process_steps = []

            for process_data in request.data['process']:
                worker_names = process_data.get('workers', [])

                # Worker & Resource ssearch
                workers = Worker.objects.filter(name__in=worker_names)
                resource = Resource.objects.filter(name=process_data['resource']).first()

                if not resource:

                    continue


                new_process = Process.objects.create(
                    name=process_data['name'],
                    resource=resource

                )
                new_process.workers.set(workers)
                new_process_steps.append(new_process)


            order.processes.set(new_process_steps)


        serializer = OrderSerializer(order)
        broadcast_order_change('updated', serializer.data)

        return JsonResponse({'message': 'Order updated successfully'})

    except Exception as e:
        print(f"Update Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
@api_view(['DELETE'])
def delete_order(request: Request, order_id: int) -> JsonResponse:
    print("start deleting")
    try:
        order = Order.objects.filter(id=order_id)
        order.delete()
        broadcast_order_change('deleted', {'id': order_id})
        return JsonResponse({'message': 'Order deleted successfully'})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

# Order / Files
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_order_file(request):
    try:
        if 'file' not in request.FILES: return JsonResponse({'error': 'No file provided'}, status=400)
        file = request.FILES['file']
        file_type = request.POST.get('type', 'general')
        order_id = request.POST.get('order_id')
        if not order_id: return JsonResponse({'error': 'order_id is required'}, status=400)
        try: order = Order.objects.get(id=order_id)
        except Order.DoesNotExist: return JsonResponse({'error': 'Order not found'}, status=404)
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
    except Order.DoesNotExist: return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e: return JsonResponse({'error': str(e)}, status=500)

# Process
@api_view(['PUT'])
def update_process_timing(request: Request, process_id: int) -> JsonResponse:
    try:
        process = Process.objects.get(id=process_id)
        if 'setup_time_seconds' in request.data: process.setup_time_seconds = int(request.data['setup_time_seconds'])
        if 'waiting_time_seconds' in request.data: process.waiting_time_seconds = int(request.data['waiting_time_seconds'])
        if 'process_time_seconds' in request.data: process.process_time_seconds = int(request.data['process_time_seconds'])
        process.save()
        return JsonResponse({
            'message': 'Process timing updated successfully',
            'setup_time_seconds': process.setup_time_seconds,
            'waiting_time_seconds': process.waiting_time_seconds,
            'process_time_seconds': process.process_time_seconds
        })
    except Process.DoesNotExist: return JsonResponse({'error': 'Process not found'}, status=404)
    except Exception as e: return JsonResponse({'error': str(e)}, status=500)

# Worker - dropdownlist
@api_view(['GET'])
def get_workers(request: Request) -> JsonResponse:
    """Get all workers"""
    try:
        workers = Worker.objects.all()
        serializer = WorkerSerializer(workers, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

#worker view logic
@api_view(['DELETE'])
def delete_worker(request: Request, worker_id: int) -> JsonResponse:
    try:
        worker = Worker.objects.get(id=worker_id)
        worker.delete()
        return JsonResponse({'success': True, 'message': 'Worker deleted'})
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
"""
@api_view(['DELETE'])
def delete_process(request: Request, process_id: int) -> JsonResponse:
    try:
        process = Process.objects.get(id=process_id)
        process.delete()
        return JsonResponse({'success': True, 'message': 'Process deleted'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

"""
# Worker

"""@api_view(['GET'])
def get_workers(request: Request) -> JsonResponse:
    ""Get all workers""
    try:
        workers = Worker.objects.all()
        serializer = WorkerSerializer(workers, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['DELETE'])
def delete_worker(request: Request, worker_id: int) -> JsonResponse:
    try:
        worker = Worker.objects.get(id=worker_id)
        worker.delete()
        return JsonResponse({'success': True, 'message': 'Worker deleted'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
def create_worker(request: Request) -> JsonResponse:
    ""Create a new worker""
    try:
        serializer = WorkerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
"""