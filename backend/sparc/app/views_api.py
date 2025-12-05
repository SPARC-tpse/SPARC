from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Resource, DisruptionType
from .serializers import ResourceSerializer, DisruptionTypeSerializer


@api_view(["GET"])
def get_resources(request):
    resources = Resource.objects.all().order_by("name")
    serializer = ResourceSerializer(resources, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_disruption_types(request):
    types = DisruptionType.objects.all().order_by("name")
    serializer = DisruptionTypeSerializer(types, many=True)
    return Response(serializer.data)
