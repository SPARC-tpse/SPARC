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
        if request.data['priority'] == "Low":
            priority = 1
        elif request.data['priority'] == "Medium":
            priority = 2
        elif request.data['priority'] == "High":
            priority = 3
        else:
            priority = 1

        if request.data['status'] == "Planned":
            status = 1
        elif request.data['status'] == "Running":
            status = 2
        elif request.data['status'] == "Paused":
            status = 3
        elif request.data['status'] == "Done":
            status = 4
        else:
            status = 1

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
            workers = Worker.objects.filter(name=process['worker'])
            resource = Resource.objects.filter(name=process['resource']).first()
            if not workers:
                return JsonResponse({'error': f'No worker exists with name: {process['worker']}'}, status=400)
            elif not resource:
                return JsonResponse({'error': f'No resource exists with name: {process['resource']}'}, status=400)
            new_process = Process.objects.create(
                name=process['name'],
                resource=resource
            )
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
        return JsonResponse({'error': 'Database integrity error (e.g., duplicate entry)'}, status=400)
    except KeyError as e:
        return JsonResponse({'error': f'Missing field: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Failed to create order'}, status=500)

@api_view(['PUT'])
def update_order(request: Request, order_id: int) -> JsonResponse:
    try:
        order = Order.objects.get(id=order_id)
        order.name = request.data.get('name')
        order.target_amount = int(request.data.get('target_amount'))
        # order.bill_of_materials = request.data.get('bill_of_materials')
        # order.files = request.data.get('files')
        order.start_date = str(request.data.get('start_date'))
        order.end_date = str(request.data.get('end_date'))
        order.product_name = request.data.get('product_name')
        order.priority = request.data.get('priority')
        order.status = request.data.get('status')
        order.comments = request.data.get('comments')
        order.process.set(request.data.get('process'))
        order.save()

        # Broadcast the change
        serializer = OrderSerializer(order)
        broadcast_order_change('updated', serializer.data)

        return JsonResponse({'message': 'Order updated successfully'})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

@api_view(['DELETE'])
def delete_order(request: Request, order_id: int) -> JsonResponse:
    print("start deleting")
    try:
        order = Order.objects.filter(id=order_id)
        order.delete()

        # Broadcast the change
        broadcast_order_change('deleted', {'id': order_id})

        return JsonResponse({'message': 'Order deleted successfully'})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

# Order / Files

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_order_file(request):
    """Upload a file for an order"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)

        file = request.FILES['file']
        file_type = request.POST.get('type', 'general')
        order_id = request.POST.get('order_id')

        if not order_id:
            return JsonResponse({'error': 'order_id is required'}, status=400)

        # Get the order
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)

        # Create OrderFile instance
        order_file = OrderFile(
            order=order,
            file=file,
            file_type=file_type,
        )
        order_file.save()

        # Serialize and return
        serializer = OrderFileSerializer(order_file, context={'request': request})

        return JsonResponse(serializer.data, status=201)

    except Exception as e:
        print(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['DELETE'])
def delete_order_file(request, file_id):
    """Delete an uploaded file"""
    try:
        order_file = OrderFile.objects.get(id=file_id)

        # Delete the actual file from disk
        if order_file.file:
            order_file.file.delete(save=False)

        # Delete the database record
        order_file.delete()

        return JsonResponse({'success': True, 'message': 'File deleted'})

    except OrderFile.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)
    except Exception as e:
        print(f"Delete error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def list_order_files(request, order_id):
    """List all files for a specific order"""
    try:
        order = Order.objects.get(id=order_id)
        files = order.order_files.all()

        serializer = OrderFileSerializer(files, many=True, context={'request': request})

        return JsonResponse({
            'order_id': order_id,
            'files': serializer.data
        })

    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        print(f"List files error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# Process

@api_view(['PUT'])
def update_process_timing(request: Request, process_id: int) -> JsonResponse:
    """Update timing for a specific process step"""
    try:
        process = Process.objects.get(id=process_id)

        # Update timing fields if provided
        if 'setup_time_seconds' in request.data:
            process.setup_time_seconds = int(request.data['setup_time_seconds'])

        if 'waiting_time_seconds' in request.data:
            process.waiting_time_seconds = int(request.data['waiting_time_seconds'])

        if 'process_time_seconds' in request.data:
            process.process_time_seconds = int(request.data['process_time_seconds'])

        process.save()

        return JsonResponse({
            'message': 'Process timing updated successfully',
            'setup_time_seconds': process.setup_time_seconds,
            'waiting_time_seconds': process.waiting_time_seconds,
            'process_time_seconds': process.process_time_seconds
        })

    except Process.DoesNotExist:
        return JsonResponse({'error': 'Process not found'}, status=404)
    except Exception as e:
        print(f"Update process timing error: {e}")
        import traceback
        traceback.print_exc()
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