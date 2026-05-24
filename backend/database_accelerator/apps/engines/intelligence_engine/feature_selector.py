from ..shared import feature_importance


def select_features(dataframe, classification):
    return feature_importance(dataframe, classification)
