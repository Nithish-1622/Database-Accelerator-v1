from rest_framework import serializers


class PreprocessingRequestSerializer(serializers.Serializer):
    dataset_id = serializers.CharField()


class PreprocessingReportSerializer(serializers.Serializer):
    dataset_id = serializers.CharField()
    filename = serializers.CharField()
    file_type = serializers.CharField()
    original_rows = serializers.IntegerField()
    cleaned_rows = serializers.IntegerField()
    original_missing_cells = serializers.IntegerField()
    cleaned_missing_cells = serializers.IntegerField()
    duplicates_removed = serializers.IntegerField()
    cleaned_file_path = serializers.CharField()
    columns_processed = serializers.ListField(child=serializers.CharField())