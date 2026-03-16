from nselib import capital_market
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(page_title="NSE Dashboard", page_icon="📈", layout="wide")

# Title
st.title('📊 Indian Stock Market Dashboard 2026')
st.markdown("---")

# Sidebar navigation
page = st.sidebar.radio(
    "Navigation",
    ["📈 Market Overview", "🔍 Stock Search", "📊 Technical Analysis", "💹 Market Indices"]
)

# ==================== PAGE 1: MARKET OVERVIEW ====================
if page == "📈 Market Overview":
    st.header("Market Overview")
    
    try:
        # Get market status
        market_status = capital_market.market_status()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Market Status", value=market_status.get('status', 'N/A'))
        with col2:
            st.metric(label="Current Time", value=datetime.now().strftime("%H:%M:%S"))
        with col3:
            st.metric(label="Last Update", value=datetime.now().strftime("%Y-%m-%d"))
        
        st.success("✅ Market is Open")
    except Exception as e:
        st.error(f"Error fetching market status: {str(e)}")
    
    st.markdown("---")
    
    # Top gainers and losers
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 Top Gainers")
        try:
            gainers = capital_market.top_gainers()
            if gainers:
                gainers_df = pd.DataFrame(gainers[:5])
                st.dataframe(gainers_df, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not fetch gainers: {str(e)}")
    
    with col2:
        st.subheader("📉 Top Losers")
        try:
            losers = capital_market.top_losers()
            if losers:
                losers_df = pd.DataFrame(losers[:5])
                st.dataframe(losers_df, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not fetch losers: {str(e)}")


# ==================== PAGE 2: STOCK SEARCH ====================
elif page == "🔍 Stock Search":
    st.header("Stock Search & Analysis")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        stock_symbol = st.text_input("Enter Stock Symbol (e.g., INFY, TCS, RELIANCE):", placeholder="INFY").upper()
    with col2:
        search_btn = st.button("🔍 Search", use_container_width=True)
    
    if search_btn and stock_symbol:
        try:
            # Get quote data
            quote = capital_market.quote(stock_symbol)
            
            if quote:
                st.subheader(f"{stock_symbol} - {quote.get('companyName', 'Unknown')}")
                
                # Display key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    price = quote.get('lastPrice', 0)
                    st.metric("Current Price", f"₹{price:.2f}")
                
                with col2:
                    change = quote.get('change', 0)
                    st.metric("Change", f"₹{change:.2f}")
                
                with col3:
                    pChange = quote.get('pChange', 0)
                    st.metric("% Change", f"{pChange:.2f}%")
                
                with col4:
                    pe = quote.get('pe', 'N/A')
                    st.metric("P/E Ratio", pe)
                
                st.markdown("---")
                
                # Stock details table
                st.subheader("Stock Details")
                details_data = {
                    "Metric": ["Open Price", "Day High", "Day Low", "52 Week High", "52 Week Low", "Volume", "Market Cap"],
                    "Value": [
                        f"₹{quote.get('open', 0):.2f}",
                        f"₹{quote.get('dayHigh', 0):.2f}",
                        f"₹{quote.get('dayLow', 0):.2f}",
                        f"₹{quote.get('ytHigh', 0):.2f}",
                        f"₹{quote.get('ytLow', 0):.2f}",
                        f"{quote.get('lastTradedQuantity', 0):,}",
                        f"{quote.get('marketCap', 'N/A')}"
                    ]
                }
                st.dataframe(pd.DataFrame(details_data), use_container_width=True, hide_index=True)
            else:
                st.error("Stock symbol not found. Please check and try again.")
                
        except Exception as e:
            st.error(f"Error fetching stock data: {str(e)}")


# ==================== PAGE 3: TECHNICAL ANALYSIS ====================
elif page == "📊 Technical Analysis":
    st.header("Technical Analysis")
    
    st.info("💡 This section demonstrates technical analysis concepts. For live chart data, integrate with a real-time data provider.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        stock_symbol = st.text_input("Enter Stock Symbol for Technical Analysis:", placeholder="INFY").upper()
    with col2:
        analyze_btn = st.button("Analyze", use_container_width=True)
    
    if analyze_btn and stock_symbol:
        try:
            quote = capital_market.quote(stock_symbol)
            
            if quote:
                st.subheader(f"{stock_symbol} Technical Indicators")
                
                # Simulate price movement data for demonstration
                np.random.seed(42)
                days = 60
                dates = pd.date_range(end=datetime.now(), periods=days)
                base_price = quote.get('lastPrice', 100)
                prices = base_price + np.cumsum(np.random.randn(days) * 2)
                
                df = pd.DataFrame({
                    'Date': dates,
                    'Price': prices
                })
                
                # Calculate moving averages
                df['MA_20'] = df['Price'].rolling(window=20).mean()
                df['MA_50'] = df['Price'].rolling(window=50).mean()
                
                # Create chart
                chart = alt.Chart(df).mark_line().encode(
                    x='Date:T',
                    y='Price:Q',
                    color=alt.value('blue')
                ).properties(
                    width=700,
                    height=400,
                    title=f"{stock_symbol} Price with Moving Averages"
                )
                
                ma20_chart = alt.Chart(df).mark_line().encode(
                    x='Date:T',
                    y='MA_20:Q',
                    color=alt.value('orange')
                )
                
                ma50_chart = alt.Chart(df).mark_line().encode(
                    x='Date:T',
                    y='MA_50:Q',
                    color=alt.value('red')
                )
                
                st.altair_chart(chart + ma20_chart + ma50_chart, use_container_width=True)
                
                # Technical Indicators
                col1, col2, col3 = st.columns(3)
                
                # Simple RSI calculation (14-period)
                delta = df['Price'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                latest_rsi = rsi.iloc[-1]
                
                with col1:
                    st.metric("RSI (14)", f"{latest_rsi:.2f}", help="Relative Strength Index - Above 70 = Overbought, Below 30 = Oversold")
                
                with col2:
                    latest_ma20 = df['MA_20'].iloc[-1]
                    st.metric("MA (20)", f"₹{latest_ma20:.2f}")
                
                with col3:
                    latest_ma50 = df['MA_50'].iloc[-1]
                    st.metric("MA (50)", f"₹{latest_ma50:.2f}")
                
        except Exception as e:
            st.error(f"Error in technical analysis: {str(e)}")


# ==================== PAGE 4: MARKET INDICES ====================
elif page == "💹 Market Indices":
    st.header("Market Indices")
    
    st.info("📌 Major Indian Stock Market Indices")
    
    try:
        # Get indices data
        indices = capital_market.market_indices()
        
        if indices:
            indices_df = pd.DataFrame(indices)
            
            # Display indices in grid
            col1, col2 = st.columns(2)
            
            for idx, row in indices_df.iterrows():
                with col1 if idx % 2 == 0 else col2:
                    index_name = row.get('index', 'Unknown')
                    last_price = row.get('lastPrice', 0)
                    change = row.get('change', 0)
                    pChange = row.get('pChange', 0)
                    
                    # Color code based on change
                    color = "🟢" if change >= 0 else "🔴"
                    
                    st.metric(
                        f"{color} {index_name}",
                        f"{last_price:.2f}",
                        f"{change:.2f} ({pChange:.2f}%)"
                    )
            
            st.markdown("---")
            st.subheader("All Indices Data")
            st.dataframe(indices_df, use_container_width=True)
        else:
            st.warning("No indices data available")
            
    except Exception as e:
        st.error(f"Error fetching indices: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
    <small>📊 NSE Market Dashboard | Data powered by nselib | Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</small>
    </div>
    """,
    unsafe_allow_html=True
)