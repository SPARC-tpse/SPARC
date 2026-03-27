from rest_framework import serializers

from app.models import Process

from .order_serializer import OrderSerializer
from .resource_serializer import ResourceSerializer
from .worker_serializer import WorkerSerializer


class ProcessSerializer(serializers.ModelSerializer):
    workers = WorkerSerializer(many=True)
    resource = ResourceSerializer(many=False)
    order = OrderSerializer(many=False)

    class Meta:
        model = Process
        fields = [
            "id",
            "name",
            "approximated_time",
            "setup_time",
            "waiting_time",
            "workers",
            "resource",
            "order",
        ]
