import os
from pathlib import Path
os.environ.setdefault('DJANGO_SETTINGS_MODULE','database_accelerator.settings')
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import django
django.setup()
from database_accelerator.apps.storage import metadata_store

sample = {
    'id': 'test-sample-123',
    'filename': 'test.csv',
    'file_path': str(Path(__file__).resolve().parents[1] / 'sample' / 'small_clean.csv'),
    'file_type': 'csv',
    'file_size': 12345,
    'rows': 10,
    'columns': 3,
    'column_names': ['a','b','c'],
}
print('Creating metadata...')
res = metadata_store.create(sample)
print('Created:', res.get('id'))
print('Fetching back...')
print(metadata_store.get('test-sample-123'))
