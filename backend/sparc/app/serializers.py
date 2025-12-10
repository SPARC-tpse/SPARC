from rest_framework import serializers
from sparc.app.models import Order, Process, Resource, DisruptionType, Disruption

class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ["id", "start_time", "end_time"]

class OrderSerializer(serializers.ModelSerializer):
    process = ProcessSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "name", "process"]

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'name', 'type', 'status']

class DisruptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisruptionType
        fields = ['id', 'name']

class DisruptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disruption
        fields = "__all__"
