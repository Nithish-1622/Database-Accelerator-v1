import pandas as pd


def detect_duplicates(dataframe: pd.DataFrame) -> dict:
    return {
        'duplicate_rows': int(dataframe.duplicated().sum()),
        'duplicate_rate': round(float(dataframe.duplicated().mean()) * 100, 2) if len(dataframe) else 0.0,
    }
