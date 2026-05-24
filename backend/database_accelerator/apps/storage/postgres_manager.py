from .postgres_adapter import PostgresAdapter


class PostgresManager:
    def __init__(self):
        self.adapter = PostgresAdapter()

    def create(self, metadata):
        return self.adapter.upsert(metadata)

    def get(self, dataset_id):
        return self.adapter.get(dataset_id)

    def list_all(self):
        return self.adapter.list_all()

    def update_status(self, dataset_id, status, error_message=None):
        return self.adapter.update_status(dataset_id, status, error_message)

    def delete(self, dataset_id):
        return self.adapter.delete(dataset_id)
