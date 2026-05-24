import json
import os

import pandas as pd
from django.conf import settings


def _read_dataset_file(file_path, file_type):
    if file_type == 'csv':
        return pd.read_csv(file_path)
    if file_type in ['xlsx', 'xls']:
        return pd.read_excel(file_path)
    if file_type == 'json':
        return pd.read_json(file_path)
    raise ValueError(f'Unsupported file type: {file_type}')


def _safe_ratio(numerator, denominator):
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def analyze_dataset(metadata):
    file_path = metadata.get('file_path')
    file_type = metadata.get('file_type')

    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError('Uploaded dataset file was not found on disk')

    dataframe = _read_dataset_file(file_path, file_type)
    total_cells = int(dataframe.shape[0] * dataframe.shape[1])
    missing_cells = int(dataframe.isna().sum().sum())
    duplicate_rows = int(dataframe.duplicated().sum())

    missing_by_column = {
        column: int(dataframe[column].isna().sum())
        for column in dataframe.columns
    }

    report = {
        'dataset_id': metadata.get('id'),
        'filename': metadata.get('filename'),
        'file_type': file_type,
        'rows': int(dataframe.shape[0]),
        'columns': int(dataframe.shape[1]),
        'missing_cells': missing_cells,
        'missing_values_by_column': missing_by_column,
        'duplicate_rows': duplicate_rows,
        'completeness_score': round(100 - _safe_ratio(missing_cells, total_cells), 2),
        'duplicate_rate': _safe_ratio(duplicate_rows, max(len(dataframe), 1)),
        'analyzed_at': metadata.get('updated_at') or metadata.get('created_at') or '',
        'column_names': list(dataframe.columns),
    }

    return report


def save_analysis_report(report):
    report_path = os.path.join(settings.REPORT_HEALTH_DIR, f"{report['dataset_id']}.json")
    with open(report_path, 'w', encoding='utf-8') as report_file:
        json.dump(report, report_file, indent=2)
    return report_path