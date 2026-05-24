import os
from pathlib import Path
import uuid
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE','database_accelerator.settings')
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import django
django.setup()

from database_accelerator.apps.upload_module.models import dataset_manager
from database_accelerator.apps.engines.pipeline_manager import run_pipeline
from database_accelerator.apps.engines.shared import build_artifact_paths

# create dirty DataFrame
rows = 50
import numpy as np
rng = np.random.default_rng(123)

df = pd.DataFrame({
    'id': range(rows),
    'value': rng.normal(loc=0, scale=1, size=rows),
    'score': rng.integers(0,100,size=rows),
    'category': rng.choice(['A','B','C'], size=rows)
})
# inject NaNs
for i in range(0,10):
    df.loc[i,'value'] = np.nan
# inject duplicates
df = pd.concat([df, df.iloc[0:5]], ignore_index=True)
# inject outliers
df.loc[10,'score'] = 9999

# write to uploads/raw
UPLOAD_DIR = Path('.') / 'uploads' / 'raw'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

dataset_id = str(uuid.uuid4())
file_path = UPLOAD_DIR / f"{dataset_id}_demo_dirty.csv"
df.to_csv(file_path, index=False)

# register
meta = dataset_manager.create(
    dataset_id=dataset_id,
    filename=file_path.name,
    file_path=str(file_path),
    file_type='csv',
    file_size=file_path.stat().st_size,
    rows=len(df),
    columns=len(df.columns),
    column_names=list(df.columns),
    column_types={c:str(df[c].dtype) for c in df.columns}
)

print('Registered dataset id:', dataset_id)
print('Running pipeline...')
result = run_pipeline(dataset_id)
print('Pipeline finished. Stage timings:', result.get('stage_timings'))

# inspect artifacts
art = build_artifact_paths(dataset_id)
clean = pd.read_csv(art.clean_dataset_csv)
model = pd.read_csv(art.recommended_model_input_csv)
print('\nOriginal shape:', df.shape)
print('Clean shape   :', clean.shape)
print('Model shape   :', model.shape)

# show imputation log and removed columns
import json
if os.path.exists(art.imputation_log_json):
    with open(art.imputation_log_json,'r',encoding='utf-8') as f:
        try:
            imp = json.load(f)
            print('\nimputation entries:', len(imp.get('imputation_log', [])))
        except Exception as e:
            print('Failed to read imputation log', e)
if os.path.exists(art.removed_columns_json):
    with open(art.removed_columns_json,'r',encoding='utf-8') as f:
        print('\nremoved_columns:', f.read())

print('\nSample clean rows:')
print(clean.head(8).to_string(index=False))
print('\nDone')
