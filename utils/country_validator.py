"""
Country Validator Utility
Validates country names with fuzzy matching support.
"""

import pandas as pd
from difflib import get_close_matches

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COUNTRY_CSV = os.path.join(
    BASE_DIR,
    "Dataset",
    "Preprocessed",
    "Final_Clustered_Dataset.csv"
)


def get_all_countries():

    df = pd.read_csv(COUNTRY_CSV)

    countries = sorted(
        df['Country Name'].dropna().unique().tolist()
    )

    return countries


def validate_country(df: pd.DataFrame, country_name: str) -> tuple:
    """
    Validate if a country exists in the dataframe.
    Supports case-insensitive and partial matching.

    Returns:
        (bool, matched_name_or_None)
    """
    if not country_name or not isinstance(country_name, str):
        return False, None

    all_countries = df['Country Name'].dropna().unique().tolist()

    # Exact match (case-insensitive)
    country_lower = country_name.strip().lower()
    for c in all_countries:
        if c.strip().lower() == country_lower:
            return True, c

    # Partial match — starts with
    matches = [c for c in all_countries if c.strip().lower().startswith(country_lower)]
    if matches:
        return True, matches[0]

    # Fuzzy match
    close = get_close_matches(country_name.strip(), all_countries, n=1, cutoff=0.6)
    if close:
        return True, close[0]

    return False, None


# def get_all_countries(df: pd.DataFrame) -> list:
#     """Return sorted list of all unique country names."""
#     return sorted(df['Country Name'].dropna().unique().tolist())
