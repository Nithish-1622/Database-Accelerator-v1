from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class EdgeCaseSpec:
    name: str
    rows: int
    numeric_columns: int
    text_columns: int
    missing_rate: float
    duplicate_rate: float


def build_dataset(spec: EdgeCaseSpec, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    base = pd.DataFrame()
    base['signal_a'] = rng.normal(loc=50, scale=12, size=spec.rows)
    base['signal_b'] = base['signal_a'] * 0.7 + rng.normal(loc=0, scale=6, size=spec.rows)
    base['signal_c'] = rng.normal(loc=100, scale=20, size=spec.rows)

    for index in range(max(0, spec.numeric_columns - 3)):
        base[f'numeric_{index + 1}'] = rng.normal(loc=index * 8, scale=15 + index, size=spec.rows)

    category_pool = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Omega', 'Prime']
    for index in range(spec.text_columns):
        base[f'category_{index + 1}'] = rng.choice(category_pool, size=spec.rows)

    name = getattr(spec, 'name', '')
    if 'very_wide' in name:
        wide_cols = {f'wide_{j}': rng.integers(0, 100, size=spec.rows) for j in range(200)}
        base = pd.concat([base, pd.DataFrame(wide_cols)], axis=1)
    if 'all_constant' in name:
        for j in range(0, min(10, spec.numeric_columns)):
            base[f'const_{j}'] = 42
    if 'extreme_missing' in name:
        mask = rng.random(base.shape) < max(spec.missing_rate, 0.9)
        base = base.mask(mask)
    if 'mixed_types' in name:
        base['mixed_col'] = [str(rng.integers(0, 100)) if (i % 7) != 0 else 'MIXED' for i in range(spec.rows)]
    if 'nested_json' in name:
        import json as _json
        base['json_payload'] = [_json.dumps({'a': int(rng.integers(0, 100)), 'tags': rng.choice(category_pool, size=int(rng.integers(1, 4))).tolist()}) for _ in range(spec.rows)]
    if 'heavy_text' in name:
        lorem = 'lorem ipsum ' * 50
        base['long_text'] = [lorem + str(i) for i in range(spec.rows)]
    if 'extreme_ranges' in name:
        base['big_val'] = rng.uniform(low=1e9, high=1e12, size=spec.rows)
        base['small_val'] = rng.uniform(low=1e-9, high=1e-3, size=spec.rows)
    if 'datetime_anomalies' in name:
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
        base['unicode_col'] = [f'Ω – emoji 🔥 {i}' for i in range(spec.rows)]

    if spec.missing_rate > 0 and 'extreme_missing' not in name:
        mask = rng.random(base.shape) < spec.missing_rate
        base = base.mask(mask)
    if spec.duplicate_rate > 0:
        duplicate_count = max(1, int(spec.rows * spec.duplicate_rate))
        duplicate_rows = base.sample(n=min(duplicate_count, len(base)), random_state=seed)
        base = pd.concat([base, duplicate_rows], ignore_index=True)
    base = base.copy()
    base.insert(0, 'row_id', range(1, len(base) + 1))
    return base
