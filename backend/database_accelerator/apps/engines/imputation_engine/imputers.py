from ..shared import apply_iterative_numeric_imputation, apply_knn_numeric_imputation, apply_simple_numeric_imputation, adaptive_imputation


def apply_imputation(dataframe, classification, patterns):
    return adaptive_imputation(dataframe, classification, patterns)
