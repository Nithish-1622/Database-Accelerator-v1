import json
import os
import shutil
from datetime import datetime

from django.conf import settings

from database_accelerator.apps.report_module.report_engine import get_cleaning_report
from database_accelerator.apps.upload_module.models import dataset_manager


def export_cleaned_dataset(dataset_id):
    metadata = dataset_manager.get(dataset_id)
    if not metadata:
        raise FileNotFoundError('Dataset not found')

    cleaning_report = get_cleaning_report(dataset_id)
    if not cleaning_report:
        raise FileNotFoundError('Cleaning report not found')

    cleaned_file_path = cleaning_report.get('cleaned_file_path')
    if not cleaned_file_path or not os.path.exists(cleaned_file_path):
        raise FileNotFoundError('Cleaned dataset file not found')

    export_filename = f"{dataset_id}_cleaned.csv"
    export_path = os.path.join(settings.EXPORT_CLEANED_CSV_DIR, export_filename)
    shutil.copy2(cleaned_file_path, export_path)

    export_report = {
        'dataset_id': dataset_id,
        'filename': metadata.get('filename'),
        'export_filename': export_filename,
        'export_path': export_path,
        'exported_at': datetime.now().isoformat(),
        'source_cleaned_file': cleaned_file_path,
    }

    report_path = os.path.join(settings.EXPORT_JSON_REPORTS_DIR, f'{dataset_id}.json')
    with open(report_path, 'w', encoding='utf-8') as report_file:
        json.dump(export_report, report_file, indent=2)

    log_path = os.path.join(settings.EXPORT_LOGS_DIR, f'{dataset_id}.log')
    with open(log_path, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Exported {dataset_id} to {export_path} at {export_report['exported_at']}\n")

    return export_report