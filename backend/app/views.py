from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.request import Request
from .models import Order
from .serializers import OrderSerializer

@api_view(['GET'])
def get_orders(request: Request) -> JsonResponse:
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return JsonResponse(serializer.data)


@api_view(['POST'])
def create_order(request: Request) -> JsonResponse:
    pass


@api_view(['PUT'])
def update_order(request: Request) -> JsonResponse:
    pass


@api_view(['DELETE'])
def delete_order(request: Request) -> JsonResponse:
    pass
