import pandas as pd

def get_portfolio_metrics(df):
    """Calculates high-level portfolio health metrics."""
    total_pipeline = df["Value"].sum()
    
    weighted_pipeline = df["Weighted_Value"].sum() if "Weighted_Value" in df.columns else 0
    
    avg_deal = df["Value"].mean()
    deal_count = len(df)
    
    return {
        "total_pipeline": total_pipeline,
        "weighted_pipeline": weighted_pipeline,
        "avg_deal_size": avg_deal,
        "deal_count": deal_count
    }

def get_sector_performance(df):
    """Groups data by Sector to compare performance."""
    if "Sector" not in df.columns:
        return None
        
    sector_stats = df.groupby("Sector").agg({
        "Value": "sum",
        "Weighted_Value": "sum" if "Weighted_Value" in df.columns else "sum",
        "Deal": "count"
    }).sort_values(by="Value", ascending=False)
    
    return sector_stats

def get_stage_distribution(df):
    """Analyzes where deals are getting stuck."""
    if "Stage" not in df.columns:
        return None
        
    stage_stats = df["Stage"].value_counts().sort_index()
    return stage_stats

def get_data_health(df):
    """Checks for data quality issues."""
    issues = []
    
    if df["Value"].sum() == 0:
        issues.append("⚠ Total pipeline value is 0. Check 'Masked Deal value' column.")
        
    if "Target_Close" in df.columns:
        missing_dates = df["Target_Close"].isna().sum()
        if missing_dates > 0:
            issues.append(f"⚠ {missing_dates} deals are missing a Target Close Date.")
        
    return issues