from rest_framework import serializers

from app.models import Disruption
from app.serializers.disruption_type_serializer import DisruptionTypeSerializer
from app.serializers.process_serializer import ProcessSerializer
from app.serializers.resource_serializer import ResourceSerializer


class DisruptionSerializer(serializers.ModelSerializer):
    type = DisruptionTypeSerializer(many=False)
    process = ProcessSerializer(many=False)
    resource = ResourceSerializer(many=False)

    class Meta:
        model = Disruption
        fields = [
            "id",
            "name",
            "type",
            "process",
            "resource",
            "created_at",
            "disruption_time",
        ]
