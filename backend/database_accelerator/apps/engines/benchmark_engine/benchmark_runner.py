import json
import os
import tempfile
import uuid
from time import perf_counter

from database_accelerator.apps.api_gateway.accelerator_engine import run_accelerator_pipeline
from database_accelerator.apps.upload_module.models import dataset_manager
from database_accelerator.apps.engines.shared import write_pdf_report

from .edge_generator import EdgeCaseSpec, build_dataset


def register_dataset(dataframe, file_path, filename):
    return dataset_manager.create(
        dataset_id=str(uuid.uuid4()),
        filename=filename,
        file_path=file_path,
        file_type='csv',
        file_size=os.path.getsize(file_path),
        rows=int(dataframe.shape[0]),
        columns=int(dataframe.shape[1]),
        column_names=[str(column) for column in dataframe.columns],
        column_types={str(column): str(dataframe[column].dtype) for column in dataframe.columns},
    )


def verify_artifacts(result):
    missing = []
    for artifact_name, artifact_path in result.get('artifacts', {}).items():
        if not os.path.exists(artifact_path):
            missing.append(artifact_name)
    return missing


def run_benchmark(specs):
    results = []
    for index, spec in enumerate(specs, start=1):
        dataframe = build_dataset(spec, seed=100 + index)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as temp_file:
            dataframe.to_csv(temp_file.name, index=False)
            temp_path = temp_file.name
        metadata = register_dataset(dataframe, temp_path, f'{spec.name}.csv')
        started_at = perf_counter()
        result = run_accelerator_pipeline(metadata['id'])
        elapsed = round(perf_counter() - started_at, 4)
        timings = result.get('stage_timings', {})
        slowest_stage = None
        if timings:
            slowest_stage = max(((stage, value) for stage, value in timings.items() if stage != 'total'), key=lambda item: item[1], default=None)
        results.append({
            'dataset': spec.__dict__,
            'dataset_id': metadata['id'],
            'elapsed_seconds': elapsed,
            'slowest_stage': slowest_stage,
            'missing_artifacts': verify_artifacts(result),
            'stage_timings': timings,
            'rows_after_pipeline': result.get('quality_after', {}).get('rows'),
            'removed_columns_count': result.get('removed_columns_count'),
        })
    return results


def write_benchmark_report(results, output_path):
    slow_stage_counts = {}
    for entry in results:
        slowest = entry['slowest_stage'][0] if entry['slowest_stage'] else 'unknown'
        slow_stage_counts[slowest] = slow_stage_counts.get(slowest, 0) + 1

    payload = {'results': results, 'slow_stage_counts': slow_stage_counts}
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle, indent=2)
    return payload


def write_benchmark_summary_pdf(results, output_path):
    total_runs = len(results)
    successful_runs = sum(1 for entry in results if not entry.get('missing_artifacts'))
    slowest_stage = 'unknown'
    slowest_duration = 0.0

    for entry in results:
        timings = entry.get('stage_timings', {})
        for stage_name, duration in timings.items():
            if stage_name == 'total':
                continue
            if duration >= slowest_duration:
                slowest_stage = stage_name
                slowest_duration = duration

    summary_lines = [
        f'Total benchmark runs: {total_runs}',
        f'Successful runs: {successful_runs}',
        f'Failed runs: {max(0, total_runs - successful_runs)}',
        f'Slowest observed stage: {slowest_stage}',
        f'Slowest stage duration: {round(slowest_duration, 4)}s',
    ]
    write_pdf_report(output_path, summary_lines, title='Database Accelerator - Benchmark Summary')
    return output_path
