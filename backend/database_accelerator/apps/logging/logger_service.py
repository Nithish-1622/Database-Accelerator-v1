import json
import os
from datetime import datetime

from django.conf import settings


class PipelineLogger:
    def __init__(self):
        self.log_root = getattr(settings, 'LOG_ROOT', os.path.join(settings.BASE_DIR, 'logs'))
        self.pipeline_dir = os.path.join(self.log_root, 'pipeline_logs')
        self.stage_dir = os.path.join(self.log_root, 'stage_logs')
        self.benchmark_dir = os.path.join(self.log_root, 'benchmark_logs')
        for directory in [self.pipeline_dir, self.stage_dir, self.benchmark_dir]:
            os.makedirs(directory, exist_ok=True)

    def _append(self, directory, dataset_id, payload):
        path = os.path.join(directory, f'{dataset_id}.jsonl')
        record = dict(payload)
        record['timestamp'] = datetime.now().isoformat()
        with open(path, 'a', encoding='utf-8') as handle:
            handle.write(json.dumps(record) + '\n')
        return path

    def log_stage_start(self, dataset_id, stage_name, details=None):
        return self._append(self.stage_dir, dataset_id, {'stage': stage_name, 'event': 'start', 'details': details or {}})

    def log_stage_end(self, dataset_id, stage_name, duration, details=None):
        return self._append(self.stage_dir, dataset_id, {'stage': stage_name, 'event': 'end', 'duration': round(float(duration), 4), 'details': details or {}})

    def log_stage_error(self, dataset_id, stage_name, error):
        return self._append(self.stage_dir, dataset_id, {'stage': stage_name, 'event': 'error', 'error': str(error)})

    def log_pipeline_event(self, dataset_id, event_name, payload=None):
        return self._append(self.pipeline_dir, dataset_id, {'event': event_name, 'payload': payload or {}})

    def log_benchmark_event(self, dataset_id, payload=None):
        return self._append(self.benchmark_dir, dataset_id, payload or {})


logger_service = PipelineLogger()
