import json
import math
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

try:
    from sklearn.experimental import enable_iterative_imputer  # noqa: F401
    from sklearn.impute import KNNImputer, IterativeImputer
    from sklearn.feature_selection import mutual_info_regression
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False
    KNNImputer = None
    IterativeImputer = None
    mutual_info_regression = None


@dataclass
class ArtifactPaths:
    artifact_dir: str
    clean_dataset_csv: str
    quality_report_pdf: str
    removed_columns_json: str
    imputation_log_json: str
    feature_summary_txt: str
    recommended_model_input_csv: str
    pipeline_log_json: str
    benchmark_report_json: str
    dataset_profile_json: str
    execution_metrics_json: str
    processing_summary_pdf: str


def read_dataset(file_path: str, file_type: str) -> pd.DataFrame:
    if file_type == 'csv':
        return pd.read_csv(file_path)
    if file_type in ['xlsx', 'xls']:
        return pd.read_excel(file_path)
    if file_type == 'json':
        return pd.read_json(file_path)
    raise ValueError(f'Unsupported file type: {file_type}')


def build_artifact_paths(dataset_id: str) -> ArtifactPaths:
    artifact_dir = os.path.join(settings.EXPORT_DIR, dataset_id)
    os.makedirs(artifact_dir, exist_ok=True)
    return ArtifactPaths(
        artifact_dir=artifact_dir,
        clean_dataset_csv=os.path.join(artifact_dir, 'clean_dataset.csv'),
        quality_report_pdf=os.path.join(artifact_dir, 'quality_report.pdf'),
        removed_columns_json=os.path.join(artifact_dir, 'removed_columns.json'),
        imputation_log_json=os.path.join(artifact_dir, 'imputation_log.json'),
        feature_summary_txt=os.path.join(artifact_dir, 'feature_summary.txt'),
        recommended_model_input_csv=os.path.join(artifact_dir, 'recommended_model_input.csv'),
        pipeline_log_json=os.path.join(artifact_dir, 'pipeline_log.json'),
        benchmark_report_json=os.path.join(artifact_dir, 'benchmark_report.json'),
        dataset_profile_json=os.path.join(artifact_dir, 'dataset_profile.json'),
        execution_metrics_json=os.path.join(artifact_dir, 'execution_metrics.json'),
        processing_summary_pdf=os.path.join(artifact_dir, 'processing_summary.pdf'),
    )


def schema_detection(dataframe: pd.DataFrame) -> Dict:
    column_schema = []
    for column in dataframe.columns:
        series = dataframe[column]
        column_schema.append({
            'name': str(column),
            'dtype': str(series.dtype),
            'missing_count': int(series.isna().sum()),
            'missing_ratio': round(float(series.isna().mean()), 4),
            'unique_count': int(series.nunique(dropna=True)),
        })

    return {'rows': int(dataframe.shape[0]), 'columns': int(dataframe.shape[1]), 'column_schema': column_schema}


def column_classification(dataframe: pd.DataFrame) -> Dict[str, List[str]]:
    import warnings
    datetime_columns: List[str] = []
    for column in dataframe.columns:
        series = dataframe[column]
        # treat explicit datetime dtypes as datetime
        is_tz = False
        try:
            is_tz = isinstance(series.dtype, pd.DatetimeTZDtype)
        except Exception:
            is_tz = False
        if pd.api.types.is_datetime64_any_dtype(series) or is_tz:
            datetime_columns.append(str(column))
            continue
        # only attempt string-like columns for heuristic detection
        if series.dtype.kind not in {'O', 'U', 'S'}:
            continue
        sample = series.dropna().astype('string').head(25)
        if sample.empty:
            continue
        # suppress user warnings from pandas trying multiple parse strategies
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=UserWarning)
            parsed = pd.to_datetime(sample, errors='coerce')
        if float(parsed.notna().mean()) >= 0.8 and parsed.nunique(dropna=True) > 0:
            datetime_columns.append(str(column))

    text_columns = [str(c) for c in dataframe.select_dtypes(include=['object', 'string', 'category']).columns if str(c) not in datetime_columns]
    return {
        'numeric': [str(c) for c in dataframe.select_dtypes(include=['number']).columns],
        'text': text_columns,
        'datetime': sorted(set(datetime_columns) | {str(c) for c in dataframe.select_dtypes(include=['datetime', 'datetimetz']).columns}),
        'boolean': [str(c) for c in dataframe.select_dtypes(include=['bool']).columns],
    }


def select_priority_numeric_columns(dataframe: pd.DataFrame, numeric_columns: List[str], limit: int) -> List[str]:
    if len(numeric_columns) <= limit:
        return numeric_columns
    variances = {}
    for column in numeric_columns:
        variance = float(dataframe[column].var()) if pd.notna(dataframe[column].var()) else 0.0
        variances[column] = variance
    ranked = sorted(variances.items(), key=lambda item: item[1], reverse=True)
    return [column for column, _ in ranked[:limit]]


def sample_for_pattern_discovery(dataframe: pd.DataFrame, numeric_columns: List[str]) -> pd.DataFrame:
    if len(dataframe) <= 5000 or len(numeric_columns) <= 2:
        return dataframe
    return dataframe.sample(n=5000, random_state=42)


def flatten_correlation_pairs(matrix: pd.DataFrame, label: str) -> List[Dict]:
    pairs = []
    for index, left in enumerate(matrix.columns):
        for right in matrix.columns[index + 1:]:
            value = matrix.loc[left, right]
            if pd.notna(value):
                pairs.append({'method': label, 'left': str(left), 'right': str(right), 'score': round(float(value), 4)})
    return pairs


def safe_mutual_information_score(x: np.ndarray, y: np.ndarray):
    if not SKLEARN_AVAILABLE:
        return None
    try:
        score = mutual_info_regression(x, y, random_state=42)
        return score[0]
    except Exception:
        return None


def build_mutual_information_pairs(dataframe: pd.DataFrame, numeric_columns: List[str]) -> List[Dict]:
    if not SKLEARN_AVAILABLE or len(dataframe) <= 10:
        return []
    if len(dataframe) > 2000 or len(numeric_columns) > 10:
        return []

    pairs: List[Dict] = []
    prioritized_columns = select_priority_numeric_columns(dataframe, numeric_columns, limit=12)
    clean_numeric = dataframe[prioritized_columns].copy()
    if len(clean_numeric) > 5000:
        clean_numeric = clean_numeric.sample(n=5000, random_state=42)
    clean_numeric = clean_numeric.fillna(clean_numeric.median(numeric_only=True))

    for index, left in enumerate(prioritized_columns):
        for right in prioritized_columns[index + 1:]:
            y = clean_numeric[right].to_numpy()
            if len(np.unique(y)) <= 1:
                continue
            score = safe_mutual_information_score(clean_numeric[[left]].to_numpy(), y)
            if score is None:
                continue
            pairs.append({'method': 'mutual_information', 'left': str(left), 'right': str(right), 'score': round(float(score), 4)})
    return pairs


def pattern_discovery(dataframe: pd.DataFrame, numeric_columns: List[str]) -> Dict:
    if len(numeric_columns) < 2:
        return {'pearson': [], 'spearman': [], 'mutual_information': []}
    selected_numeric = numeric_columns
    if len(numeric_columns) > 40:
        selected_numeric = select_priority_numeric_columns(dataframe, numeric_columns, limit=30)
    pattern_frame = sample_for_pattern_discovery(dataframe, selected_numeric)
    pearson = pattern_frame[selected_numeric].corr(method='pearson', numeric_only=True)
    spearman = pattern_frame[selected_numeric].corr(method='spearman', numeric_only=True)
    return {
        'pearson': flatten_correlation_pairs(pearson, 'pearson'),
        'spearman': flatten_correlation_pairs(spearman, 'spearman'),
        'mutual_information': build_mutual_information_pairs(pattern_frame, selected_numeric),
    }


def quality_analysis(dataframe: pd.DataFrame, numeric_columns: List[str]) -> Dict:
    total_rows = int(len(dataframe))
    total_cells = int(dataframe.shape[0] * dataframe.shape[1])
    missing_cells = int(dataframe.isna().sum().sum())
    duplicate_rows = int(dataframe.duplicated().sum())
    empty_rows = int((dataframe.isna().all(axis=1)).sum())
    outlier_rows = 0

    if numeric_columns:
        outlier_mask = pd.Series(False, index=dataframe.index)
        for column in numeric_columns:
            series = dataframe[column]
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            if pd.isna(iqr) or iqr == 0:
                continue
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outlier_mask = outlier_mask | ((series < lower) | (series > upper))
        outlier_rows = int(outlier_mask.sum())

    health_score = 100.0
    health_score -= (missing_cells / max(total_cells, 1)) * 45.0
    health_score -= (duplicate_rows / max(total_rows, 1)) * 30.0
    health_score -= (outlier_rows / max(total_rows, 1)) * 25.0
    health_score = max(0.0, round(health_score, 2))

    return {
        'rows': total_rows,
        'missing_cells': missing_cells,
        'duplicate_rows': duplicate_rows,
        'empty_rows': empty_rows,
        'outlier_rows': outlier_rows,
        'health_score': health_score,
        'missing_by_column': {str(column): int(dataframe[column].isna().sum()) for column in dataframe.columns},
    }


def choose_numeric_imputation_method(missing_ratio: float, skewness: float, has_relation: bool, numeric_count: int, row_count: int) -> str:
    if row_count > 50000 or numeric_count > 20:
        return 'mean' if missing_ratio < 0.05 else 'median'
    if missing_ratio < 0.05:
        return 'mean'
    if abs(skewness) > 1.0:
        return 'median'
    if has_relation and SKLEARN_AVAILABLE and numeric_count >= 2 and row_count <= 20000:
        return 'knn'
    if missing_ratio > 0.25 and SKLEARN_AVAILABLE and row_count <= 15000 and numeric_count <= 12:
        return 'iterative'
    return 'median'


def extract_strong_relations(patterns: Dict) -> set:
    return {tuple(sorted((item['left'], item['right']))) for item in patterns.get('pearson', []) if abs(item['score']) >= 0.7}


def build_numeric_imputation_plan(df: pd.DataFrame, numeric_columns: List[str], strong_relations: set) -> Dict:
    log_entries = []
    mean_columns: List[str] = []
    median_columns: List[str] = []
    knn_columns: List[str] = []
    iterative_columns: List[str] = []

    for column in numeric_columns:
        missing_ratio = float(df[column].isna().mean())
        if missing_ratio == 0:
            continue
        skewness = float(df[column].dropna().skew()) if df[column].dropna().shape[0] > 3 else 0.0
        has_relation = any(column in relation for relation in strong_relations)
        method = choose_numeric_imputation_method(missing_ratio, skewness, has_relation, len(numeric_columns), len(df))
        if method == 'mean':
            mean_columns.append(column)
        elif method == 'median':
            median_columns.append(column)
        elif method == 'knn':
            knn_columns.append(column)
        elif method == 'iterative':
            iterative_columns.append(column)
        log_entries.append({'column': str(column), 'type': 'numeric', 'missing_ratio': round(missing_ratio, 4), 'method': method, 'reason': {'missing_lt_5_percent': missing_ratio < 0.05, 'high_skew': abs(skewness) > 1.0, 'pattern_relation': has_relation}})

    return {'log_entries': log_entries, 'mean_columns': mean_columns, 'median_columns': median_columns, 'knn_columns': knn_columns, 'iterative_columns': iterative_columns}


def apply_simple_numeric_imputation(df: pd.DataFrame, mean_columns: List[str], median_columns: List[str]) -> None:
    for column in mean_columns:
        df[column] = df[column].fillna(df[column].mean())
    for column in median_columns:
        df[column] = df[column].fillna(df[column].median())


def apply_knn_numeric_imputation(df: pd.DataFrame, numeric_columns: List[str], knn_columns: List[str]) -> None:
    if not knn_columns or not SKLEARN_AVAILABLE:
        return
    numeric_matrix = df[numeric_columns].fillna(df[numeric_columns].median(numeric_only=True))
    imputer = KNNImputer(n_neighbors=5)
    df[numeric_columns] = imputer.fit_transform(numeric_matrix)


def apply_iterative_numeric_imputation(df: pd.DataFrame, numeric_columns: List[str], iterative_columns: List[str]) -> None:
    if not iterative_columns or not SKLEARN_AVAILABLE:
        return
    try:
        imputer = IterativeImputer(random_state=42, max_iter=10)
        df[numeric_columns] = imputer.fit_transform(df[numeric_columns])
    except Exception:
        return


def impute_text_columns(df: pd.DataFrame, text_columns: List[str]) -> List[Dict]:
    log_entries = []
    for column in text_columns:
        missing_ratio = float(df[column].isna().mean())
        if missing_ratio == 0:
            continue
        method = 'most_frequent' if missing_ratio < 0.35 else 'pattern_completion'
        series = df[column].astype('string').str.strip()
        mode_values = series.mode(dropna=True)
        fill_value = mode_values.iloc[0] if not mode_values.empty else 'Unknown'
        df[column] = series.fillna(fill_value)
        log_entries.append({'column': str(column), 'type': 'text', 'missing_ratio': round(missing_ratio, 4), 'method': method, 'reason': 'Most frequent value for sparse text or pattern completion fallback'})
    return log_entries


def adaptive_imputation(dataframe: pd.DataFrame, classification: Dict[str, List[str]], patterns: Dict) -> Tuple[pd.DataFrame, List[Dict]]:
    df = dataframe.copy()
    log_entries: List[Dict] = []
    numeric_columns = classification['numeric']
    text_columns = classification['text']
    strong_relations = extract_strong_relations(patterns)
    numeric_plan = build_numeric_imputation_plan(df, numeric_columns, strong_relations)
    log_entries.extend(numeric_plan['log_entries'])
    apply_simple_numeric_imputation(df, numeric_plan['mean_columns'], numeric_plan['median_columns'])
    apply_knn_numeric_imputation(df, numeric_columns, numeric_plan['knn_columns'])
    apply_iterative_numeric_imputation(df, numeric_columns, numeric_plan['iterative_columns'])
    log_entries.extend(impute_text_columns(df, text_columns))
    return df, log_entries


def noise_and_duplicate_removal(dataframe: pd.DataFrame, numeric_columns: List[str]) -> Tuple[pd.DataFrame, Dict]:
    df = dataframe.copy()
    initial_rows = len(df)
    outlier_mask = pd.Series(False, index=df.index)

    if numeric_columns:
        per_column_outlier = pd.DataFrame(False, index=df.index, columns=numeric_columns)
        for column in numeric_columns:
            series = df[column]
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            if pd.isna(iqr) or iqr == 0:
                continue
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            per_column_outlier[column] = (series < lower) | (series > upper)
        threshold = max(1, math.ceil(len(numeric_columns) * 0.35))
        outlier_mask = per_column_outlier.sum(axis=1) >= threshold

    completeness = 1.0 - df.isna().mean(axis=1)
    importance_proxy = 1.0 - (outlier_mask.astype(float) * 0.35)
    noise_ratio = outlier_mask.astype(float)
    final_score = (0.55 * completeness) + (0.35 * importance_proxy) - (0.2 * noise_ratio)
    keep_mask = final_score >= 0.45
    row_scores = [
        {'row_index': int(index), 'completeness': round(float(completeness.loc[index]), 4), 'importance': round(float(importance_proxy.loc[index]), 4), 'noise': round(float(noise_ratio.loc[index]), 4), 'final_score': round(float(final_score.loc[index]), 4), 'decision': 'keep' if bool(keep_mask.loc[index]) else 'remove'}
        for index in df.index[: min(120, len(df.index))]
    ]

    df = df[keep_mask].copy()
    outlier_removed = int(initial_rows - len(df))
    duplicate_before = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    duplicate_removed = duplicate_before
    return df, {'outlier_rows_removed': outlier_removed, 'duplicate_rows_removed': duplicate_removed, 'row_scoring_sample': row_scores}


def feature_importance(dataframe: pd.DataFrame, classification: Dict[str, List[str]]) -> Dict[str, float]:
    scores: Dict[str, float] = {}
    for column in dataframe.columns:
        series = dataframe[column]
        completeness = 1.0 - float(series.isna().mean())
        uniqueness = float(series.nunique(dropna=True) / max(len(series), 1))
        variance_component = 0.55
        if column in classification['numeric']:
            variance = float(series.var()) if pd.notna(series.var()) else 0.0
            variance_component = min(1.0, variance / (variance + 1.0))
        elif column in classification['text']:
            counts = series.astype('string').value_counts(normalize=True)
            entropy = float(-(counts * np.log2(counts + 1e-9)).sum()) if not counts.empty else 0.0
            variance_component = min(1.0, entropy / 6.0)
        score = (0.45 * completeness) + (0.35 * uniqueness) + (0.20 * variance_component)
        scores[str(column)] = round(float(score), 4)
    max_score = max(scores.values()) if scores else 1.0
    return {column: round(score / max_score, 4) for column, score in scores.items()}


def dataset_optimizer(dataframe: pd.DataFrame, feature_scores: Dict[str, float]) -> Tuple[pd.DataFrame, List[Dict]]:
    df = dataframe.copy()
    removed_columns = []
    for column in df.columns:
        missing_ratio = float(df[column].isna().mean())
        unique_count = int(df[column].nunique(dropna=True))
        score = feature_scores.get(str(column), 0.0)
        reasons = []
        if missing_ratio >= 0.8:
            reasons.append('high_missing_ratio')
        if unique_count <= 1:
            reasons.append('constant_column')
        if score < 0.08:
            reasons.append('low_feature_importance')
        if reasons:
            removed_columns.append({'column': str(column), 'reasons': reasons, 'missing_ratio': round(missing_ratio, 4), 'feature_importance': score})
    if removed_columns:
        df = df.drop(columns=[entry['column'] for entry in removed_columns], errors='ignore')
    return df, removed_columns


def recommended_model_input(dataframe: pd.DataFrame, classification: Dict[str, List[str]]) -> pd.DataFrame:
    model_df = dataframe.copy()
    for column in classification['text']:
        if column in model_df.columns:
            encoded, _ = pd.factorize(model_df[column].astype('string'), sort=True)
            model_df[column] = encoded
    import warnings
    for column in classification['datetime']:
        if column in model_df.columns:
            # parse robustly and convert to epoch seconds; keep NaT as 0
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=UserWarning)
                parsed = pd.to_datetime(model_df[column], errors='coerce')
            def _to_epoch(x):
                try:
                    return int(x.timestamp()) if not pd.isna(x) else 0
                except Exception:
                    return 0
            timestamps = parsed.apply(_to_epoch).astype('int64')
            model_df[column] = timestamps
    for column in model_df.select_dtypes(include=['number']).columns:
        series = model_df[column]
        std = float(series.std()) if pd.notna(series.std()) else 0.0
        if std > 0:
            model_df[column] = (series - series.mean()) / std
    return model_df


def write_pdf_report(path: str, summary_lines: List[str], title: str = 'Database Accelerator - Quality Report') -> None:
    width, height = 1240, 1754
    image = Image.new('RGB', (width, height), color=(18, 25, 42))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.rectangle((40, 40, width - 40, height - 40), outline=(97, 145, 255), width=3)
    y = 80
    draw.text((70, y), title, fill=(235, 243, 255), font=font)
    y += 45
    for line in summary_lines:
        draw.text((70, y), line, fill=(198, 214, 236), font=font)
        y += 28
    image.save(path, 'PDF', resolution=100.0)


def write_feature_summary(path: str, feature_scores: Dict[str, float], removed_columns: List[Dict]) -> None:
    lines = ['Feature Importance Summary', '==========================', '']
    ranked = sorted(feature_scores.items(), key=lambda item: item[1], reverse=True)
    for index, (column, score) in enumerate(ranked, start=1):
        lines.append(f'{index}. {column}: {score}')
    lines.extend(['', 'Removed Columns', '---------------'])
    if not removed_columns:
        lines.append('None')
    else:
        for item in removed_columns:
            lines.append(f"- {item['column']}: {', '.join(item['reasons'])}")
    with open(path, 'w', encoding='utf-8') as summary_file:
        summary_file.write('\n'.join(lines))
