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


def _clean_column(series):
    if pd.api.types.is_numeric_dtype(series):
        median_value = series.median()
        return series.fillna(median_value)

    if pd.api.types.is_datetime64_any_dtype(series):
        return series.fillna(method='ffill').fillna(method='bfill')

    cleaned = series.astype('string').str.strip()
    mode_values = cleaned.mode(dropna=True)
    fill_value = mode_values.iloc[0] if not mode_values.empty else ''
    return cleaned.fillna(fill_value)


def preprocess_dataset(metadata):
    file_path = metadata.get('file_path')
    file_type = metadata.get('file_type')

    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError('Uploaded dataset file was not found on disk')

    dataframe = _read_dataset_file(file_path, file_type)
    original_rows = int(dataframe.shape[0])
    original_missing = int(dataframe.isna().sum().sum())

    cleaned = dataframe.copy()
    for column in cleaned.columns:
        cleaned[column] = _clean_column(cleaned[column])

    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    cleaned_rows = int(cleaned.shape[0])
    cleaned_missing = int(cleaned.isna().sum().sum())
    duplicates_removed = original_rows - cleaned_rows

    cleaned_file_path = os.path.join(settings.UPLOAD_PROCESSED_DIR, f"{metadata['id']}_cleaned.csv")
    cleaned.to_csv(cleaned_file_path, index=False)

    report = {
        'dataset_id': metadata.get('id'),
        'filename': metadata.get('filename'),
        'file_type': file_type,
        'original_rows': original_rows,
        'cleaned_rows': cleaned_rows,
        'original_missing_cells': original_missing,
        'cleaned_missing_cells': cleaned_missing,
        'duplicates_removed': duplicates_removed,
        'cleaned_file_path': cleaned_file_path,
        'columns_processed': list(cleaned.columns),
    }

    return report


def save_preprocessing_report(report):
    report_path = os.path.join(settings.REPORT_CLEANING_DIR, f"{report['dataset_id']}.json")
    with open(report_path, 'w', encoding='utf-8') as report_file:
        json.dump(report, report_file, indent=2)
    return report_path