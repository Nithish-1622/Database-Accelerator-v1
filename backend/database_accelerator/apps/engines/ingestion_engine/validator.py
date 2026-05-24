import pandas as pd


def validate_dataframe(dataframe: pd.DataFrame) -> dict:
    return {
        'rows': int(dataframe.shape[0]),
        'columns': int(dataframe.shape[1]),
        'has_data': bool(len(dataframe) > 0 and len(dataframe.columns) > 0),
        'duplicate_rows': int(dataframe.duplicated().sum()),
    }
