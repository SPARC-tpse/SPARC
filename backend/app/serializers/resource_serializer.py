from rest_framework import serializers

from app.models import Resource
from app.serializers.resource_type_serializer import ResourceTypeSerializer


class ResourceSerializer(serializers.ModelSerializer):
    type = ResourceTypeSerializer(many=False)

    class Meta:
        model = Resource
        fields = ["id", "name", "type", "status"]
