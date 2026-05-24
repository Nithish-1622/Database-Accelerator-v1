from ..shared import build_numeric_imputation_plan, extract_strong_relations


def select_strategies(dataframe, classification, patterns):
    strong_relations = extract_strong_relations(patterns)
    return build_numeric_imputation_plan(dataframe, classification['numeric'], strong_relations)
