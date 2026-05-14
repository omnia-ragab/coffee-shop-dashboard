import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ====================== CONFIG & STYLING ======================
st.set_page_config(page_title="Barista Coffee Dashboard", layout="wide", page_icon="☕")

# Custom CSS for better look
st.markdown("""
<style>
    .main {background-color: #0f172a;}
    .stPlotlyChart {background-color: #1e2937; border-radius: 10px; padding: 10px;}
    h1 {color: #f59e0b; font-size: 2.8rem;}
    .metric-card {background-color: #1e2937; padding: 15px; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

st.title("☕ Barista Coffee Shop")
st.markdown("### Sales Analytics Dashboard | 100,000 Transactions (2020–2025)")

# ====================== LOAD DATA ======================
@st.cache_data
def load_data():
    df = pd.read_csv("coffee_sales_cleaned.csv")
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df['year'] = df['order_date'].dt.year
    df['month'] = df['order_date'].dt.month_name()
    df['day_of_week'] = df['order_date'].dt.day_name()
    df['hour'] = pd.to_datetime(df['order_time'], format='%H:%M:%S', errors='coerce').dt.hour
    return df

df = load_data()

# ====================== SIDEBAR ======================
st.sidebar.header("🔍 Filters")
date_range = st.sidebar.date_input("Date Range", [df['order_date'].min().date(), df['order_date'].max().date()])
locations = st.sidebar.multiselect("Store Location", options=sorted(df['store_location'].unique()), default=sorted(df['store_location'].unique()))
categories = st.sidebar.multiselect("Product Category", options=sorted(df['product_category'].unique()), default=sorted(df['product_category'].unique()))

# Filter
mask = (df['order_date'].dt.date.between(date_range[0], date_range[1]))
filtered_df = df[mask & df['store_location'].isin(locations) & df['product_category'].isin(categories)]

# ====================== KPIs (Modern Cards) ======================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("**Total Revenue**", f"${filtered_df['total_amount'].sum():,.0f}", "📈")
with col2:
    st.metric("**Total Transactions**", f"{len(filtered_df):,}", "🛒")
with col3:
    st.metric("**Avg Order Value**", f"${filtered_df['total_amount'].mean():.2f}", "💰")
with col4:
    st.metric("**Loyalty Members %**", f"{(filtered_df['loyalty_member'].mean()*100):.1f}%", "⭐")

st.divider()

# ====================== TABS (Improved) ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "⏰ Time Analysis", "📦 Products", "🏬 Stores", "👥 Customers"])

with tab1:
    st.subheader("Annual Revenue Trend")
    yearly = filtered_df.groupby('year')['total_amount'].sum().reset_index()
    fig1 = px.line(yearly, x='year', y='total_amount', markers=True, title="Annual Revenue Trend", 
                   color_discrete_sequence=['#f59e0b'])
    fig1.update_layout(template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Revenue by Day of Week")
        dow = filtered_df.groupby('day_of_week')['total_amount'].sum().reset_index()
        fig2 = px.bar(dow, x='day_of_week', y='total_amount', color_discrete_sequence=['#3b82f6'])
        fig2.update_layout(template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)
    
    with col_b:
        st.subheader("Revenue by Hour of Day")
        hourly = filtered_df.groupby('hour')['total_amount'].sum().reset_index()
        fig3 = px.bar(hourly, x='hour', y='total_amount', color_discrete_sequence=['#10b981'])
        fig3.update_layout(template="plotly_dark")
        st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.subheader("Performance by Product Category")
    cat = filtered_df.groupby('product_category')['total_amount'].sum().reset_index().sort_values('total_amount', ascending=False)
    fig4 = px.bar(cat, x='total_amount', y='product_category', orientation='h', 
                  color='total_amount', color_continuous_scale='Viridis')
    fig4.update_layout(template="plotly_dark")
    st.plotly_chart(fig4, use_container_width=True)

with tab4:
    st.subheader("Store Location Performance")
    loc = filtered_df.groupby('store_location')['total_amount'].sum().reset_index()
    fig5 = px.pie(loc, values='total_amount', names='store_location', 
                  color_discrete_sequence=px.colors.sequential.Plasma)
    fig5.update_layout(template="plotly_dark")
    st.plotly_chart(fig5, use_container_width=True)

with tab5:
    st.subheader("Loyalty & Demographics")
    loyalty = filtered_df.groupby('loyalty_member')['total_amount'].sum().reset_index()
    loyalty['loyalty_member'] = loyalty['loyalty_member'].map({True: 'Loyalty Member', False: 'Non-Member'})
    fig6 = px.bar(loyalty, x='loyalty_member', y='total_amount', color_discrete_sequence=['#8b5cf6'])
    fig6.update_layout(template="plotly_dark")
    st.plotly_chart(fig6, use_container_width=True)

st.divider()
st.subheader("🔑 Key Recommendations")
st.markdown("""
**1. Revenue Plateau** → Focus on increasing daily transactions  
**2. Lunch Window** → Big opportunity (only ~8%) → Launch lunch combos  
**3. Loyalty Program** → Improve rewards to increase spending  
**4. Senior Segment (55-64)** → Create special senior offers
""")

st.caption("🚀 Enhanced Dashboard | Built with Streamlit + Plotly")
