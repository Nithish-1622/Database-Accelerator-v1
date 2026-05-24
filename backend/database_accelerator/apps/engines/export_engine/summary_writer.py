from ..shared import write_feature_summary


def export_summary(path, feature_scores, removed_columns):
    write_feature_summary(path, feature_scores, removed_columns)
    return path
