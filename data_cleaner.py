import pandas as pd
import numpy as np

def clean_deals(df):
    if df.empty:
        return df

    # 1. Standardize Column Headers
    df.columns = df.columns.str.strip()
    
    # 2. Rename Logic (Robust Mappings)
    mapping = {
        "Name": "Deal",              # From Monday API
        "Deal Name": "Deal",         # From your Screenshot
        "Owner code": "Owner",
        "Client Code": "Client",
        "Deal Status": "Status",
        "Close Date (A)": "Actual_Close",
        "Closure Probability": "Probability_Label", 
        "Masked Deal value": "Value",
        "Tentative Close Date": "Target_Close",
        "Deal Stage": "Stage",
        "Product deal": "Product",
        "Sector/service": "Sector",
        "Created Date": "Created_At"
    }
    
    df = df.rename(columns=mapping)

    # 3. Numeric Conversions
    if "Value" in df.columns:
        df["Value"] = df["Value"].astype(str).str.replace(r'[$,]', '', regex=True)
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce").fillna(0)

    # 4. Probability Mapping
    if "Probability_Label" in df.columns:
        prob_map = {
            "high": 0.80,
            "medium": 0.50,
            "low": 0.20,
            "won": 1.00,
            "lost": 0.00
        }
        df["Probability_Score"] = df["Probability_Label"].astype(str).str.lower().map(prob_map).fillna(0.1)
        
        # Calculate Weighted Value
        if "Value" in df.columns:
            df["Weighted_Value"] = df["Value"] * df["Probability_Score"]

    # 5. Date Parsing (Fixed for Mixed Formats)
    date_cols = ["Actual_Close", "Target_Close", "Created_At"]
    for col in date_cols:
        if col in df.columns:
            # format='mixed' handles ISO (YYYY-MM-DD) and European (DD-MM-YYYY) together
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True, format="mixed")

    # 6. Text Normalization
    text_cols = ["Status", "Stage", "Sector", "Owner", "Product"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df