from rest_framework import serializers
from .models import Order, Process, Resource, DisruptionType

class ProcessSerializer(serializers.ModelSerializer):

    class Meta:
        model = Process
        fields = ["id", "name", "start_time", "end_time", "work_time", "setup_time", "workers", "resource"]

class OrderSerializer(serializers.ModelSerializer):
    #process = ProcessSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "start_date", "end_date", "name", "product_name", "priority", "status", "target_amount", "comments"]

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["id", "name"]   # only what Vue needs

class DisruptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisruptionType
        fields = ["id", "name"]
