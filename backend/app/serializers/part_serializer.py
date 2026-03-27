from rest_framework import serializers

from app.models import Part

from .process_serializer import ProcessSerializer


class PartSerializer(serializers.ModelSerializer):
    process = ProcessSerializer(many=False)

    class Meta:
        model = Part
        fields = ["process", "process_time"]
