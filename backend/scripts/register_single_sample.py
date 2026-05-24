import os
from pathlib import Path
import sys
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE','database_accelerator.settings')
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import django
django.setup()

from database_accelerator.apps.upload_module.models import dataset_manager

FILE = ROOT.parent / 'sample' / 'extreme_missing.csv'
if not FILE.exists():
    print('file not found', FILE)
    raise SystemExit(1)

dataset_id = str(uuid.uuid4())
size = FILE.stat().st_size
import csv
with open(FILE, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)
    cols = len(rows[0]) if rows else 0
    row_count = len(rows) - 1 if len(rows) > 0 else 0

metadata = dataset_manager.create(
    dataset_id=dataset_id,
    filename=FILE.name,
    file_path=str(FILE),
    file_type='csv',
    file_size=size,
    rows=row_count,
    columns=cols,
    column_names=[c for c in rows[0]] if rows else [],
    column_types={},
)

print('REGISTERED', metadata.get('dataset_id', dataset_id))
