import argparse
import json
import os
import sys
import tempfile
import uuid
from dataclasses import dataclass
from time import perf_counter

import numpy as np
import pandas as pd


def _bootstrap_django():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'database_accelerator.settings')

    import django

    django.setup()


@dataclass
class DatasetSpec:
    name: str
    rows: int
    numeric_columns: int
    text_columns: int
    missing_rate: float
    duplicate_rate: float


def _build_dataset(spec: DatasetSpec, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    base = pd.DataFrame()
    # Base signals
    base['signal_a'] = rng.normal(loc=50, scale=12, size=spec.rows)
    base['signal_b'] = base['signal_a'] * 0.7 + rng.normal(loc=0, scale=6, size=spec.rows)
    base['signal_c'] = rng.normal(loc=100, scale=20, size=spec.rows)

    # Numeric columns (allow many for very_wide scenario)
    for index in range(max(0, spec.numeric_columns - 3)):
        base[f'numeric_{index + 1}'] = rng.normal(loc=index * 8, scale=15 + index, size=spec.rows)

    # Text columns: categories or heavy text depending on scenario
    category_pool = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Omega', 'Prime']
    for index in range(spec.text_columns):
        base[f'category_{index + 1}'] = rng.choice(category_pool, size=spec.rows)

    # Scenario-specific augmentations
    name = getattr(spec, 'name', '')
    if 'very_wide' in name:
        # Add many small numeric columns in bulk to avoid DataFrame fragmentation
        wide_cols = {
            f'wide_{j}': rng.integers(0, 100, size=spec.rows)
            for j in range(200)
        }
        base = pd.concat([base, pd.DataFrame(wide_cols)], axis=1)

    if 'all_constant' in name:
        # Replace many columns with constants
        for j in range(0, min(10, spec.numeric_columns)):
            base[f'const_{j}'] = 42

    if 'extreme_missing' in name:
        # Set very high missing rate if requested
        mask = rng.random(base.shape) < max(spec.missing_rate, 0.9)
        base = base.mask(mask)

    if 'mixed_types' in name:
        # Create columns with mixed numeric and string entries
        mixed = []
        for i in range(spec.rows):
            mixed.append(str(rng.integers(0, 100)) if (i % 7) != 0 else 'MIXED')
        base['mixed_col'] = mixed

    if 'nested_json' in name:
        # JSON strings in a column
        import json as _json

        def _rand_obj(i):
            return _json.dumps({'a': int(rng.integers(0, 100)), 'tags': rng.choice(category_pool, size=int(rng.integers(1, 4))).tolist()})

        base['json_payload'] = [_rand_obj(i) for i in range(spec.rows)]

    if 'heavy_text' in name:
        # Very large text fields
        lorem = 'lorem ipsum ' * 50
        base['long_text'] = [lorem + str(i) for i in range(spec.rows)]

    if 'extreme_ranges' in name:
        # Very large/small numeric values
        base['big_val'] = rng.uniform(low=1e9, high=1e12, size=spec.rows)
        base['small_val'] = rng.uniform(low=1e-9, high=1e-3, size=spec.rows)

    if 'datetime_anomalies' in name:
        # Mixed date formats and some invalid entries
        dates = []
        for i in range(spec.rows):
            if i % 10 == 0:
                dates.append('not_a_date')
            elif i % 3 == 0:
                dates.append(pd.Timestamp('2020-01-01') + pd.Timedelta(days=int(i)))
            else:
                dates.append((pd.Timestamp('2020-01-01') + pd.Timedelta(days=int(i))).strftime('%d/%m/%Y'))
        base['weird_date'] = dates

    if 'unicode' in name:
        # Include unicode and emoji
        base['unicode_col'] = [f'Ω – emoji 🔥 {i}' for i in range(spec.rows)]

    if spec.missing_rate > 0 and 'extreme_missing' not in name:
        mask = rng.random(base.shape) < spec.missing_rate
        base = base.mask(mask)

    if spec.duplicate_rate > 0:
        duplicate_count = max(1, int(spec.rows * spec.duplicate_rate))
        duplicate_rows = base.sample(n=min(duplicate_count, len(base)), random_state=seed)
        base = pd.concat([base, duplicate_rows], ignore_index=True)

    # De-fragment frame if many columns were concatenated/inserted
    base = base.copy()
    base.insert(0, 'row_id', range(1, len(base) + 1))
    return base


def _register_dataset(df: pd.DataFrame, file_path: str, filename: str):
    from database_accelerator.apps.upload_module.models import dataset_manager

    return dataset_manager.create(
        dataset_id=str(uuid.uuid4()),
        filename=filename,
        file_path=file_path,
        file_type='csv',
        file_size=os.path.getsize(file_path),
        rows=int(df.shape[0]),
        columns=int(df.shape[1]),
        column_names=[str(column) for column in df.columns],
        column_types={str(column): str(df[column].dtype) for column in df.columns},
    )


def _verify_artifacts(result: dict):
    missing = []
    for artifact_name, artifact_path in result.get('artifacts', {}).items():
        if not os.path.exists(artifact_path):
            missing.append(artifact_name)
    return missing


def run_benchmark(specs):
    from database_accelerator.apps.api_gateway.accelerator_engine import run_accelerator_pipeline

    results = []
    for index, spec in enumerate(specs, start=1):
        dataframe = _build_dataset(spec, seed=100 + index)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as temp_file:
            dataframe.to_csv(temp_file.name, index=False)
            temp_path = temp_file.name

        metadata = _register_dataset(dataframe, temp_path, f'{spec.name}.csv')

        started_at = perf_counter()
        result = run_accelerator_pipeline(metadata['id'])
        elapsed = round(perf_counter() - started_at, 4)

        missing_artifacts = _verify_artifacts(result)
        timings = result.get('stage_timings', {})
        slowest_stage = None
        if timings:
            slowest_stage = max(((stage, value) for stage, value in timings.items() if stage != 'total'), key=lambda item: item[1], default=None)

        results.append({
            'dataset': spec.__dict__,
            'dataset_id': metadata['id'],
            'elapsed_seconds': elapsed,
            'slowest_stage': slowest_stage,
            'missing_artifacts': missing_artifacts,
            'stage_timings': timings,
            'rows_after_pipeline': result.get('quality_after', {}).get('rows'),
            'removed_columns_count': result.get('removed_columns_count'),
        })

    return results


def main():
    _bootstrap_django()

    parser = argparse.ArgumentParser(description='Benchmark the Database Accelerator pipeline with synthetic datasets.')
    parser.add_argument('--output', default='', help='Optional path to write benchmark results as JSON.')
    args = parser.parse_args()

    specs = [
        DatasetSpec(name='small_clean', rows=250, numeric_columns=6, text_columns=3, missing_rate=0.03, duplicate_rate=0.02),
        DatasetSpec(name='medium_noisy', rows=2500, numeric_columns=12, text_columns=5, missing_rate=0.12, duplicate_rate=0.06),
        DatasetSpec(name='large_sparse', rows=12000, numeric_columns=18, text_columns=6, missing_rate=0.2, duplicate_rate=0.04),
        # Edge cases
        DatasetSpec(name='very_wide', rows=500, numeric_columns=50, text_columns=2, missing_rate=0.05, duplicate_rate=0.01),
        DatasetSpec(name='all_constant', rows=300, numeric_columns=10, text_columns=2, missing_rate=0.01, duplicate_rate=0.0),
        DatasetSpec(name='extreme_missing', rows=1000, numeric_columns=8, text_columns=3, missing_rate=0.95, duplicate_rate=0.0),
        DatasetSpec(name='mixed_types', rows=800, numeric_columns=6, text_columns=2, missing_rate=0.1, duplicate_rate=0.02),
        DatasetSpec(name='nested_json', rows=600, numeric_columns=4, text_columns=1, missing_rate=0.02, duplicate_rate=0.0),
        DatasetSpec(name='heavy_text', rows=400, numeric_columns=3, text_columns=2, missing_rate=0.01, duplicate_rate=0.0),
        DatasetSpec(name='extreme_ranges', rows=500, numeric_columns=6, text_columns=1, missing_rate=0.01, duplicate_rate=0.0),
        DatasetSpec(name='datetime_anomalies', rows=700, numeric_columns=4, text_columns=1, missing_rate=0.02, duplicate_rate=0.0),
        DatasetSpec(name='unicode', rows=350, numeric_columns=3, text_columns=2, missing_rate=0.01, duplicate_rate=0.0),
    ]

    results = run_benchmark(specs)
    slow_stage_counts = {}
    for entry in results:
        slowest = entry['slowest_stage'][0] if entry['slowest_stage'] else 'unknown'
        slow_stage_counts[slowest] = slow_stage_counts.get(slowest, 0) + 1

    payload = {
        'results': results,
        'slow_stage_counts': slow_stage_counts,
    }

    print(json.dumps(payload, indent=2))

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as output_file:
            json.dump(payload, output_file, indent=2)


if __name__ == '__main__':
    main()