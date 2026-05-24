from rest_framework import serializers
from .parser import parse_file
from .validators import validate_file
from .models import dataset_manager
import os
from django.conf import settings


class DatasetSerializer(serializers.Serializer):
    """Serializer for dataset metadata (filesystem-based)"""
    id = serializers.CharField(read_only=True)
    filename = serializers.CharField(read_only=True)
    file_type = serializers.CharField(read_only=True)
    file_size = serializers.IntegerField(read_only=True)
    file_size_mb = serializers.FloatField(read_only=True)
    rows = serializers.IntegerField(read_only=True)
    columns = serializers.IntegerField(read_only=True)
    column_names = serializers.ListField(read_only=True)
    column_types = serializers.DictField(read_only=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    error_message = serializers.CharField(required=False, allow_blank=True)


class DatasetUploadSerializer(serializers.Serializer):
    """Serializer for file upload"""
    file = serializers.FileField()

    def validate_file(self, value):
        # Validate file type and size
        validation_result = validate_file(value)
        if not validation_result['valid']:
            raise serializers.ValidationError(validation_result['message'])
        return value

    def create(self, validated_data):
        file = validated_data['file']
        
        # Parse file to get metadata
        parse_result = parse_file(file)
        
        if not parse_result['success']:
            return {
                'success': False,
                'message': parse_result['message']
            }

        # Save file to uploads/raw directory
        dataset_id = parse_result['dataset_id']
        file_path = os.path.join(settings.UPLOAD_RAW_DIR, f"{dataset_id}_{file.name}")
        
        # Write file to disk
        try:
            with open(file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to save file: {str(e)}'
            }

        # Create metadata in filesystem
        metadata = dataset_manager.create(
            dataset_id=dataset_id,
            filename=file.name,
            file_path=file_path,
            file_type=parse_result['file_type'],
            file_size=file.size,
            rows=parse_result['rows'],
            columns=parse_result['columns'],
            column_names=parse_result['column_names'],
            column_types=parse_result['column_types']
        )

        return {
            'success': True,
            'dataset': metadata
        }

