from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.request import Request
from .models import Order, Process, Worker, Resource
from .serializers import OrderSerializer
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def broadcast_order_change(action, order_data=None):
    """Helper to broadcast order changes via WebSocket"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'orders_orders',
        {
            'type': 'order_message',
            'action': action,
            'data': order_data
        }
    )

@api_view(['GET'])
def get_order(request: Request, order_id: int) -> JsonResponse:
    try:
        order = Order.objects.filter(id=order_id)
        serializer = OrderSerializer(order, many=True)
        return JsonResponse(serializer.data[0], safe=True)
    except Exception as e:
        return JsonResponse({'error': 'Order not found'}, status=404)

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

        new_entry = Order(
            name = str(request.data['name']),
            target_amount = int(request.data['target']),
            bill_of_materials = None,
            files = None,
            start_date = str(request.data['start']),
            end_date = str(request.data['end']),
            product_name = str(request.data['product']),
            priority = priority,
            status = str(request.data['status']),
            comments = str(request.data['comments']),
        )
        process_steps = []
        for process in request.data['process']:

            workers = Worker.objects.filter(name=process['worker'])
            resource = Resource.objects.filter(name=process['resource'])
            print(workers)
            if not workers:
                return JsonResponse({'error': f'No worker exists with name: {process['worker']}'}, status=400)
            elif not resource:
                return JsonResponse({'error': f'No resource exists with name: {process['resource']}'}, status=400)

            process_steps.append(Process(
                start_time = None,
                end_time = None,
                work_time = None,
                setup_time = None,
                workers =  workers,
                name = process['notes'],
                resource = resource
            ))
        new_entry.save()
        new_entry.process.set(process_steps)

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
    print(request.data)
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
