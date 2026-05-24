import uuid
from datetime import datetime

from database_accelerator.apps.storage import metadata_store


class DatasetManager:
    """Dataset registry backed by the metadata abstraction."""

    def create(self, dataset_id, filename, file_path, file_type, file_size, rows, columns, column_names, column_types):
        dataset_id = dataset_id or str(uuid.uuid4())
        metadata = {
            'id': dataset_id,
            'dataset_id': dataset_id,
            'filename': filename,
            'dataset_name': filename,
            'file_path': file_path,
            'upload_path': file_path,
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
            'created_time': datetime.now().isoformat(),
            'processing_time': None,
            'artifact_paths': {},
            'benchmark_status': 'pending',
        }
        return metadata_store.create(metadata)

    def get(self, dataset_id):
        return metadata_store.get(dataset_id)

    def list_all(self):
        return metadata_store.list_all()

    def update_status(self, dataset_id, status, error_message=None):
        return metadata_store.update_status(dataset_id, status, error_message)

    def delete(self, dataset_id):
        return metadata_store.delete(dataset_id)


dataset_manager = DatasetManager()
