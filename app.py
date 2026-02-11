import streamlit as st
from connection_manager import monday_manager
from monday_api import fetch_deals
from data_cleaner import clean_deals
import analytics
import insight_generator

# Page Config
st.set_page_config(page_title="Monday.com Founder BI Agent", layout="wide")

st.title("🤖 Monday.com Founder BI Agent")

# --- INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am connected to your Monday.com board. Ask me about pipeline performance, sectors, or specific metrics.", "data": None}
    ]

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔌 System Status")
    if not monday_manager.is_connected:
        with st.spinner("Connecting..."):
            success, msg = monday_manager.connect()
            if success:
                st.success("System Online")
            else:
                st.error(msg)
    else:
        st.success("✅ System Online")
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

# --- CHAT INTERFACE ---

# 1. Display existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Check if there is a dataframe attached to this message and display it
        if message.get("data") is not None:
            st.dataframe(message["data"])

# 2. Handle User Input
if prompt := st.chat_input("Ask a question (e.g., 'How is the Mining pipeline?')..."):
    
    # User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt, "data": None})

    # Assistant Logic
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        extracted_data = None # This will hold the table we want to show

        if not monday_manager.is_connected:
            full_response = "⚠ Please check the connection in the sidebar first."
            message_placeholder.markdown(full_response)
        else:
            with st.spinner("Analyzing data..."):
                try:
                    # FETCH AND CLEAN
                    raw_df = fetch_deals()
                    df = clean_deals(raw_df)

                    if df.empty:
                        full_response = "I couldn't find any data on the board."
                    else:
                        # ANALYTICS LOGIC
                        sectors = analytics.get_sector_performance(df)
                        available_sectors = sectors.index.tolist() if sectors is not None else []
                        
                        prompt_lower = prompt.lower()
                        
                        # --- INTENT RECOGNITION ---
                        
                        # 1. Sector Specific
                        detected_sector = next((s for s in available_sectors if s.lower() in prompt_lower), None)
                        
                        if detected_sector:
                            # Filter data for this sector
                            sector_df = df[df["Sector"] == detected_sector]
                            metrics = {
                                "total_pipeline": sector_df["Value"].sum(),
                                "weighted_pipeline": sector_df["Weighted_Value"].sum() if "Weighted_Value" in sector_df.columns else 0,
                                "avg_deal_size": sector_df["Value"].mean(),
                                "deal_count": len(sector_df)
                            }
                            full_response = f"### 📊 Analysis for {detected_sector}\n"
                            full_response += f"**Pipeline:** ${metrics['total_pipeline']:,.0f} | **Deals:** {metrics['deal_count']}\n"
                            
                            if metrics['deal_count'] > 0:
                                full_response += f"\n- **Risk-Adjusted Forecast:** ${metrics['weighted_pipeline']:,.0f}"
                                full_response += f"\n- **Avg Deal Size:** ${metrics['avg_deal_size']:,.0f}"
                            
                            # ATTACH DATA: Show only the rows for this sector
                            extracted_data = sector_df

                        # 2. General Summary
                        elif any(x in prompt_lower for x in ["overview", "summary", "performance", "health"]):
                            portfolio = analytics.get_portfolio_metrics(df)
                            stage_dist = analytics.get_stage_distribution(df)
                            health = analytics.get_data_health(df)
                            full_response = insight_generator.generate_executive_summary(portfolio, sectors, stage_dist, health)
                            
                            # ATTACH DATA: Show the high-level Sector Performance table
                            extracted_data = sectors 

                        # 3. Greetings
                        elif any(x in prompt_lower for x in ["hello", "hi", "help"]):
                            full_response = "I can help you analyze your board. Try asking:\n- *Give me a portfolio summary*\n- *How is the Mining sector performing?*"

                        # 4. Fallback
                        else:
                            full_response = f"I didn't understand that specific query. Try asking for a **summary** or about a specific sector like: **{', '.join(available_sectors)}**."

                except Exception as e:
                    full_response = f"❌ An error occurred: {str(e)}"
        
        # Display Response
        message_placeholder.markdown(full_response)
        
        # Display Table if it exists
        if extracted_data is not None:
            st.dataframe(extracted_data)

        # Save to History
        st.session_state.messages.append({"role": "assistant", "content": full_response, "data": extracted_data})