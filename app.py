import streamlit as st
import pandas as pd
import plotly.express as px

# ====================== CONFIG ======================
st.set_page_config(page_title="Barista Coffee Dashboard", layout="wide", page_icon="☕")
st.title("☕ Barista Coffee Shop - Sales Analytics Dashboard")
st.markdown("**100,000 Transactions | 2020–2025** | Data Analytics Capstone")

# ====================== LOAD ORIGINAL DATA ======================
@st.cache_data
def load_data():
    df = pd.read_csv("coffee_sales_cleaned.csv")
    # تنظيف البيانات
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df['year'] = df['order_date'].dt.year
    df['month'] = df['order_date'].dt.month_name()
    df['day_of_week'] = df['order_date'].dt.day_name()
    
    # استخراج الساعة من order_time
    df['hour'] = pd.to_datetime(df['order_time'], format='%H:%M:%S', errors='coerce').dt.hour
    return df

df = load_data()

# ====================== SIDEBAR FILTERS ======================
st.sidebar.header("🔍 Filters")

date_range = st.sidebar.date_input(
    "Date Range", 
    [df['order_date'].min().date(), df['order_date'].max().date()]
)

locations = st.sidebar.multiselect(
    "Store Location", 
    options=sorted(df['store_location'].unique()),
    default=sorted(df['store_location'].unique())
)

categories = st.sidebar.multiselect(
    "Product Category", 
    options=sorted(df['product_category'].unique()),
    default=sorted(df['product_category'].unique())
)

# ====================== FILTER DATA ======================
mask = (df['order_date'].dt.date.between(date_range[0], date_range[1]))
filtered_df = df[mask & df['store_location'].isin(locations) & df['product_category'].isin(categories)]

# ====================== KPIs ======================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${filtered_df['total_amount'].sum():,.0f}")
col2.metric("Total Transactions", f"{len(filtered_df):,}")
col3.metric("Avg Order Value", f"${filtered_df['total_amount'].mean():.2f}")
col4.metric("Model Accuracy", "R² = 0.83")

st.divider()

# ====================== TABS ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "⏰ Time Analysis", "📦 Products", "🏬 Stores", "👥 Customers"])

with tab1:
    st.subheader("Annual Revenue Trend")
    yearly = filtered_df.groupby('year')['total_amount'].sum().reset_index()
    fig1 = px.bar(yearly, x='year', y='total_amount', title="Annual Revenue")
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Revenue by Day of Week")
        dow = filtered_df.groupby('day_of_week')['total_amount'].sum().reset_index()
        fig2 = px.bar(dow, x='day_of_week', y='total_amount')
        st.plotly_chart(fig2, use_container_width=True)
    
    with col_b:
        st.subheader("Revenue by Hour")
        hourly = filtered_df.groupby('hour')['total_amount'].sum().reset_index()
        fig3 = px.bar(hourly, x='hour', y='total_amount', title="Revenue by Time of Day")
        st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.subheader("Revenue by Product Category")
    cat = filtered_df.groupby('product_category')['total_amount'].sum().reset_index()
    fig4 = px.bar(cat, x='total_amount', y='product_category', orientation='h', title="Revenue by Category")
    st.plotly_chart(fig4, use_container_width=True)

with tab4:
    st.subheader("Revenue by Store Location")
    loc = filtered_df.groupby('store_location')['total_amount'].sum().reset_index()
    fig5 = px.bar(loc, x='store_location', y='total_amount', title="Revenue by Location")
    st.plotly_chart(fig5, use_container_width=True)

with tab5:
    st.subheader("Loyalty Program Analysis")
    loyalty = filtered_df.groupby('loyalty_member')['total_amount'].agg(['sum', 'count']).reset_index()
    loyalty['loyalty_member'] = loyalty['loyalty_member'].map({True: 'Loyalty Member', False: 'Non-Member'})
    fig6 = px.bar(loyalty, x='loyalty_member', y='sum', title="Revenue by Loyalty Status")
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Age Group Analysis")
    if 'customer_age' in filtered_df.columns:
        filtered_df['age_group'] = pd.cut(filtered_df['customer_age'], 
                                         bins=[0,24,34,44,54,64,100], 
                                         labels=['18-24','25-34','35-44','45-54','55-64','65+'])
        age_rev = filtered_df.groupby('age_group')['total_amount'].sum().reset_index()
        fig7 = px.bar(age_rev, x='age_group', y='total_amount')
        st.plotly_chart(fig7, use_container_width=True)

st.divider()
st.subheader("🔑 Key Insights from the Report")
st.info("""
- Revenue has been **flat** for 5 years → Need growth strategies  
- **Lunch window** is underperforming (big opportunity)  
- Loyalty program has room to grow  
- **55-64 age group** is the highest spending segment
""")

st.caption("Built with ❤️ using Streamlit | Barista Coffee Sales Analytics")
