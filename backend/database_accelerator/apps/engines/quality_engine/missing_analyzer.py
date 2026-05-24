from ..shared import quality_analysis


def analyze_missingness(dataframe, numeric_columns):
    return quality_analysis(dataframe, numeric_columns)
