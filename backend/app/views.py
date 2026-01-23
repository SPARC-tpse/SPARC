from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.request import Request
from .models import Order
from .serializers import OrderSerializer
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError

@api_view(['GET'])
def get_orders(request: Request) -> JsonResponse:
    try:
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return JsonResponse(serializer.data)
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
            priority = 0

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
        new_entry.save()
        new_entry.process.set([])
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
        # Update logic here
        # order.field = request.data.get('field')
        order.save()
        return JsonResponse({'message': 'Order updated successfully'})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

@api_view(['DELETE'])
def delete_order(request: Request, order_id: int) -> JsonResponse:
    try:
        order = Order.objects.get(id=order_id)
        order.delete()
        return JsonResponse({'message': 'Order deleted successfully'})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
