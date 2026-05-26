from rest_framework import serializers

from .models import AudioUpload, TranscriptModel, KeywordModel, FrequencyModel, ClusterModel, ClusterMember
from .utils.validators import validate_audio_file


class AudioUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioUpload
        fields = [
            'id',
            'filename',
            'file_path',
            'file_size',
            'duration',
            'status',
            'processing_stage',
            'created_at',
            'updated_at',
            'error_message',
        ]
        read_only_fields = fields


class AudioUploadCreateSerializer(serializers.Serializer):
    audio_file = serializers.FileField()

    def validate_audio_file(self, value):
        validation = validate_audio_file(value)
        if not validation['valid']:
            raise serializers.ValidationError(validation['message'])
        return value


class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranscriptModel
        fields = ['id', 'audio', 'transcript', 'model_name', 'language', 'created_at']
        read_only_fields = fields


class TranscriptRequestSerializer(serializers.Serializer):
    audio_id = serializers.UUIDField()
    transcript_override = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    model_name = serializers.CharField(required=False, allow_blank=True, default='whisper-small')


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeywordModel
        fields = ['id', 'audio', 'keyword', 'frequency', 'timestamps', 'created_at']
        read_only_fields = fields


class FrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = FrequencyModel
        fields = ['id', 'audio', 'keyword', 'count', 'created_at']
        read_only_fields = fields


class ClusterMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClusterMember
        fields = ['id', 'cluster', 'keyword', 'keyword_text', 'weight']


class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClusterModel
        fields = ['id', 'audio', 'algorithm', 'parameters', 'created_at']
        read_only_fields = fields
