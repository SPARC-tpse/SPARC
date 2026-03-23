from rest_framework import serializers

from app.models import Resource


class ResourceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["id", "name"]
