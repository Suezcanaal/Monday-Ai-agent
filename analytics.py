import pandas as pd

def ad_hoc_analysis(df, dimension=None, metric="count"):
    """
    Performs dynamic analysis based on the user's query intent.
    
    Args:
        df: The dataframe
        dimension: Column to group by (e.g., 'Status', 'Group', 'Owner')
        metric: 'count' or 'sum' (for Value)
    """
    if df.empty:
        return {"error": "Dataframe is empty."}

    # Default to Status if no dimension found or if dimension is invalid
    if not dimension or dimension not in df.columns:
        # Fallback logic: prefer Status, then Group, then Item
        if "Status" in df.columns:
            dimension = "Status"
        elif "Group" in df.columns:
            dimension = "Group"
        else:
            dimension = "Item"

    # If we still can't find the column, return error
    if dimension not in df.columns:
        return {"error": f"Could not group by '{dimension}'. Column not found."}

    # Dynamic Grouping
    try:
        if metric == "sum" and "Value" in df.columns:
            # Summing Value (Revenue, Budget)
            # Ensure Value is numeric before summing
            df["Value"] = pd.to_numeric(df["Value"], errors='coerce').fillna(0)
            result = df.groupby(dimension)["Value"].sum().sort_values(ascending=False)
            # Format as currency
            formatted_result = result.apply(lambda x: f"${x:,.0f}")
        else:
            # Counting Items (Work Orders, Tasks)
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