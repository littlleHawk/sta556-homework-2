""" 3 Functions

Suggested examples:
def clean_columns(data):
...
def filter_records(data):
...
def summarize_group(data, group_col):
...
Requirements:
1
• each function has a clear purpose;
• avoid unnecessary global variables;
• return objects rather than relying only on print;
• use sensible names and docstrings"""

import re

import numpy as np
import pandas as pd

# Calendar quarters covered by every label that is not already a plain "Qn YYYY".
# Fiscal-year labels are mapped to calendar quarters using the months in their brackets.
# Edit a line here if you disagree with how a label was read.
TIME_PD_TO_QTR_MAPPING = {
    # calendar halves, 9 months, full years
    "H1 2026": ["Q1 2026", "Q2 2026"],
    "FY2026":  ["Q1 2026", "Q2 2026", "Q3 2026", "Q4 2026"],
    "9M 2025": ["Q1 2025", "Q2 2025", "Q3 2025"],
    "H2 2025": ["Q3 2025", "Q4 2025"],
    "H1 2025": ["Q1 2025", "Q2 2025"],
    "FY2025":  ["Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"],
    "9M 2024": ["Q1 2024", "Q2 2024", "Q3 2024"],
    "H2 2024": ["Q3 2024", "Q4 2024"],
    "H1 2024": ["Q1 2024", "Q2 2024"],
    "FY2024":  ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"],
    "9M 2023": ["Q1 2023", "Q2 2023", "Q3 2023"],
    "H2 2023": ["Q3 2023", "Q4 2023"],
    "H1 2023": ["Q1 2023", "Q2 2023"],
    "FY2023":  ["Q1 2023", "Q2 2023", "Q3 2023", "Q4 2023"],
    "FY2022":  ["Q1 2022", "Q2 2022", "Q3 2022", "Q4 2022"],
    "FY2021":  ["Q1 2021", "Q2 2021", "Q3 2021", "Q4 2021"],
    "FY2020":  ["Q1 2020", "Q2 2020", "Q3 2020", "Q4 2020"],

    # 7 months (Jan-Jul), split evenly across the 3 quarters it touches
    "7M 2026": ["Q1 2026", "Q2 2026", "Q3 2026"],
    "7M 2025": ["Q1 2025", "Q2 2025", "Q3 2025"],

    # fiscal labels with months given
    "H1 FY2027 (Apr-Sep 2026)":       ["Q2 2026", "Q3 2026"],
    "H1 FY2026 (Apr-Sep 2025)":       ["Q2 2025", "Q3 2025"],
    "H1 FY2025 (Apr-Sep 2024)":       ["Q2 2024", "Q3 2024"],
    "9M FY2026 (Apr-Dec 2025)":       ["Q2 2025", "Q3 2025", "Q4 2025"],
    "9M FY2025 (Apr-Dec 2024)":       ["Q2 2024", "Q3 2024", "Q4 2024"],
    "9M FY2023 (Apr-Dec 2022)":       ["Q2 2022", "Q3 2022", "Q4 2022"],
    "9M FY2022 (Apr-Dec 2021)":       ["Q2 2021", "Q3 2021", "Q4 2021"],
    "H1 FY2025 (Oct-Mar 2025)":       ["Q4 2024", "Q1 2025"],
    "H1 FY2025 (Oct 2024-Mar 2025)":  ["Q4 2024", "Q1 2025"],
    "H1 FY2026 (Oct 2025-Mar 2026)":  ["Q4 2025", "Q1 2026"],
    "9M FY2026 (Oct 2025-Jun 2026)":  ["Q4 2025", "Q1 2026", "Q2 2026"],
    "9M FY2025 (Oct 2024-Jun 2025)":  ["Q4 2024", "Q1 2025", "Q2 2025"],
    "9M FY2024 (Oct 2023-Jun 2024)":  ["Q4 2023", "Q1 2024", "Q2 2024"],
    "9M FY2026 (Jul 2025-Mar 2026)":  ["Q3 2025", "Q4 2025", "Q1 2026"],
    "9M FY2025 (Jul-Mar 2025)":       ["Q3 2024", "Q4 2024", "Q1 2025"],
    "HY2026 (Jul-Dec 2025)":          ["Q3 2025", "Q4 2025"],

    # fiscal labels with no months: assumed to follow the calendar year
    "H1 FY2025": ["Q1 2025", "Q2 2025"],
    "9M FY2026": ["Q1 2026", "Q2 2026", "Q3 2026"],

    # single months and 2M (Jan-Feb): all inside one quarter, so not split
    "January 2026": ["Q1 2026"],  "January 2025": ["Q1 2025"],
    "Feb 2026":     ["Q1 2026"],  "Feb 2025":     ["Q1 2025"],
    "2M 2026":      ["Q1 2026"],  "2M 2025":      ["Q1 2025"],
    "Jun 2026":     ["Q2 2026"],  "Jun 2025":     ["Q2 2025"],
    "July 2026":    ["Q3 2026"],  "July 2025":    ["Q3 2025"],
    "Sep 2024":     ["Q3 2024"],  "Sep 2023":     ["Q3 2023"],
    "October 2024": ["Q4 2024"],  "October 2023": ["Q4 2023"],
}

def homogenize_time_periods_and_split_values(df:pd.DataFrame, period_col_name:str, value_cols:list[str]):
    """Reads in the time period data in dataframe and turns time periods into quarters.
    Relies on the ``TIME_PD_TO_QTR_MAPPING`` mapping in ``utils.py``. Rows with a time period
    not in the mappig and which are not already in a Q# YYYY format are dropped. 
    """
    return_df = df.copy(deep=True)
    # use the _map_quarters helper function to decide which new value shild be saved as the quarter
    # based on the current time period value
    return_df["quarter"] = return_df[period_col_name].map(_map_quarters)
    # Drop NAs (rows that did not get mapped)
    return_df = return_df[return_df["quarter"].notna()]
    # Count how many splits resulted from that mapping
    n_splits = return_df["quarter"].map(len).to_numpy()
    # Divide the value column among those splits
    for c in value_cols:
        return_df[c] = return_df[c].to_numpy() / n_splits
    return_df = return_df.explode("quarter", ignore_index=True)
    # Add a year column
    return_df["year"] = return_df["quarter"].str[-4:].astype(int)
    return return_df



def _map_quarters(label):
    label = str(label)
    # Return matched label in the mapping
    if label in TIME_PD_TO_QTR_MAPPING:
        return TIME_PD_TO_QTR_MAPPING[label]
    # Match Q# YYYY values (not in mapping)
    if re.fullmatch(r"Q[1-4] \d{4}", label):
        return [label]
    # Otherwise, drop the row
    return None

def apply_extraction_units(df:pd.DataFrame, output_col_name:str, units_col: str, val_col_name:str):
    "Converts value (amount of the commodity extracted) to kilograms for one-to-one comparison"
    unit_to_kg = {
    "kt": 1_000_000,
    "kcts": 0.2,          # thousand carats
    "koz": 31.1034768,    # thousand troy ounces
    }
    df[output_col_name] = df[val_col_name] * df[units_col].map(unit_to_kg)

    return df

def log_transform(df:pd.DataFrame, transform_col: str, output_col_name:str):
    """Accepts a dataframa and adds a column that is the log transform of that column.
    If the column in not numeric, raise a warning and return the original df.
    Also drops rows with 0 or less as the value because log(0) = -inf"""

    df_out = df
    # As of now, float is the only data type I use this transform on,
    # could be expanded to include ints
    if df[transform_col].dtypes != "float64":
        raise UserWarning(f"Column {transform_col} is not a numeric data type. Returning original dataframe\n")
    else:
        df_out = df.dropna().copy()
        df_out = df_out[df_out[transform_col] > 0].copy() # filter out zeroes and negatives
        df_out[output_col_name] = np.log(df_out[transform_col])
    return df_out

