import json
from datetime import datetime

from django.db import connection


class PostgresAdapter:
    table_name = 'database_accelerator_metadata'

    def ensure_schema(self):
        with connection.cursor() as cursor:
            cursor.execute(
                f'''
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    dataset_id TEXT PRIMARY KEY,
                    dataset_name TEXT NOT NULL,
                    upload_path TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_time TEXT NOT NULL,
                    processing_time REAL,
                    artifact_paths TEXT,
                    benchmark_status TEXT,
                    metadata_json TEXT,
                    updated_time TEXT NOT NULL
                )
                '''
            )
            # If table already existed before adding metadata_json, ensure the column exists
            try:
                cursor.execute(f"ALTER TABLE {self.table_name} ADD COLUMN IF NOT EXISTS metadata_json TEXT")
            except Exception:
                # best-effort: ignore if unable to alter
                pass

    def upsert(self, metadata):
        self.ensure_schema()
        payload = dict(metadata)
        payload.setdefault('updated_at', datetime.now().isoformat())
        with connection.cursor() as cursor:
            cursor.execute(
                f'''
                INSERT INTO {self.table_name} (
                    dataset_id, dataset_name, upload_path, status, created_time,
                    processing_time, artifact_paths, benchmark_status, metadata_json, updated_time
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT(dataset_id) DO UPDATE SET
                    dataset_name=excluded.dataset_name,
                    upload_path=excluded.upload_path,
                    status=excluded.status,
                    created_time=excluded.created_time,
                    processing_time=excluded.processing_time,
                    artifact_paths=excluded.artifact_paths,
                    benchmark_status=excluded.benchmark_status,
                    metadata_json=excluded.metadata_json,
                    updated_time=excluded.updated_time
                ''',
                [
                    payload.get('id'),
                    payload.get('filename') or payload.get('dataset_name') or '',
                    payload.get('file_path') or payload.get('upload_path') or '',
                    payload.get('status') or 'ready',
                    payload.get('created_at') or payload.get('created_time') or payload.get('updated_at'),
                    payload.get('processing_time'),
                    json.dumps(payload.get('artifact_paths') or {}),
                    payload.get('benchmark_status') or 'pending',
                    json.dumps(payload or {}),
                    payload.get('updated_at') or payload.get('created_at') or datetime.now().isoformat(),
                ]
            )
        return payload

    def get(self, dataset_id):
        self.ensure_schema()
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT dataset_id, dataset_name, upload_path, status, created_time, processing_time, artifact_paths, benchmark_status, metadata_json, updated_time FROM {self.table_name} WHERE dataset_id = %s', [dataset_id])
            row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_metadata(row)

    def list_all(self):
        self.ensure_schema()
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT dataset_id, dataset_name, upload_path, status, created_time, processing_time, artifact_paths, benchmark_status, metadata_json, updated_time FROM {self.table_name} ORDER BY created_time DESC')
            rows = cursor.fetchall()
        return [self._row_to_metadata(row) for row in rows]

    def update_status(self, dataset_id, status, error_message=None):
        metadata = self.get(dataset_id)
        if not metadata:
            return None
        metadata['status'] = status
        metadata['error_message'] = error_message
        return self.upsert(metadata)

    def delete(self, dataset_id):
        self.ensure_schema()
        with connection.cursor() as cursor:
            cursor.execute(f'DELETE FROM {self.table_name} WHERE dataset_id = %s', [dataset_id])
        return True

    def _row_to_metadata(self, row):
        artifact_paths = row[6]
        try:
            artifact_paths = json.loads(artifact_paths) if artifact_paths else {}
        except Exception:
            artifact_paths = {}
        # base metadata from columns
        base = {
            'id': row[0],
            'dataset_id': row[0],
            'filename': row[1],
            'dataset_name': row[1],
            'file_path': row[2],
            'upload_path': row[2],
            'status': row[3],
            'created_at': row[4],
            'created_time': row[4],
            'processing_time': row[5],
            'artifact_paths': artifact_paths,
            'benchmark_status': row[7],
            'updated_at': row[9] if len(row) > 9 else row[8],
            'updated_time': row[9] if len(row) > 9 else row[8],
        }
        # merge optional metadata_json if present
        try:
            metadata_json = row[8] if len(row) > 8 else None
            if metadata_json:
                parsed = json.loads(metadata_json)
                # prefer explicit fields from parsed metadata
                base.update({k: v for k, v in parsed.items() if v is not None})
        except Exception:
            pass

        return base
