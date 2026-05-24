from rest_framework import serializers


class IntelligenceReportSerializer(serializers.Serializer):
    dataset_id = serializers.CharField()
    filename = serializers.CharField()
    source = serializers.CharField()
    rows = serializers.IntegerField()
    columns = serializers.IntegerField()
    numeric_columns = serializers.ListField(child=serializers.CharField())
    categorical_columns = serializers.ListField(child=serializers.CharField())
    datetime_columns = serializers.ListField(child=serializers.CharField())
    strong_correlations = serializers.ListField()
    high_cardinality_columns = serializers.ListField()
    frequent_values = serializers.DictField()
    duplicate_rows = serializers.IntegerField()
    distinct_rows = serializers.IntegerField()
    pattern_summary = serializers.DictField()