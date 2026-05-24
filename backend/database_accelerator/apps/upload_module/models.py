import json
import os
import uuid
from datetime import datetime


class DatasetManager:
    """
    Filesystem-based dataset manager (replaces Django ORM)
    Stores dataset metadata as JSON files
    """

    def __init__(self):
        from django.conf import settings
        self.upload_raw_dir = settings.UPLOAD_RAW_DIR
        self.upload_processed_dir = settings.UPLOAD_PROCESSED_DIR
        self.upload_failed_dir = settings.UPLOAD_FAILED_DIR
        self.metadata_suffix = '.metadata.json'

    def create(self, dataset_id, filename, file_path, file_type, file_size, rows, columns, column_names, column_types):
        """Create a new dataset entry"""
        dataset_id = dataset_id or str(uuid.uuid4())
        
        metadata = {
            'id': dataset_id,
            'filename': filename,
            'file_path': file_path,
            'file_type': file_type,
            'file_size': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'rows': rows,
            'columns': columns,
            'column_names': column_names,
            'column_types': column_types,
            'status': 'ready',
            'error_message': None,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }

        # Save metadata file
        metadata_file = os.path.join(self.upload_raw_dir, f"{dataset_id}{self.metadata_suffix}")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        return metadata

    def get(self, dataset_id):
        """Retrieve dataset metadata by ID"""
        metadata_file = os.path.join(self.upload_raw_dir, f"{dataset_id}{self.metadata_suffix}")
        
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                return json.load(f)
        return None

    def list_all(self):
        """List all datasets"""
        datasets = []
        
        if os.path.exists(self.upload_raw_dir):
            for file in os.listdir(self.upload_raw_dir):
                if file.endswith(self.metadata_suffix):
                    filepath = os.path.join(self.upload_raw_dir, file)
                    with open(filepath, 'r') as f:
                        datasets.append(json.load(f))
        
        # Sort by creation date (newest first)
        datasets.sort(key=lambda x: x['created_at'], reverse=True)
        return datasets

    def update_status(self, dataset_id, status, error_message=None):
        """Update dataset status"""
        metadata_file = os.path.join(self.upload_raw_dir, f"{dataset_id}{self.metadata_suffix}")
        
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            metadata['status'] = status
            metadata['error_message'] = error_message
            metadata['updated_at'] = datetime.now().isoformat()
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return metadata
        return None

    def delete(self, dataset_id):
        """Delete dataset"""
        metadata_file = os.path.join(self.upload_raw_dir, f"{dataset_id}{self.metadata_suffix}")
        data_file = os.path.join(self.upload_raw_dir, dataset_id)
        
        try:
            if os.path.exists(metadata_file):
                os.remove(metadata_file)
            if os.path.exists(data_file):
                os.remove(data_file)
            return True
        except Exception:
            return False


# Global dataset manager instance
dataset_manager = DatasetManager()

