"""
Data Loader Utility
Loads and caches historical and future development datasets.
"""

import pandas as pd
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configurable paths — update these to match your environment
HISTORICAL_CSV = os.path.join(
    BASE_DIR,
    "Dataset",
    "Preprocessed",
    "Final_Clustered_Dataset.csv"
)

MASTER_CSV = os.path.join(
    BASE_DIR,
    "Dataset",
    "Preprocessed",
    "Master_Development_Dataset.csv"
)

FUTURE_CSV = os.path.join(
    BASE_DIR,
    "Dataset",
    "Preprocessed",
    "Future_Development_Dataset_2025_2040.csv"
)

_hist_cache = None
_future_cache = None

_master_cache = None


def load_master_data():
    global _master_cache

    if _master_cache is not None:
        return _master_cache.copy()

    df = pd.read_csv(MASTER_CSV)

    df.columns = df.columns.str.strip()

    _master_cache = df

    return df.copy()


def load_historical_data() -> pd.DataFrame:
    """
    Load historical development dataset (2014–2024).
    Returns a cleaned DataFrame.
    """
    global _hist_cache
    if _hist_cache is not None:
        return _hist_cache.copy()

    if not os.path.exists(HISTORICAL_CSV):
        raise FileNotFoundError(
            f"Historical CSV not found at: {HISTORICAL_CSV}\n"
            "Please update the HISTORICAL_CSV path in utils/data_loader.py"
        )

    df = pd.read_csv(HISTORICAL_CSV)
    df = _clean_historical(df)
    _hist_cache = df
    return df.copy()


def load_future_data() -> pd.DataFrame:
    """
    Load future forecast dataset (2025–2040).
    Returns a cleaned DataFrame.
    """
    global _future_cache
    if _future_cache is not None:
        return _future_cache.copy()

    if not os.path.exists(FUTURE_CSV):
        raise FileNotFoundError(
            f"Future CSV not found at: {FUTURE_CSV}\n"
            "Please update the FUTURE_CSV path in utils/data_loader.py"
        )

    df = pd.read_csv(FUTURE_CSV)
    df = _clean_future(df)
    _future_cache = df
    return df.copy()


def _clean_historical(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize historical dataset."""
    df.columns = df.columns.str.strip()

    required_cols = ['Country Name', 'Year', 'Development_Score', 'Development_Level']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column in historical dataset: {col}")

    numeric_cols = ['GDP', 'Inflation', 'Internet_Users', 'Life_Expectancy',
                    'Literacy_Rate', 'Poverty', 'Unemployment', 'Development_Score']

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
    df['Country Name'] = df['Country Name'].str.strip()
    df['Development_Level'] = df['Development_Level'].str.strip()
    df = df.dropna(subset=['Country Name', 'Year'])
    return df.reset_index(drop=True)


def _clean_future(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize future forecast dataset."""
    df.columns = df.columns.str.strip()

    required_cols = ['Country Name', 'Year', 'GDP_Per_Capita', 'Development_Score', 'Development_Level']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column in future dataset: {col}")

    numeric_cols = ['GDP_Per_Capita', 'Development_Score']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
    df['Country Name'] = df['Country Name'].str.strip()
    df['Development_Level'] = df['Development_Level'].str.strip()
    df = df.dropna(subset=['Country Name', 'Year'])
    return df.reset_index(drop=True)


def get_future_development_level(future_df: pd.DataFrame, country: str, year: int) -> dict:
    """Get development info for a specific country and future year."""
    row = future_df[
        (future_df['Country Name'] == country) &
        (future_df['Year'] == year)
    ]
    if row.empty:
        return None
    r = row.iloc[0]
    return {
        'country': country,
        'year': int(year),
        'gdp_per_capita': round(float(r['GDP_Per_Capita']), 2),
        'development_score': round(float(r['Development_Score']), 2),
        'development_level': r['Development_Level']
    }
