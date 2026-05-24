import json
import os

import pandas as pd
from django.conf import settings

from database_accelerator.apps.report_module.report_engine import get_cleaning_report
from database_accelerator.apps.upload_module.models import dataset_manager


def _read_dataset_file(file_path, file_type):
    if file_type == 'csv':
        return pd.read_csv(file_path)
    if file_type in ['xlsx', 'xls']:
        return pd.read_excel(file_path)
    if file_type == 'json':
        return pd.read_json(file_path)
    raise ValueError(f'Unsupported file type: {file_type}')


def _infer_file_type(file_path, fallback_file_type):
    _, extension = os.path.splitext(file_path)
    extension = extension.lower().lstrip('.')

    if extension in ['csv', 'xlsx', 'xls', 'json']:
        return extension

    return fallback_file_type


def _resolve_input_path(metadata):
    cleaning_report = get_cleaning_report(metadata['id'])
    cleaned_file_path = cleaning_report.get('cleaned_file_path') if cleaning_report else None

    if cleaned_file_path and os.path.exists(cleaned_file_path):
        return cleaned_file_path, _infer_file_type(cleaned_file_path, metadata.get('file_type')), True

    original_file_path = metadata.get('file_path')
    return original_file_path, _infer_file_type(original_file_path, metadata.get('file_type')), False


def _get_column_groups(dataframe):
    return {
        'numeric_columns': list(dataframe.select_dtypes(include='number').columns),
        'categorical_columns': list(dataframe.select_dtypes(include=['object', 'string', 'category']).columns),
        'datetime_columns': list(dataframe.select_dtypes(include=['datetime', 'datetimetz']).columns),
    }


def _get_strong_correlations(dataframe, numeric_columns):
    if len(numeric_columns) < 2:
        return []

    strong_correlations = []
    correlation_matrix = dataframe[numeric_columns].corr(numeric_only=True)

    for left_index, left_column in enumerate(numeric_columns):
        for right_column in numeric_columns[left_index + 1:]:
            correlation_value = correlation_matrix.loc[left_column, right_column]
            if pd.notna(correlation_value) and abs(correlation_value) >= 0.75:
                strong_correlations.append({
                    'left': left_column,
                    'right': right_column,
                    'correlation': round(float(correlation_value), 4),
                })

    return strong_correlations


def _get_categorical_insights(dataframe, categorical_columns):
    high_cardinality_columns = []
    frequent_values = {}

    for column in categorical_columns:
        unique_ratio = round(dataframe[column].nunique(dropna=True) / max(len(dataframe), 1), 4)
        if unique_ratio >= 0.5:
            high_cardinality_columns.append({
                'column': column,
                'unique_ratio': unique_ratio,
            })

        top_values = dataframe[column].astype('string').fillna('Missing').value_counts().head(3)
        frequent_values[column] = [
            {'value': index, 'count': int(count)}
            for index, count in top_values.items()
        ]

    return high_cardinality_columns, frequent_values


def discover_patterns(metadata):
    file_path, file_type, using_cleaned_data = _resolve_input_path(metadata)

    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError('Dataset file was not found on disk')

    dataframe = _read_dataset_file(file_path, file_type)
    column_groups = _get_column_groups(dataframe)
    numeric_columns = column_groups['numeric_columns']
    categorical_columns = column_groups['categorical_columns']
    datetime_columns = column_groups['datetime_columns']
    strong_correlations = _get_strong_correlations(dataframe, numeric_columns)
    high_cardinality_columns, frequent_values = _get_categorical_insights(dataframe, categorical_columns)

    report = {
        'dataset_id': metadata.get('id'),
        'filename': metadata.get('filename'),
        'source': 'cleaned' if using_cleaned_data else 'raw',
        'rows': int(dataframe.shape[0]),
        'columns': int(dataframe.shape[1]),
        'numeric_columns': numeric_columns,
        'categorical_columns': categorical_columns,
        'datetime_columns': datetime_columns,
        'strong_correlations': strong_correlations,
        'high_cardinality_columns': high_cardinality_columns,
        'frequent_values': frequent_values,
        'duplicate_rows': int(dataframe.duplicated().sum()),
        'distinct_rows': int(dataframe.drop_duplicates().shape[0]),
        'pattern_summary': {
            'has_numeric_patterns': len(numeric_columns) > 0,
            'has_categorical_patterns': len(categorical_columns) > 0,
            'has_datetime_patterns': len(datetime_columns) > 0,
        },
    }

    return report


def save_intelligence_report(report):
    report_path = os.path.join(settings.REPORT_INTELLIGENCE_DIR, f"{report['dataset_id']}.json")
    with open(report_path, 'w', encoding='utf-8') as report_file:
        json.dump(report, report_file, indent=2)
    return report_path


def build_intelligence_report(dataset_id):
    metadata = dataset_manager.get(dataset_id)
    if not metadata:
        raise FileNotFoundError('Dataset not found')

    report = discover_patterns(metadata)
    save_intelligence_report(report)
    return report