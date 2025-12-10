from rest_framework import generics
from .models import Order, Resource, DisruptionType
from .serializers import OrderSerializer
from django.http import JsonResponse


def get_resources(request):
    data = list(Resource.objects.values("id", "name"))
    return JsonResponse(data, safe=False)

def get_disruption_types(request):
    data = list(DisruptionType.objects.values("id", "name"))
    return JsonResponse(data, safe=False)

