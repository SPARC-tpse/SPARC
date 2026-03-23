from rest_framework import serializers

from ..models import OrderFile


class OrderFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = OrderFile
        fields = [
            "id",
            "file",  # Relative path (e.g., "1/bom/file.pdf")
            "file_url",  # Full URL (e.g., "http://localhost:8000/media/1/bom/file.pdf")
            "file_name",  # Just filename (e.g., "file.pdf")
            "file_size",  # Size in bytes
            "file_type",  # 'bom' or 'general'
            "uploaded_at",
        ]

    def get_file_url(self, obj):
        """Return full URL to access the file"""
        request = self.context.get("request")
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
            except Exception as _:
                return None
        return None
