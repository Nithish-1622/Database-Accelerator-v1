from ..shared import quality_analysis


def detect_outliers(dataframe, numeric_columns):
    return quality_analysis(dataframe, numeric_columns)
