from django.conf import settings

from .postgres_manager import PostgresManager


class MetadataStore:
    def __init__(self):
        self.postgres = PostgresManager()
        self.backend = getattr(settings, 'METADATA_BACKEND', 'postgres')

    def create(self, metadata):
        return self.postgres.create(metadata)

    def get(self, dataset_id):
        return self.postgres.get(dataset_id)

    def list_all(self):
        return self.postgres.list_all()

    def update_status(self, dataset_id, status, error_message=None):
        return self.postgres.update_status(dataset_id, status, error_message)

    def delete(self, dataset_id):
        return self.postgres.delete(dataset_id)


metadata_store = MetadataStore()
