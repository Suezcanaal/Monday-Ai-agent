import pandas as pd
import numpy as np

def clean_data(df, mapping_config=None):
    """
    Cleans data based on the specific board configuration.
    """
    if df.empty:
        return df

    # 1. Clean Headers (Strip whitespace)
    df.columns = df.columns.str.strip()
    
    # 2. Apply Specific Mapping (if provided)
    if mapping_config:
        # We only rename columns that actually exist in the dataframe
        # This prevents errors if Monday API changes slightly
        valid_map = {k: v for k, v in mapping_config.items() if k in df.columns}
        df = df.rename(columns=valid_map)
    
    # 3. Handle Missing Core Columns (Resilience)
    # If mapping failed or column missing, ensure we have defaults
    required_cols = ["Item", "Status", "Value", "Group", "Owner"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = "Unknown" # Placeholder to prevent crash

    # 4. Text Cleaning
    text_cols = ["Item", "Status", "Group", "Owner", "Stage"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace("nan", "Unknown")

    # 5. Numeric Cleaning
    if "Value" in df.columns:
        # Handle "489360" or "264,398.08" format
        df["Value"] = df["Value"].astype(str).str.replace(r'[$,]', '', regex=True)
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce").fillna(0)

    # 6. Date Cleaning (DD-MM-YYYY format from your screenshots)
    if "Date" in df.columns:
        # dayfirst=True is CRITICAL for dates like 26-02-2026
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True, format="mixed")

    return df