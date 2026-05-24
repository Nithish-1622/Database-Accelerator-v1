from ..shared import build_mutual_information_pairs


def build_mutual_information_report(dataframe, numeric_columns):
    return build_mutual_information_pairs(dataframe, numeric_columns)
