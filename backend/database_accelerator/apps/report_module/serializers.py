from rest_framework import serializers


class CombinedReportSerializer(serializers.Serializer):
    dataset_id = serializers.CharField()
    analysis_report = serializers.DictField(allow_null=True)
    cleaning_report = serializers.DictField(allow_null=True)
    intelligence_report = serializers.DictField(allow_null=True)


class ReportListSerializer(serializers.Serializer):
    report_ids = serializers.ListField(child=serializers.CharField())