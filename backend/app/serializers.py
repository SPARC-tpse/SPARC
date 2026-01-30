from rest_framework import serializers
from .models import Order, Process, Resource, DisruptionType, Disruption


class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ["id", "start_time", "end_time"]


class OrderSerializer(serializers.ModelSerializer):
    process = ProcessSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "start_date", "end_date", "name",
                  "product_name", "priority", "status", "process"]


class ResourceSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='type.name', read_only=True)

    class Meta:
        model = Resource
        fields = ["id", "name", "type", "type_name", "status"]
        read_only_fields = ["id"]


class DisruptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisruptionType
        fields = ["id", "name"]

class ResourceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisruptionType
        fields = ["id", "name"]

class DisruptionSerializer(serializers.ModelSerializer):
    start = serializers.DateTimeField(source='start_date')
    end = serializers.DateTimeField(source='end_date')
    resource_name = serializers.CharField(source='resource.name', read_only=True)
    type_name = serializers.CharField(source='type.name', read_only=True)

    class Meta:
        model = Disruption
        fields = ["id", "name", "start", "end", "resource", "type", "resource_name", "type_name"]
        read_only_fields = ["id"]
