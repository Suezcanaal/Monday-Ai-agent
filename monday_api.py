import pandas as pd
from connection_manager import monday_manager

def fetch_board_data(board_id):
    """
    Generic fetcher that works for ANY Monday.com board.
    """
    if not board_id:
        raise Exception("No Board ID provided.")

    if not monday_manager.is_connected:
        monday_manager.connect()

    # Query 500 items from the specific board ID
    query = f"""
    query {{
      boards(ids: {board_id}) {{
        name
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
        return pd.DataFrame()

    try:
        # Check if board data exists
        if not data["data"]["boards"]:
            return pd.DataFrame()
            
        board_data = data["data"]["boards"][0]
        items = board_data["items_page"]["items"]
    except (KeyError, IndexError, TypeError):
        return pd.DataFrame()

    rows = []
    for item in items:
        row = {"Name": item["name"]}
        for col in item["column_values"]:
            # Ensure column title exists before adding
            if col.get("column") and col["column"].get("title"):
                row[col["column"]["title"]] = col["text"]
        rows.append(row)

    return pd.DataFrame(rows)