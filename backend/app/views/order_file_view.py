from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser

from ..models import Order, OrderFile
from ..serializers.order_file_serializer import OrderFileSerializer


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_order_file(request):
    """Upload an order file"""
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
    """Deletes an order file by its ID"""
    try:
        order_file = OrderFile.objects.get(id=file_id)
        if order_file.file:
            order_file.file.delete(save=False)
        order_file.delete()
        return JsonResponse({'success': True, 'message': 'File deleted'})
    except OrderFile.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def list_order_files(request, order_id):
    """Lists all order files for a given order ID"""
    try:
        files = OrderFile.objects.get(order__id=order_id)
        serializer = OrderFileSerializer(files, many=True, context={'request': request})
        return JsonResponse({'order_id': order_id, 'files': serializer.data})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
