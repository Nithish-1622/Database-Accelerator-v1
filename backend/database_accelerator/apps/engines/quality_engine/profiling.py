from ..shared import schema_detection


def build_profile(dataframe):
    return schema_detection(dataframe)
