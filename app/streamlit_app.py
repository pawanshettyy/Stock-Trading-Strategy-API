import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# FastAPI backend URL
BASE_URL = "http://127.0.0.1:8000"  # Update if needed

st.title("📈 Stock Trading Strategy Dashboard By Pawan Shetty")

# Sidebar navigation
st.sidebar.header("📌 Navigation")
option = st.sidebar.selectbox("Choose:", ["🏠 Home", "📊 View Ticker Data", "📉 Run Moving Average Strategy"])

if option == "🏠 Home":
    st.markdown("## Welcome to the Stock Trading Strategy Dashboard! 🚀")
    st.write("Navigate using the sidebar to analyze stocks and strategies.")

elif option == "📊 View Ticker Data":
    st.subheader("📈 Ticker Data")
    ticker = st.text_input("Enter Ticker Symbol", "HINDALCO")
    if st.button("🔍 Fetch Data"):
        response = requests.get(f"{BASE_URL}/data/?ticker_symbol={ticker}")
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)  # Convert to DataFrame for better display
            st.write(df)
        else:
            st.error("❌ Failed to fetch data. Check API.")

elif option == "📉 Run Moving Average Strategy":
    st.subheader("📊 Moving Average Crossover Strategy")
    
    ticker = st.text_input("Enter Ticker Symbol", "HINDALCO")
    short_window = st.number_input("Short Window", min_value=1, value=5)
    long_window = st.number_input("Long Window", min_value=2, value=20)
    
    if st.button("🚀 Run Strategy"):
        params = {"ticker_symbol": ticker, "short_window": short_window, "long_window": long_window}
        response = requests.get(f"{BASE_URL}/strategy/performance", params=params)
        
        if response.status_code == 200:
            result = response.json()
            
            # Display Strategy Results
            st.write("### Strategy Performance")
            st.write(f"**Ticker Symbol:** {result['ticker_symbol']}")
            st.write(f"**Total Trades:** {result['total_trades']}")
            st.write(f"**Winning Trades:** {result['winning_trades']}")
            st.write(f"**Losing Trades:** {result['losing_trades']}")
            st.write(f"**Net Profit/Loss:** ${result['profit_loss']:.2f}")

            # Convert signals to DataFrame
            if "signals" in result and result["signals"]:
                signals_df = pd.DataFrame(result["signals"])
                st.write("### Trade Signals")
                st.write(signals_df)

                # Plot the Moving Averages & Signals
                st.write("### 📈 Moving Averages Chart")
                fig, ax = plt.subplots(figsize=(10, 5))
                
                ax.plot(signals_df["timestamp"], signals_df["short_ma"], label=f"Short MA ({short_window})", color='blue')
                ax.plot(signals_df["timestamp"], signals_df["long_ma"], label=f"Long MA ({long_window})", color='red')
                ax.scatter(signals_df["timestamp"], signals_df["buy_signal"], label="Buy Signal", marker='^', color='green')
                ax.scatter(signals_df["timestamp"], signals_df["sell_signal"], label="Sell Signal", marker='v', color='red')
                
                ax.legend()
                ax.set_xlabel("Date")
                ax.set_ylabel("Price")
                ax.set_title(f"Moving Average Crossover - {ticker}")
                
                st.pyplot(fig)  # Display the plot
        else:
            st.error("❌ Failed to fetch strategy performance")
