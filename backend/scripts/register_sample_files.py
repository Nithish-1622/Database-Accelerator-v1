import os
from pathlib import Path
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE','database_accelerator.settings')
# Ensure repository root is on sys.path so Django project can be imported
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import django
django.setup()

from database_accelerator.apps.upload_module.models import dataset_manager

SAMPLE_DIR = ROOT / 'sample'

registered = []
for file_path in SAMPLE_DIR.glob('*.csv'):
    dataset_id = str(uuid.uuid4())
    size = file_path.stat().st_size
    # naive columns/rows count
    import csv
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        cols = len(rows[0]) if rows else 0
        row_count = len(rows) - 1 if len(rows) > 0 else 0

    metadata = dataset_manager.create(
        dataset_id=dataset_id,
        filename=file_path.name,
        file_path=str(file_path),
        file_type='csv',
        file_size=size,
        rows=row_count,
        columns=cols,
        column_names=[c for c in rows[0]] if rows else [],
        column_types={},
    )
    registered.append((dataset_id, file_path.name))

print('Registered sample datasets:')
for did, name in registered:
    print(did, name)
