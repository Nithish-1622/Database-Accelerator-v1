"""
Generate sample CSV datasets for frontend testing and save them to the repository `sample/` folder.
This script reuses the existing EdgeCaseSpec/build_dataset helper in the project.
"""
import os
from pathlib import Path
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'database_accelerator.settings')

try:
    from database_accelerator.apps.engines.benchmark_engine.edge_generator import EdgeCaseSpec, build_dataset
except Exception:
    # fallback: simple generator
    EdgeCaseSpec = None
    def build_dataset(spec, seed=0):
        import numpy as np
        rng = np.random.default_rng(seed)
        df = pd.DataFrame({
            'a': rng.normal(size=spec.rows),
            'b': rng.integers(0, 10, size=spec.rows),
            'cat': rng.choice(['Alpha','Beta','Gamma'], size=spec.rows),
        })
        return df

OUT = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
SAMPLE_DIR = OUT / 'sample'
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

class SimpleSpec:
    def __init__(self, name, rows, numeric_columns=4, text_columns=1, missing_rate=0.0, duplicate_rate=0.0):
        self.name = name
        self.rows = rows
        self.numeric_columns = numeric_columns
        self.text_columns = text_columns
        self.missing_rate = missing_rate
        self.duplicate_rate = duplicate_rate

specs = [
    ('small_clean.csv', EdgeCaseSpec(name='small_clean', rows=250, numeric_columns=6, text_columns=3, missing_rate=0.03, duplicate_rate=0.02) if 'EdgeCaseSpec' in globals() and EdgeCaseSpec is not None else SimpleSpec('small_clean', rows=250, numeric_columns=6, text_columns=3, missing_rate=0.03, duplicate_rate=0.02)),
    ('very_wide.csv', EdgeCaseSpec(name='very_wide', rows=300, numeric_columns=50, text_columns=2, missing_rate=0.02, duplicate_rate=0.01) if 'EdgeCaseSpec' in globals() and EdgeCaseSpec is not None else SimpleSpec('very_wide', rows=300, numeric_columns=50, text_columns=2, missing_rate=0.02, duplicate_rate=0.01)),
    ('mixed_types.csv', EdgeCaseSpec(name='mixed_types', rows=200, numeric_columns=6, text_columns=2, missing_rate=0.1, duplicate_rate=0.02) if 'EdgeCaseSpec' in globals() and EdgeCaseSpec is not None else SimpleSpec('mixed_types', rows=200, numeric_columns=6, text_columns=2, missing_rate=0.1, duplicate_rate=0.02)),
    ('extreme_missing.csv', EdgeCaseSpec(name='extreme_missing', rows=300, numeric_columns=8, text_columns=3, missing_rate=0.95, duplicate_rate=0.0) if 'EdgeCaseSpec' in globals() and EdgeCaseSpec is not None else SimpleSpec('extreme_missing', rows=300, numeric_columns=8, text_columns=3, missing_rate=0.95, duplicate_rate=0.0)),
    ('datetime_anomalies.csv', EdgeCaseSpec(name='datetime_anomalies', rows=220, numeric_columns=4, text_columns=1, missing_rate=0.02, duplicate_rate=0.0) if 'EdgeCaseSpec' in globals() and EdgeCaseSpec is not None else SimpleSpec('datetime_anomalies', rows=220, numeric_columns=4, text_columns=1, missing_rate=0.02, duplicate_rate=0.0)),
]

created = []
for filename, spec in specs:
    try:
        df = build_dataset(spec, seed=42)
    except Exception:
        # fallback: simple DataFrame
        import numpy as np
        rng = np.random.default_rng(42)
        rows = getattr(spec, 'rows', 200)
        df = pd.DataFrame({
            'numeric_1': rng.normal(size=rows),
            'numeric_2': rng.normal(size=rows),
            'text_1': rng.choice(['A','B','C'], size=rows),
        })

    path = SAMPLE_DIR / filename
    df.to_csv(path, index=False)
    created.append(path)

print('Created sample files:')
for p in created:
    print(p)
