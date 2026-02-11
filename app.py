import streamlit as st
import re
from connection_manager import monday_manager
from monday_api import fetch_board_data
from data_cleaner import clean_data
import analytics  # <--- THIS IMPORT FIXES YOUR ERROR
from config import BOARD_CONFIG, get_board_id

st.set_page_config(page_title="Enterprise BI Agent", layout="wide")

st.title("🤖 Monday.com Enterprise BI Agent")

# Sidebar
with st.sidebar:
    st.header("🔌 Connection")
    if not monday_manager.is_connected:
        success, msg = monday_manager.connect()
        if success:
            st.success("Connected")
        else:
            st.error(msg)
    else:
        st.success("System Online")
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "I can analyze your **Sales Pipeline** and **Work Orders**. Try asking:\n- *Show me revenue by Sector*\n- *Which Work Orders are completed?*\n- *Show me overdue items*"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])
    if "data" in msg and msg["data"] is not None:
        st.dataframe(msg["data"])

# Input Logic
if prompt := st.chat_input("Ask about deals, execution, or delays..."):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            
            # 1. ROUTING LOGIC (Board Selection)
            prompt_lower = prompt.lower()
            selected_board_key = None
            
            for key, config in BOARD_CONFIG.items():
                if any(k in prompt_lower for k in config["keywords"]):
                    selected_board_key = key
                    break
            
            if not selected_board_key:
                selected_board_key = "deals"

            board_conf = BOARD_CONFIG[selected_board_key]
            board_id = get_board_id(board_conf["env_var"])

            if not board_id:
                response = f"⚠ **Configuration Error:** Board ID for '{board_conf['name']}' not found."
                st.write(response)
            else:
                # 2. FETCH DATA
                raw_df = fetch_board_data(board_id)

                if raw_df.empty:
                    response = f"I connected to **{board_conf['name']}**, but found no data."
                    st.write(response)
                else:
                    # 3. CLEANING
                    df = clean_data(raw_df, mapping_config=board_conf["columns"])

                    # 4. ANALYSIS ROUTER
                    
                    # --- A. DELAY ANALYSIS ---
                    if any(x in prompt_lower for x in ["delay", "overdue", "late", "stuck"]):
                        # Extract number of days (default 30)
                        threshold = 30
                        numbers = re.findall(r'\d+', prompt)
                        if numbers:
                            threshold = int(numbers[0])

                        result = analytics.analyze_delays(df, threshold_days=threshold)
                        
                        if "error" in result:
                            response = f"⚠ {result['error']}"
                            data_to_show = None
                        else:
                            count = result['delayed_count']
                            missing = result['missing_date_count']
                            
                            response = f"### ⏳ Delay Analysis (> {threshold} days)\n"
                            response += f"Found **{count} items** that are overdue.\n"
                            
                            if count > 0:
                                top_delay = result['delayed_items'].iloc[0]
                                response += f"**Most Delayed:** '{top_delay['Item']}' ({int(top_delay['Days_Overdue'])} days).\n"
                            
                            if missing > 0:
                                response += f"\n⚠ **Note:** {missing} items ignored (missing dates)."
                            
                            data_to_show = result['delayed_items'] if count > 0 else None

                    # --- B. STANDARD AD-HOC ANALYSIS ---
                    else:
                        metric = "sum" if any(x in prompt_lower for x in ["value", "revenue", "amount", "budget"]) else "count"
                        
                        dimension = "Status"
                        if "owner" in prompt_lower or "personnel" in prompt_lower: dimension = "Owner"
                        if "sector" in prompt_lower or "group" in prompt_lower: dimension = "Group"
                        if "stage" in prompt_lower: dimension = "Stage"
                        if "item" in prompt_lower or "name" in prompt_lower: dimension = "Item"

                        result = analytics.ad_hoc_analysis(df, dimension, metric)

                        if "error" in result:
                            response = f"⚠ {result['error']}"
                            data_to_show = None
                        else:
                            top_cat = result['formatted'].index[0]
                            top_val = result['formatted'].iloc[0]
                            
                            response = f"### 📂 Source: {board_conf['name']}\n"
                            response += f"Breaking down **{metric}** by **{dimension}**:\n\n"
                            response += f"**Top Result:** '{top_cat}' with {top_val}.\n"
                            data_to_show = result['formatted']

                    # 5. DISPLAY
                    st.markdown(response)
                    if data_to_show is not None:
                        st.dataframe(data_to_show)
                    
                    st.session_state.messages.append({"role": "assistant", "content": response, "data": data_to_show})