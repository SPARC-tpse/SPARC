from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.request import Request
from .models import Order, Disruption, DisruptionType, Resource
from .serializers import OrderSerializer, DisruptionSerializer, ResourceSerializer, DisruptionTypeSerializer
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.dateparse import parse_datetime


#----------------------Disruptions----------------------
@api_view(['GET'])
def get_disruptions(request: Request) -> JsonResponse:
    try:
        disruptions = Disruption.objects.all()
        serializer = DisruptionSerializer(disruptions, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        return JsonResponse({'error': 'Failed to retrieve disruptions'}, status=500)




@api_view(['POST'])
def create_disruption(request: Request) -> JsonResponse:
    serializer = DisruptionSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            new_entry = serializer.save() 
            return JsonResponse({
                'id': new_entry.id, 
                'message': 'Disruption created successfully'
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': f'Database-error: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': serializer.errors}, status=400)

@api_view(['PUT'])
def update_disruption(request: Request, disruption_id: str) -> JsonResponse:
    try:
        disruption = Disruption.objects.get(id=disruption_id)
        data = request.data
        
        disruption.name = data.get('name', disruption.name)
        disruption.start_date = data.get('start', disruption.start_date)
        disruption.end_date = data.get('end', disruption.end_date)
        
        if 'resource' in data:
            disruption.resource_id = data['resource']
        if 'type' in data:
            disruption.type_id = data['type']
            
        disruption.save()
        return JsonResponse({'message': 'Disruption updated successfully'})
    except Disruption.DoesNotExist:
        return JsonResponse({'error': 'Disruption not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(['DELETE'])
def delete_disruption(request: Request, disruption_id: int) -> JsonResponse:
    try:
        disruption = Disruption.objects.get(id=disruption_id)
        disruption.delete()
        return JsonResponse({'message': 'Disruption deleted successfully'})
    except Disruption.DoesNotExist:
        return JsonResponse({'error': 'Disruption not found'}, status=404)





#--------------------------Orders--------------------------------
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
    
#--------------------Resources------------------------------
@api_view(['GET'])
def get_resources(request: Request) -> JsonResponse:
    try:
        resources = Resource.objects.all()
        serializer = ResourceSerializer(resources, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

#-------------DisruptionTypes----------------(DisruptionTypes written like that to avoid ambiguity with disruption.type which would be called disruption_type)
@api_view(['GET'])
def get_disruptionTypes(request: Request) -> JsonResponse:
    try:
        types = DisruptionType.objects.all()
        serializer = DisruptionTypeSerializer(types, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
