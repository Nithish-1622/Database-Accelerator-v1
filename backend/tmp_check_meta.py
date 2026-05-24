import os, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'database_accelerator.settings')
import django
django.setup()
from database_accelerator.apps.upload_module.models import dataset_manager
from database_accelerator.apps.engines.shared import build_artifact_paths

with open('benchmark_results.json','r',encoding='utf-8') as f:
    payload = json.load(f)
first = payload['results'][0]
did = first['dataset_id']
print('checking dataset id', did)
meta = dataset_manager.get(did)
print('metadata:', {k: meta.get(k) for k in ['id','filename','file_path','rows','columns','status']})
art = build_artifact_paths(did)
print('artifact dir:', art.artifact_dir)
print('artifact dir exists:', os.path.isdir(art.artifact_dir))
print('example artifact sizes:')
for name in ['clean_dataset_csv','quality_report_pdf','recommended_model_input_csv']:
    path = getattr(art, name)
    print(name, os.path.exists(path), os.path.getsize(path) if os.path.exists(path) else None)
