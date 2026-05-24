import json
from time import perf_counter

from .ingestion_engine.normalizer import normalize_dataframe
from .ingestion_engine.reader import read_dataset
from .ingestion_engine.validator import validate_dataframe
from .quality_engine.profiling import build_profile
from .quality_engine.missing_analyzer import analyze_missingness
from .quality_engine.duplicate_detector import detect_duplicates
from .quality_engine.outlier_detector import detect_outliers
from .imputation_engine.strategy_selector import select_strategies
from .imputation_engine.imputers import apply_imputation
from .imputation_engine.logger import build_imputation_log
from .intelligence_engine.correlation import build_correlation_report
from .intelligence_engine.feature_selector import select_features
from .intelligence_engine.recommender import build_model_input
from .export_engine.csv_exporter import export_csv
from .export_engine.pdf_exporter import export_pdf
from .export_engine.json_exporter import export_json
from .export_engine.summary_writer import export_summary
from database_accelerator.apps.artifacts import artifact_manager
from database_accelerator.apps.logging import logger_service
from database_accelerator.apps.storage import metadata_store
from .shared import build_artifact_paths, column_classification, dataset_optimizer, noise_and_duplicate_removal, quality_analysis, schema_detection


def run_pipeline(dataset_id):
    metadata = metadata_store.get(dataset_id)
    if not metadata:
        raise FileNotFoundError('Dataset not found')

    file_path = metadata.get('file_path') or metadata.get('upload_path')
    file_type = metadata.get('file_type', 'csv')
    if not file_path:
        raise FileNotFoundError('Dataset file not found on disk')

    dataframe = read_dataset(file_path, file_type)
    dataframe = normalize_dataframe(dataframe)
    validation = validate_dataframe(dataframe)
    artifacts = build_artifact_paths(dataset_id)
    stage_timings = {}
    stage_logs = []
    pipeline_start = perf_counter()

    def timed(stage_name, callback):
        stage_start = perf_counter()
        logger_service.log_stage_start(dataset_id, stage_name)
        try:
            value = callback()
            stage_timings[stage_name] = round(perf_counter() - stage_start, 4)
            logger_service.log_stage_end(dataset_id, stage_name, stage_timings[stage_name])
            stage_logs.append({'stage': stage_name, 'status': 'completed', 'duration': stage_timings[stage_name]})
            return value
        except Exception as exc:
            logger_service.log_stage_error(dataset_id, stage_name, exc)
            stage_logs.append({'stage': stage_name, 'status': 'failed', 'error': str(exc)})
            raise

    schema = timed('schema_detection', lambda: schema_detection(dataframe))
    classification = timed('column_classification', lambda: column_classification(dataframe))
    profile = timed('quality_profile', lambda: build_profile(dataframe))
    quality_before = timed('quality_analysis_before', lambda: quality_analysis(dataframe, classification['numeric']))
    _ = timed('duplicate_scan', lambda: detect_duplicates(dataframe))
    _ = timed('outlier_scan', lambda: detect_outliers(dataframe, classification['numeric']))
    patterns = timed('pattern_discovery', lambda: build_correlation_report(dataframe, classification['numeric']))
    strategy_plan = timed('imputation_strategy_selection', lambda: select_strategies(dataframe, classification, patterns))
    imputed_df, imputation_entries = timed('adaptive_imputation', lambda: apply_imputation(dataframe, classification, patterns))
    imputation_log = build_imputation_log(imputation_entries)
    denoised_df, removal_log = timed('noise_and_duplicate_removal', lambda: noise_and_duplicate_removal(imputed_df, classification['numeric']))
    feature_scores = timed('feature_selection', lambda: select_features(denoised_df, classification))
    optimized_df, removed_columns = timed('dataset_optimizer', lambda: dataset_optimizer(denoised_df, feature_scores))
    model_ready_df = timed('model_ready_transform', lambda: build_model_input(optimized_df, classification))
    quality_after = timed('quality_analysis_after', lambda: quality_analysis(optimized_df, [c for c in classification['numeric'] if c in optimized_df.columns]))

    timed('write_csv_artifacts', lambda: (export_csv(optimized_df, artifacts.clean_dataset_csv), export_csv(model_ready_df, artifacts.recommended_model_input_csv)))
    timed('write_json_artifacts', lambda: (
        export_json(artifacts.removed_columns_json, removed_columns),
        export_json(artifacts.imputation_log_json, {'imputation_log': imputation_entries, 'noise_and_duplicate_removal': removal_log}),
        export_json(artifacts.dataset_profile_json, profile),
        export_json(artifacts.execution_metrics_json, {'validation': validation, 'stage_timings': stage_timings}),
        export_json(artifacts.pipeline_log_json, stage_logs),
    ))

    pdf_lines = [
        f"Dataset: {metadata.get('filename')}",
        f"Rows (original): {schema['rows']}",
        f"Rows (optimized): {int(len(optimized_df))}",
        f"Missing cells (before): {quality_before['missing_cells']}",
        f"Missing cells (after): {quality_after['missing_cells']}",
        f"Duplicates removed: {removal_log['duplicate_rows_removed']}",
        f"Outlier rows removed: {removal_log['outlier_rows_removed']}",
        f"Health score (before): {quality_before['health_score']}%",
        f"Health score (after): {quality_after['health_score']}%",
        f"Removed columns: {len(removed_columns)}",
    ]
    timed('report_generation', lambda: (
        export_pdf(artifacts.quality_report_pdf, pdf_lines),
        export_pdf(artifacts.processing_summary_pdf, pdf_lines, title='Database Accelerator - Processing Summary'),
        export_summary(artifacts.feature_summary_txt, feature_scores, removed_columns),
    ))

    benchmark_payload = {
        'dataset_id': dataset_id,
        'stage_timings': stage_timings,
        'quality_before': quality_before,
        'quality_after': quality_after,
        'removed_columns_count': len(removed_columns),
    }
    export_json(artifacts.benchmark_report_json, benchmark_payload)
    artifact_registry = {}
    for name, path in {
        'clean_dataset.csv': artifacts.clean_dataset_csv,
        'quality_report.pdf': artifacts.quality_report_pdf,
        'removed_columns.json': artifacts.removed_columns_json,
        'imputation_log.json': artifacts.imputation_log_json,
        'feature_summary.txt': artifacts.feature_summary_txt,
        'recommended_model_input.csv': artifacts.recommended_model_input_csv,
        'pipeline_log.json': artifacts.pipeline_log_json,
        'benchmark_report.json': artifacts.benchmark_report_json,
        'dataset_profile.json': artifacts.dataset_profile_json,
        'execution_metrics.json': artifacts.execution_metrics_json,
        'processing_summary.pdf': artifacts.processing_summary_pdf,
    }.items():
        artifact_manager.register_artifact(artifact_registry, name, path)

    stage_timings['total'] = round(perf_counter() - pipeline_start, 4)
    metadata_store.update_status(dataset_id, 'optimized')
    metadata_store.create({
        'id': dataset_id,
        'filename': metadata.get('filename'),
        'file_path': file_path,
        'status': 'optimized',
        'created_at': metadata.get('created_at'),
        'processing_time': stage_timings['total'],
        'artifact_paths': artifact_registry,
        'benchmark_status': 'completed',
    })

    return {
        'dataset_id': dataset_id,
        'input_file': metadata.get('filename'),
        'schema_detection': schema,
        'column_classification': classification,
        'pattern_discovery': patterns,
        'quality_before': quality_before,
        'quality_after': quality_after,
        'feature_importance': feature_scores,
        'removed_columns_count': len(removed_columns),
        'stage_timings': stage_timings,
        'artifacts': {name: data['path'] for name, data in artifact_registry.items()},
    }
