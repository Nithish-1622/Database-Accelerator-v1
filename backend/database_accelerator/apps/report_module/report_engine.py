import json
import os

from django.conf import settings


def _read_json(path):
    if not os.path.exists(path):
        return None

    with open(path, 'r', encoding='utf-8') as report_file:
        return json.load(report_file)


def get_analysis_report(dataset_id):
    report_path = os.path.join(settings.REPORT_HEALTH_DIR, f'{dataset_id}.json')
    return _read_json(report_path)


def get_cleaning_report(dataset_id):
    report_path = os.path.join(settings.REPORT_CLEANING_DIR, f'{dataset_id}.json')
    return _read_json(report_path)


def get_intelligence_report(dataset_id):
    report_path = os.path.join(settings.REPORT_INTELLIGENCE_DIR, f'{dataset_id}.json')
    return _read_json(report_path)


def list_report_ids():
    report_ids = set()

    for directory in [settings.REPORT_HEALTH_DIR, settings.REPORT_CLEANING_DIR]:
        if not os.path.exists(directory):
            continue

        for file_name in os.listdir(directory):
            if file_name.endswith('.json'):
                report_ids.add(file_name.replace('.json', ''))

    return sorted(report_ids)


def get_combined_report(dataset_id):
    return {
        'dataset_id': dataset_id,
        'analysis_report': get_analysis_report(dataset_id),
        'cleaning_report': get_cleaning_report(dataset_id),
        'intelligence_report': get_intelligence_report(dataset_id),
    }