from ..shared import pattern_discovery


def build_correlation_report(dataframe, numeric_columns):
    return pattern_discovery(dataframe, numeric_columns)
