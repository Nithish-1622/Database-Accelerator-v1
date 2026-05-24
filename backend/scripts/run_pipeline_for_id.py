import os
from pathlib import Path
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE','database_accelerator.settings')
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import django
django.setup()

from database_accelerator.apps.engines.pipeline_manager import run_pipeline

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: run_pipeline_for_id.py <dataset_id>')
        raise SystemExit(1)
    dataset_id = sys.argv[1]
    print('Running pipeline for', dataset_id)
    res = run_pipeline(dataset_id)
    print('Done. Result keys:', list(res.keys()))
    if 'stage_timings' in res:
        print('Stage timings:', res['stage_timings'])