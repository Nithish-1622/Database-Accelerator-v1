import os,json
os.environ.setdefault('DJANGO_SETTINGS_MODULE','database_accelerator.settings')
import django
django.setup()
from database_accelerator.apps.upload_module.models import dataset_manager
from database_accelerator.apps.storage import metadata_store

with open('benchmark_results.json','r',encoding='utf-8') as f:
    j=json.load(f)
first=j['results'][0]
did=first['dataset_id']
meta=dataset_manager.get(did)
print('before fields:', 'file_type' in meta, meta.get('file_type'))
meta['file_type']='csv'
metadata_store.create(meta)
meta2=dataset_manager.get(did)
print('after fields:', 'file_type' in meta2, meta2.get('file_type'))
