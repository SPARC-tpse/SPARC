from typing import Any, cast

from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request

from ..models import Disruption, DisruptionType
from ..serializers.disruption_serializer import DisruptionSerializer
from . import broadcast_db_change


def format_dt(dt):
    """Converts a datetime object to a string in ISO 8601 format"""
    if not dt:
        return None

    return dt.strftime('%Y-%m-%dT%H:%M:%S')


@api_view(['GET'])
def get_disruptions(request: Request) -> JsonResponse:
    """Returns a list of all disruptions"""
    try:
        disruptions = Disruption.objects.all()
        serializer = DisruptionSerializer(disruptions, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
def get_disruption(request: Request, disruption_id: int) -> JsonResponse:
    """Returns a single disruption by its ID"""
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
    """Returns a list of all disruption types"""
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
    """Creates a new disruption"""
    try:
        serializer = DisruptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            broadcast_db_change('disruption', 'created', cast(dict[str, Any], serializer.data))
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['PUT'])
def update_disruption(request: Request, disruption_id: int) -> JsonResponse:
    """Updates an existing disruption by its ID"""
    try:
        disruption = Disruption.objects.get(id=disruption_id)
    except Disruption.DoesNotExist:
        return JsonResponse({'error': 'Disruption not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = DisruptionSerializer(disruption, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return JsonResponse({'message': 'Updated', 'data': serializer.data})

    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_disruption(request: Request, disruption_id: int) -> JsonResponse:
    """Deletes a disruption by its ID"""
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
