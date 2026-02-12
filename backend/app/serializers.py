from rest_framework import serializers
from .models import Order, Process, Resource, DisruptionType, Worker, Disruption, OrderFile

class ResourceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = [
            "id",
            "name"
        ]


class ResourceSerializer(serializers.ModelSerializer):
    type = ResourceTypeSerializer(many = False)

    class Meta:
        model = Resource
        fields = [
            "id",
            "name",
            "type",
            "status"
        ]


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = [
            "id",
            "name"
        ]


class ProcessSerializer(serializers.ModelSerializer):
    workers = WorkerSerializer(many = True)
    resource = ResourceSerializer(many = False)

    class Meta:
        model = Process
        fields = [
            "id",
            "name",
            "setup_time_seconds",
            "waiting_time_seconds",
            "process_time_seconds",
            "workers",
            "resource"
        ]


class OrderFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = OrderFile
        fields = [
            'id',
            'file',         # Relative path (e.g., "1/bom/file.pdf")
            'file_url',     # Full URL (e.g., "http://localhost:8000/media/1/bom/file.pdf")
            'file_name',    # Just filename (e.g., "file.pdf")
            'file_size',    # Size in bytes
            'file_type',    # 'bom' or 'general'
            'uploaded_at',
        ]

    def get_file_url(self, obj):
        """Return full URL to access the file"""
        request = self.context.get('request')
        if obj.file:
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_file_name(self, obj):
        """Return just the filename (e.g., 'document.pdf')"""
        return obj.get_filename()

    def get_file_size(self, obj):
        """Return file size in bytes"""
        if obj.file:
            try:
                return obj.file.size
            except:
                return None
        return None


class OrderSerializer(serializers.ModelSerializer):
    processes = ProcessSerializer(many = True, read_only = True)
    order_files = OrderFileSerializer(many = True, read_only = True)
    bom_files = serializers.SerializerMethodField()
    general_files = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "name",
            "target_amount",
            "order_files",  # All files attached to this order
            "start_date",
            "end_date",
            "product_name",
            "priority",
            "status",
            "comments",
            "processes",
            "bom_files",
            "general_files"
        ]

    def get_bom_files(self, obj):
        """Get only BOM files"""
        bom_files = obj.order_files.filter(file_type='bom')
        return OrderFileSerializer(bom_files, many=True, context=self.context).data

    def get_general_files(self, obj):
        """Get only general files"""
        general_files = obj.order_files.filter(file_type='general')
        return OrderFileSerializer(general_files, many=True, context=self.context).data


class DisruptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisruptionType
        fields = [
            "id",
            "name"
        ]


class DisruptionSerializer(serializers.ModelSerializer):
    type = DisruptionTypeSerializer(many = False)
    process = ProcessSerializer(many = False)
    resource = ResourceSerializer(many = False)

    class Meta:
        model = Disruption
        fields = [
            "id",
            "name",
            "type",
            "process",
            "resource",
            "created_at",
            "duration"
        ]
