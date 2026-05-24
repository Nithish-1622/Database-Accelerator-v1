from rest_framework import serializers


class ExportReportSerializer(serializers.Serializer):
    dataset_id = serializers.CharField()
    filename = serializers.CharField()
    export_filename = serializers.CharField()
    export_path = serializers.CharField()
    exported_at = serializers.CharField()
    source_cleaned_file = serializers.CharField()