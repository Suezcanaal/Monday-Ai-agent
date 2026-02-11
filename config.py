import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_board_id(key):
    """
    Safely retrieves the Board ID from .env (Local) OR st.secrets (Cloud).
    """
    # 1. Try Local Environment Variable first (.env)
    # This prevents the crash because we don't touch st.secrets if we find it here.
    value = os.getenv(key)
    if value:
        return value

    # 2. Try Streamlit Secrets (Cloud)
    # We wrap this in a try-except block so it doesn't crash on your laptop
    try:
        if key in st.secrets:
            return st.secrets[key]
    except FileNotFoundError:
        # This error is expected locally if no secrets.toml exists
        pass
    except Exception:
        pass
        
    return None

# CONFIGURATION & MAPPINGS
BOARD_CONFIG = {
    "deals": {
        "name": "Sales Pipeline",
        "env_var": "MONDAY_BOARD_ID_DEALS",
        "keywords": ["pipeline", "sales", "deal", "revenue", "forecast", "close"],
        "type": "financial",
        # EXACT MAPPING from your Image 1
        "columns": {
            "Deal Name": "Item",
            "Owner code": "Owner",
            "Deal Status": "Status",
            "Masked Deal value": "Value",
            "Tentative Close Date": "Date",
            "Sector/service": "Group",
            "Deal Stage": "Stage",
            "Closure Probability": "Probability"
        }
    },
    "work_orders": {
        "name": "Work Orders",
        "env_var": "MONDAY_BOARD_ID_WORK_ORDERS",
        "keywords": ["work", "order", "execution", "project", "delivery", "operational"],
        "type": "operational",
        # EXACT MAPPING from your Image 4
        "columns": {
            "Deal name masked": "Item",
            "BD/KAM Personnel code": "Owner",
            "Execution Status": "Status", 
            "Amount in Rupees (Excl of GST) (Masked)": "Value", 
            "Probable End Date": "Date",
            "Sector": "Group",
            "Nature of Work": "Stage"
        }
    }
}