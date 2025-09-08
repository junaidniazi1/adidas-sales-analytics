import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import io

# Page configuration
st.set_page_config(
    page_title="Adidas Sales Dashboard",
    page_icon="👟",
    layout="wide"
)

# Beautiful CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0 2rem 0;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    .chart-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 1rem;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 0.5rem;
    }
    
    .success-msg {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
        text-align: center;
    }
    
    .error-msg {
        background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
        text-align: center;
    }
    
    .welcome-box {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin: 2rem 0;
    }
    
    .welcome-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .welcome-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 1rem;
    }
    
    .welcome-text {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def clean_data(df):
    """Simple data cleaning function"""
    try:
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Convert date column
        if 'Invoice Date' in df.columns:
            df['Invoice Date'] = pd.to_datetime(df['Invoice Date'], errors='coerce')
        
        # Clean currency columns
        currency_cols = ['Price per Unit', 'Total Sales', 'Operating Profit']
        for col in currency_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(r'[\$,]', '', regex=True),
                    errors='coerce'
                )
        
        # Clean numeric columns
        if 'Units Sold' in df.columns:
            df['Units Sold'] = pd.to_numeric(df['Units Sold'], errors='coerce')
        
        # Clean operating margin
        if 'Operating Margin' in df.columns:
            df['Operating Margin'] = pd.to_numeric(
                df['Operating Margin'].astype(str).str.replace('%', ''),
                errors='coerce'
            ) / 100
        
        # Remove rows with critical missing data
        df = df.dropna(subset=['Total Sales', 'Units Sold'])
        
        return df
    except Exception as e:
        st.error(f"Error cleaning data: {str(e)}")
        return pd.DataFrame()

def load_data(uploaded_file):
    """Load data from uploaded file"""
    try:
        # Read file based on extension
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Check if empty
        if df.empty:
            st.error("The uploaded file is empty.")
            return None
        
        # Clean the data
        df = clean_data(df)
        
        if df.empty:
            st.error("No valid data found after cleaning.")
            return None
        
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def show_metrics(df):
    """Display key metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = df['Total Sales'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${total_revenue:,.0f}</div>
            <div class="metric-label">💰 Total Revenue</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_units = df['Units Sold'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_units:,.0f}</div>
            <div class="metric-label">📦 Units Sold</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        transaction_count = len(df)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{transaction_count:,}</div>
            <div class="metric-label">🧾 Transactions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_margin = df['Operating Margin'].mean() * 100 if 'Operating Margin' in df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_margin:.1f}%</div>
            <div class="metric-label">📊 Avg Margin</div>
        </div>
        """, unsafe_allow_html=True)

def create_charts(df):
    """Create beautiful charts"""
    
    # Revenue by Region
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🌍 Revenue by Region</div>', unsafe_allow_html=True)
        
        if 'Region' in df.columns:
            region_data = df.groupby('Region')['Total Sales'].sum().reset_index()
            region_data = region_data.sort_values('Total Sales', ascending=True)
            
            fig = px.bar(
                region_data,
                x='Total Sales',
                y='Region',
                orientation='h',
                color='Total Sales',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🛍️ Sales Method Distribution</div>', unsafe_allow_html=True)
        
        if 'Sales Method' in df.columns:
            sales_data = df.groupby('Sales Method')['Total Sales'].sum().reset_index()
            
            fig = px.pie(
                sales_data,
                values='Total Sales',
                names='Sales Method',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Top Products
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🏷️ Top 10 Products by Revenue</div>', unsafe_allow_html=True)
    
    if 'Product' in df.columns:
        top_products = df.groupby('Product')['Total Sales'].sum().reset_index()
        top_products = top_products.sort_values('Total Sales', ascending=False).head(10)
        
        fig = px.bar(
            top_products,
            x='Product',
            y='Total Sales',
            color='Total Sales',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            height=500,
            xaxis_tickangle=-45,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Monthly Trend
    if 'Invoice Date' in df.columns:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 Monthly Sales Trend</div>', unsafe_allow_html=True)
        
        df['Month'] = df['Invoice Date'].dt.to_period('M')
        monthly_data = df.groupby('Month')['Total Sales'].sum().reset_index()
        monthly_data['Month'] = monthly_data['Month'].astype(str)
        
        fig = px.line(
            monthly_data,
            x='Month',
            y='Total Sales',
            markers=True,
            color_discrete_sequence=['#667eea']
        )
        fig.update_traces(line=dict(width=3))
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def create_sidebar_filters(df):
    """Simple sidebar filters"""
    st.sidebar.markdown("## 🎯 Filters")
    
    # Region filter
    if 'Region' in df.columns:
        regions = st.sidebar.multiselect(
            "Select Regions",
            options=sorted(df['Region'].unique()),
            default=sorted(df['Region'].unique())
        )
        df = df[df['Region'].isin(regions)]
    
    # Sales Method filter
    if 'Sales Method' in df.columns:
        methods = st.sidebar.multiselect(
            "Select Sales Methods",
            options=sorted(df['Sales Method'].unique()),
            default=sorted(df['Sales Method'].unique())
        )
        df = df[df['Sales Method'].isin(methods)]
    
    # Date range filter
    if 'Invoice Date' in df.columns:
        min_date = df['Invoice Date'].min().date()
        max_date = df['Invoice Date'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            df = df[df['Invoice Date'].dt.date.between(date_range[0], date_range[1])]
    
    return df

def show_welcome():
    """Show welcome screen"""
    st.markdown("""
    <div class="welcome-box">
        <div class="welcome-icon">👟</div>
        <div class="welcome-title">Welcome to Adidas Sales Dashboard</div>
        <div class="welcome-text">Upload your sales data to get started with beautiful analytics and insights</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample data format
    st.markdown("### 📋 Expected Data Format")
    sample_data = pd.DataFrame({
        'Retailer': ['West Gear', 'Foot Locker', 'Sports Direct'],
        'Region': ['West', 'Northeast', 'South'],
        'Product': ['Men\'s Footwear', 'Women\'s Footwear', 'Men\'s Footwear'],
        'Total Sales': [600000, 382500, 625000],
        'Units Sold': [1200, 850, 1250],
        'Sales Method': ['In-store', 'Online', 'Outlet']
    })
    st.dataframe(sample_data, use_container_width=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>👟 Adidas Sales Dashboard</h1>
        <p>Beautiful Analytics for Your Business</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    st.sidebar.markdown("## 📁 Upload Data")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a file",
        type=["csv", "xlsx", "xls"],
        help="Upload your Adidas sales data"
    )
    
    if uploaded_file is not None:
        # Load data
        with st.spinner("Loading data..."):
            df = load_data(uploaded_file)
        
        if df is not None:
            # Success message
            st.markdown(f"""
            <div class="success-msg">
                ✅ Data loaded successfully! {len(df):,} records processed
            </div>
            """, unsafe_allow_html=True)
            
            # Apply filters
            filtered_df = create_sidebar_filters(df)
            
            # Show metrics
            show_metrics(filtered_df)
            
            # Show charts
            create_charts(filtered_df)
            
            # Data preview
            with st.expander("📋 View Data"):
                st.dataframe(filtered_df.head(100), use_container_width=True)
            
            # Download section
            col1, col2 = st.columns(2)
            
            with col1:
                csv_data = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name=f"adidas_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Create summary report
                summary = f"""# Sales Report
                
Total Revenue: ${filtered_df['Total Sales'].sum():,.2f}
Total Units: {filtered_df['Units Sold'].sum():,.0f}
Transactions: {len(filtered_df):,}
Date Range: {filtered_df['Invoice Date'].min():%Y-%m-%d} to {filtered_df['Invoice Date'].max():%Y-%m-%d}
"""
                st.download_button(
                    label="📊 Download Report",
                    data=summary,
                    file_name=f"sales_report_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
    
    else:
        show_welcome()

if __name__ == "__main__":
    main()