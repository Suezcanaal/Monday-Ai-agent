import pandas as pd
from datetime import datetime

def ad_hoc_analysis(df, dimension=None, metric="count"):
    """
    Performs dynamic analysis based on the user's query intent.
    """
    if df.empty:
        return {"error": "Dataframe is empty."}

    # Default to Status if no dimension found or if dimension is invalid
    if not dimension or dimension not in df.columns:
        if "Status" in df.columns:
            dimension = "Status"
        elif "Group" in df.columns:
            dimension = "Group"
        else:
            dimension = "Item"

    if dimension not in df.columns:
        return {"error": f"Could not group by '{dimension}'. Column not found."}

    try:
        if metric == "sum" and "Value" in df.columns:
            # Ensure Value is numeric before summing
            df["Value"] = pd.to_numeric(df["Value"], errors='coerce').fillna(0)
            result = df.groupby(dimension)["Value"].sum().sort_values(ascending=False)
            formatted_result = result.apply(lambda x: f"${x:,.0f}")
        else:
            result = df[dimension].value_counts()
            formatted_result = result
            
        return {
            "data": result,
            "formatted": formatted_result,
            "dimension": dimension,
            "metric": metric
        }
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

def analyze_delays(df, threshold_days=30):
    """
    Identifies deals that are delayed/overdue.
    """
    if df.empty:
        return {"error": "No data to analyze."}

    # 1. Check for Date column (Mapped as 'Date')
    if "Date" not in df.columns:
        return {"error": "Cannot calculate delay: Target Date column is missing."}

    today = pd.Timestamp.now()
    
    # 2. Handle Missing Dates
    # We create a copy to avoid SettingWithCopy warnings
    df_clean = df.copy()
    
    # Coerce dates just in case
    df_clean["Date"] = pd.to_datetime(df_clean["Date"], errors="coerce", dayfirst=True)
    
    missing_mask = df_clean["Date"].isna()
    missing_count = missing_mask.sum()
    
    # Filter to valid dates
    valid_df = df_clean[~missing_mask].copy()

    if valid_df.empty:
         return {
            "delayed_count": 0,
            "missing_date_count": missing_count,
            "delayed_items": pd.DataFrame()
        }

    # 3. Calculate Overdue
    valid_df["Days_Overdue"] = (today - valid_df["Date"]).dt.days
    
    # 4. Filter > Threshold
    delayed_df = valid_df[valid_df["Days_Overdue"] > threshold_days].sort_values(by="Days_Overdue", ascending=False)
    
    # Optional: Remove "Done" items
    if "Status" in delayed_df.columns:
        done_statuses = ["done", "won", "closed", "completed", "paid", "billed"]
        delayed_df = delayed_df[~delayed_df["Status"].astype(str).str.lower().isin(done_statuses)]

    return {
        "delayed_count": len(delayed_df),
        "missing_date_count": missing_count,
        "delayed_items": delayed_df[["Item", "Status", "Date", "Days_Overdue", "Owner"]] if not delayed_df.empty else pd.DataFrame()
    }