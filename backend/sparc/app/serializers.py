from rest_framework import serializers
from sparc.app.models import Order, Process, Resource, DisruptionType, Disruption
from .services import Database


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
    resource_type_name = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = ['id', 'name', 'type', 'status', 'resource_type_name']

    def get_resource_type_name(self, obj: Resource) -> str:
        return Database.get_resource_type_name_by_id(obj.type_id)


class DisruptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisruptionType
        fields = ['id', 'name']


class DisruptionSerialzier(serializers.ModelSerializer):
    resource_name = serializers.SerializerMethodField()
    disruption_type_name = serializers.SerializerMethodField()

    class Meta:
        model = Disruption
        fields = ('id', 'name', 'start_date', 'end_date', 'resource', 'resource_name', 'type', 'disruption_type_name','comment')

    def get_resource_name_by_id(self, obj: Disruption) -> str:
        return Database.get_resource_name_by_id(obj.resource_id)

    def get_disruption_type_name_by_id(self, obj: Disruption) -> str:
        return Database.get_disruption_type_name_by_id(obj.type_id)