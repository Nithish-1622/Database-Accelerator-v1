import os, csv, json
from pathlib import Path
os.environ.setdefault('DJANGO_SETTINGS_MODULE','database_accelerator.settings')
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import django
django.setup()
from database_accelerator.apps.upload_module.models import dataset_manager
from database_accelerator.apps.engines.shared import build_artifact_paths
import pandas as pd

# find dataset by filename
target = 'extreme_missing.csv'
all_ds = dataset_manager.list_all()
match = None
for d in all_ds:
    if d.get('filename') == target:
        match = d
        break
if not match:
    print('Dataset not found in metadata store')
    raise SystemExit(0)

print('Found dataset id:', match['id'])
print('Status:', match.get('status'))
print('File path:', match.get('file_path'))

art = build_artifact_paths(match['id'])
clean_path = art.clean_dataset_csv
orig_path = match.get('file_path')

print('\nOriginal size:', os.path.getsize(orig_path) if orig_path and os.path.exists(orig_path) else 'missing')
print('Clean size   :', os.path.getsize(clean_path) if os.path.exists(clean_path) else 'missing')

# show first 6 rows of each
print('\n--- Original (first 5 rows) ---')
with open(orig_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        print(line.strip())
        if i>=4: break

print('\n--- Cleaned (first 5 rows) ---')
with open(clean_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        print(line.strip())
        if i>=4: break

# Check missing counts differences for numeric columns
orig = pd.read_csv(orig_path)
clean = pd.read_csv(clean_path)
print('\nOrig shape:', orig.shape, '\nClean shape:', clean.shape)

for col in clean.columns:
    o_missing = orig[col].isna().sum() if col in orig.columns else 'N/A'
    c_missing = clean[col].isna().sum()
    if o_missing!=c_missing:
        print(f'Col {col}: missing orig={o_missing}, clean={c_missing}')

# Show removed columns file
removed_file = art.removed_columns_json
if os.path.exists(removed_file):
    with open(removed_file,'r',encoding='utf-8') as f:
        print('\nremoved_columns.json:', f.read())

# Show imputation log
imp = art.imputation_log_json
if os.path.exists(imp):
    with open(imp,'r',encoding='utf-8') as f:
        obj=json.load(f)
        print('\nimputation entries:', len(obj.get('imputation_log', [])))
