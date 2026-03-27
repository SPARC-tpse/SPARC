from rest_framework import serializers

from ..models import Order
from .order_file_serializer import OrderFileSerializer


class OrderSerializer(serializers.ModelSerializer):
    order_files = OrderFileSerializer(many=True, read_only=True)
    bom_files = serializers.SerializerMethodField()
    general_files = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "name",
            "order_number",
            "target_amount",
            "order_files",  # All files attached to this order
            "start_date",
            "end_date",
            "product_name",
            "priority",
            "status",
            "comments",
            "bom_files",
            "general_files",
        ]

    def get_bom_files(self, obj):
        """Get only BOM files"""
        bom_files = obj.order_files.filter(file_type="bom")
        return OrderFileSerializer(bom_files, many=True, context=self.context).data

    def get_general_files(self, obj):
        """Get only general files"""
        general_files = obj.order_files.filter(file_type="general")
        return OrderFileSerializer(general_files, many=True, context=self.context).data
