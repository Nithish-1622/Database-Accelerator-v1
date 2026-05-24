from rest_framework import serializers


class AcceleratorPipelineSerializer(serializers.Serializer):
    dataset_id = serializers.CharField()
    input_file = serializers.CharField()
    schema_detection = serializers.DictField()
    column_classification = serializers.DictField()
    pattern_discovery = serializers.DictField()
    quality_before = serializers.DictField()
    quality_after = serializers.DictField()
    feature_importance = serializers.DictField()
    removed_columns_count = serializers.IntegerField()
    artifacts = serializers.DictField()