from ..shared import recommended_model_input


def build_model_input(dataframe, classification):
    return recommended_model_input(dataframe, classification)
