import os
import pandas as pd
from connection_manager import monday_manager
from dotenv import load_dotenv
import streamlit as st
load_dotenv()

def fetch_deals():
    """
    Fetches all items from the board defined in .env
    """
    # Try finding ID in .env (Local) OR Streamlit Secrets (Cloud)
    board_id = os.getenv("MONDAY_BOARD_ID")
    if not board_id and "MONDAY_BOARD_ID" in st.secrets:
        board_id = st.secrets["MONDAY_BOARD_ID"]

    if not board_id:
        raise Exception("Board ID not found.")
    
    if not monday_manager.is_connected:
        success, msg = monday_manager.connect()
        if not success:
            raise Exception(msg)

    board_id = os.getenv("MONDAY_BOARD_ID")
    if not board_id:
        raise Exception("Board ID not found in .env file.")

    query = f"""
    query {{
      boards(ids: {board_id}) {{
        items_page(limit: 500) {{
          items {{
            name
            column_values {{
              text
              column {{ title }}
            }}
          }}
        }}
      }}
    }}
    """

    data = monday_manager.execute_query(query)

    if 'errors' in data:
        raise Exception(f"Monday API Error: {data['errors']}")

    try:
        items = data["data"]["boards"][0]["items_page"]["items"]
    except (KeyError, IndexError, TypeError):
        return pd.DataFrame()

    rows = []
    for item in items:
        row = {"Name": item["name"]}
        for col in item["column_values"]:
            if col["column"]["title"]:
                row[col["column"]["title"]] = col["text"]
        rows.append(row)

    return pd.DataFrame(rows)