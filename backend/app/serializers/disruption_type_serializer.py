from rest_framework import serializers

from app.models import DisruptionType


class DisruptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisruptionType
        fields = ["id", "name"]
