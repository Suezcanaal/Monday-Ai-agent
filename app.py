import streamlit as st
from connection_manager import monday_manager
from monday_api import fetch_board_data
from data_cleaner import clean_data
from analytics import ad_hoc_analysis
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
    st.session_state.messages = [{"role": "assistant", "content": "I can analyze your **Sales Pipeline** and **Work Orders**. Try asking:\n- *Show me revenue by Sector*\n- *Which Work Orders are completed?*"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])
    if "data" in msg and msg["data"] is not None:
        st.dataframe(msg["data"])

# Input Logic
if prompt := st.chat_input("Ask about deals, execution, or revenue..."):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            
            # 1. ROUTING LOGIC
            prompt_lower = prompt.lower()
            selected_board_key = None
            
            # Find which board config matches the user's keywords
            for key, config in BOARD_CONFIG.items():
                if any(k in prompt_lower for k in config["keywords"]):
                    selected_board_key = key
                    break
            
            # Default to 'deals' if no specific keyword found
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
                    response = f"I connected to **{board_conf['name']}**, but found no data. Check your Board ID."
                    st.write(response)
                else:
                    # 3. CLEANING (Pass the specific column map!)
                    df = clean_data(raw_df, mapping_config=board_conf["columns"])

                    # 4. ANALYSIS
                    # Detect Metric (Money vs Count)
                    metric = "sum" if any(x in prompt_lower for x in ["value", "revenue", "amount", "budget"]) else "count"
                    
                    # Detect Dimension (Grouping)
                    dimension = "Status" # Default
                    if "owner" in prompt_lower or "personnel" in prompt_lower: dimension = "Owner"
                    if "sector" in prompt_lower or "group" in prompt_lower: dimension = "Group"
                    if "stage" in prompt_lower: dimension = "Stage"
                    if "item" in prompt_lower or "name" in prompt_lower: dimension = "Item"

                    result = ad_hoc_analysis(df, dimension, metric)

                    # 5. GENERATE RESPONSE
                    if "error" in result:
                        response = f"⚠ {result['error']}"
                    else:
                        top_cat = result['formatted'].index[0]
                        top_val = result['formatted'].iloc[0]
                        
                        response = f"### 📂 Source: {board_conf['name']}\n"
                        response += f"Breaking down **{metric}** by **{dimension}**:\n\n"
                        response += f"**Top Result:** '{top_cat}' with {top_val}.\n"
                        
                        st.markdown(response)
                        st.dataframe(result['formatted'])
                        
                        # Save to history
                        st.session_state.messages.append({"role": "assistant", "content": response, "data": result['formatted']})