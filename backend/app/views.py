from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.request import Request
from .models import Order
from .serializers import OrderSerializer
from datetime import datetime

@api_view(['GET'])
def get_orders(request: Request) -> JsonResponse:
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return JsonResponse(serializer.data)


@api_view(['POST'])
def create_order(request: Request) -> JsonResponse:
    # print(request.data)

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


@api_view(['PUT'])
def update_order(request: Request) -> JsonResponse:
    pass


@api_view(['DELETE'])
def delete_order(request: Request) -> JsonResponse:
    pass
