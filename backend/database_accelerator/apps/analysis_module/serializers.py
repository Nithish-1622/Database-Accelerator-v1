from rest_framework import serializers


class AnalysisRequestSerializer(serializers.Serializer):
    dataset_id = serializers.CharField()


class AnalysisReportSerializer(serializers.Serializer):
    dataset_id = serializers.CharField()
    filename = serializers.CharField()
    file_type = serializers.CharField()
    rows = serializers.IntegerField()
    columns = serializers.IntegerField()
    missing_cells = serializers.IntegerField()
    missing_values_by_column = serializers.DictField()
    duplicate_rows = serializers.IntegerField()
    completeness_score = serializers.FloatField()
    duplicate_rate = serializers.FloatField()
    analyzed_at = serializers.CharField()
    column_names = serializers.ListField(child=serializers.CharField())