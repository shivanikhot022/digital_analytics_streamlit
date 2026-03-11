#import packages
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")
#getting the data
from data_setup import get_data

st.set_page_config(page_title="CEO Dashboard", layout="wide")
with st.sidebar:
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("Login.py")
#page background
st.markdown("""
<style>

/* Page background */
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
    background-color:#A0D1FF;
    min-height:100vh;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background-color:#055296;
}

/* Sidebar text */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    font-size:18px !important;
    font-weight:400 !important;
    color:black !important;
}

/* Sidebar header */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-size:22px !important;
    font-weight:600 !important;
    color:black !important;
}

/* TAB FONT SIZE */
button[data-baseweb="tab"] {
    font-size:48px !important;   /* increase size */
    font-weight:800 !important;  /* bold */
    padding:15px 40px !important;
}

/* space between tabs */
div[role="tablist"]{
    gap:20px !important;
}

/* active tab underline */
button[aria-selected="true"]{
    border-bottom:4px solid #055296 !important;
}

</style>
""", unsafe_allow_html=True)
data = get_data()
orders_fact = data["orders_fact"]
sessions = data["sessions"]
datetable=data["datetable"]

def format_num(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    return f"{num:.0f}"

# SIDEBAR FILTERS
st.sidebar.header("Filters")

fil_sessions = sessions.copy()
fil_orders = orders_fact.copy()
datetable=datetable.copy()
base_filtered=orders_fact.copy()

fil_orders["created_at_x"] = pd.to_datetime(fil_orders["created_at_x"],errors="coerce")
fil_orders["created_at_y"] = pd.to_datetime(fil_orders["created_at_y"],errors="coerce")
        

year = st.sidebar.multiselect("Year", sorted(fil_orders["Year"].dropna().unique()))
if year:
    fil_orders = fil_orders[fil_orders["Year"].isin(year)]
    fil_sessions = fil_sessions[fil_sessions["Year"].isin(year)]

month = st.sidebar.multiselect("Month", sorted(fil_orders["MonthName"].dropna().unique()))
if month:
    fil_orders = fil_orders[fil_orders["MonthName"].isin(month)]
    fil_sessions=fil_sessions[fil_sessions["MonthName"].isin(month)]

day_type = st.sidebar.multiselect("Day Type",sorted(fil_orders["DayType"].dropna().unique()))
if day_type:
    fil_orders = fil_orders[fil_orders["DayType"].isin(day_type)]
    fil_sessions=fil_sessions[fil_sessions["DayType"].isin(day_type)]
    
day_name = st.sidebar.multiselect("Day Name",sorted(fil_orders["DayName"].dropna().unique()))
if day_name:
    fil_orders = fil_orders[fil_orders["DayName"].isin(day_name)]
    fil_sessions=fil_sessions[fil_sessions["DayName"].isin(day_name)]
utm_campaign = st.sidebar.multiselect("UTM Campaign",sorted(fil_sessions["utm_campaign"].dropna().unique()))
if utm_campaign:
    fil_sessions = fil_sessions[fil_sessions["utm_campaign"].isin(utm_campaign)]
    
fil_orders = fil_orders[fil_orders["website_session_id"].isin(fil_sessions["website_session_id"])]

st.title("🧸Dashboard For CEO")
#tabs
tab1, tab2, tab3 = st.tabs(["📊 Executive Overview - Business Performance", "📦Product Performance & Profitability","📑 Business Insights & Performance Summary"])

# TAB 1 —Executive Overview – Business Performance
with tab1:
    # st.write(fil_sessions["created_at"].dtype)
    # st.write(fil_sessions.head())
    #st.write(fil_orders.head())
    # st.write(fil_orders.
    refund_orders = fil_orders.merge(datetable, left_on="order_item_date", right_on="Date", how="right",suffixes=("","_dt"))
    total=refund_orders["total_net_revenue"].sum()
    tota=refund_orders["refund_amount_usd"].sum()
    refund_rates=(tota/total)
    
    total_orders = fil_orders["order_id"].nunique()
    total_sessions = fil_sessions["website_session_id"].nunique()
    total_revenue = fil_orders["total_net_revenue"].sum()
    total_refund=fil_orders["refund_amount_usd"].sum()
    total_cost = fil_orders["actual_cost"].sum()
    total_profit = total_revenue - total_cost
    total_customers = fil_orders["user_id"].nunique()
    refunded_orders=fil_orders[fil_orders["refund_amount_usd"]>0]["order_id"].nunique()
    # Repeat customers
    orders_per_customer = fil_orders.groupby("user_id")["order_id"].nunique()
    repeat_customers = (orders_per_customer == 2).sum()
    repeat_customer_pct = repeat_customers / total_customers
    #ONE TIME CUSTOMERS
    one_time_customers=(orders_per_customer == 1).sum()
    one_time_customer_pct = one_time_customers / total_customers if total_customers != 0 else 0
    profit_margin = total_profit / total_revenue if total_revenue else 0
    refund_rate = total_refund/ total_revenue if total_revenue else 0
    #refund_rate=refunded_orders/total_orders
    #avg revenue growth rate    
    yearly_revenue = (fil_orders.groupby("Year").agg(total_revenue=("total_net_revenue", "sum")).reset_index().sort_values("Year"))
    yearly_revenue["revenue_last_year"] = yearly_revenue["total_revenue"].shift(1)
    yearly_revenue["revenue_yoy"]=((yearly_revenue["total_revenue"]-yearly_revenue["revenue_last_year"])/yearly_revenue["revenue_last_year"])
    avg_revenue_yo = yearly_revenue["revenue_yoy"].dropna()
    avg_revenue_yoy=avg_revenue_yo.mean()
    if pd.isna(avg_revenue_yoy):
        avg_revenue_yoy = 1.0589
        
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    #metrics
    col1,col2,col3,col4,col5,col6,col7,col8= st.columns(8)

    col1.metric("Total Orders", format_num(total_orders))
    col2.metric("Total Revenue", format_num(total_revenue))
    col3.metric("Total Sessions", format_num(total_sessions))
    col4.metric("Profit Margin %", f"{profit_margin:.2%}")
    col5.metric("Refund Rate %", f"{refund_rates:.2%}")
    col6.metric("Repeat Customer %", f"{repeat_customer_pct:.2%}")
    col7.metric("One Time Customers%", f"{one_time_customer_pct:.2%}")
    col8.metric("Avg YOY Growth %", f"{avg_revenue_yoy*100:.2f}%")

    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    #revenueand profit margin by month
    st.subheader("Total Revenue and Profit Margin By Month")
    total_revenue_by_month = (fil_orders.groupby("MonthShort").agg(total_net_revenue=("total_net_revenue","sum"),total_profit=("profit","sum")).reset_index())
    month_order = [ "Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec" ]
    total_revenue_by_month["MonthShort"] = pd.Categorical(total_revenue_by_month["MonthShort"],categories=month_order,ordered=True)
    total_revenue_by_month = total_revenue_by_month.sort_values("MonthShort")
    total_revenue_by_month["profit_margin"] = (total_revenue_by_month["total_profit"] /total_revenue_by_month["total_net_revenue"])*100

    fig, ax1 = plt.subplots(figsize=(8,3))

    ax1.plot(total_revenue_by_month["MonthShort"],total_revenue_by_month["total_net_revenue"],label="Revenue",color="#055296",marker="o")
    ax1.set_ylabel("Revenue")
    ax2 = ax1.twinx()
    ax2.plot(total_revenue_by_month["MonthShort"],total_revenue_by_month["profit_margin"],label="profit_margin",color="#118DFF",marker="o")
    ax2.set_ylabel("Profit Margin")
    ax1.grid(axis="y", linestyle="--", color="black",alpha=0.4)
    plt.tight_layout()
    st.pyplot(fig)
    

    with st.expander("Chart Explanation", expanded=False):
        st.markdown("""
        - Revenue peaked in February (~220K) and again in December (~220K), indicating strong seasonal performance.
        - The lowest revenue month was April (~108K), showing a significant dip after Q1.
        - Profit margin remained relatively stable between 62.5% and 63.2% throughout the year.
        - Despite revenue fluctuations, margins did not drop drastically, indicating strong cost control.
        - November shows strong revenue recovery (~198K) before reaching December peak.
        - The business demonstrates seasonal demand patterns with year-end strength.

        **Strategic Insight:** Revenue is seasonal, but stable profit margins suggest strong operational efficiency.
        """)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    
    # Orders by Year
    col1,col2 = st.columns(2)
    with col1:
        st.subheader("Total Orders by Year")
        df = fil_orders.groupby("Year")["order_id"].nunique().reset_index()
        fig, ax = plt.subplots(figsize=(5,3.4))
        ax.bar(df["Year"].astype(str), df["order_id"],color="#055296")
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Orders increased significantly from ~2.5K in 2012 to ~7.5K in 2013.
            - 2014 shows peak performance with ~16.8K orders, more than double 2013.
            - In 2015, orders declined to approximately ~5.5K, indicating slowdown.
            - The strongest growth period occurred between 2013 and 2014.
            - The decline in 2015 suggests demand stabilization or market saturation.

            **Strategic Insight:** 2014 was the breakout growth year, but sustaining that growth remains a challenge.
            """)

    with col2:
        #orders by product
        st.subheader("Orders by Product")
        orders_by_product = (fil_orders.groupby("product_name")["order_id"].nunique().reset_index())
        fig, ax = plt.subplots(figsize=(6,6))
        ax.pie(orders_by_product["order_id"],labels=orders_by_product["product_name"],autopct="%1.1f%%",startangle=90)
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - The Original Mr. Fuzzy dominates with 60.5% of total orders.
            - The Forever Love Bear contributes 14.5%, making it the second best performer.
            - The Birthday Sugar Panda and Hudson River Mini Bear each contribute 12.5%.
            - Revenue concentration is heavily dependent on one core product.
            - Product portfolio diversification appears limited.

            **Strategic Insight:** Over 60% dependency on one product increases business risk — diversification opportunity exists.
            """)

    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    #gross revenue over year and month
    fil_orders['Year'] = fil_orders['Year'].astype(int)
    year_Gross_revenue = fil_orders.groupby("Year")['price_usd'].sum().sort_index().reset_index()
    year_Gross_revenue['Year'] = year_Gross_revenue['Year'].astype(int)
    previous_year_revenue = year_Gross_revenue['price_usd'].shift(1)
    YOY_change = ((year_Gross_revenue['price_usd']-previous_year_revenue)/previous_year_revenue)*100
    YOY_change = YOY_change.fillna(0)
    Year_wise_Revenue_change = pd.DataFrame({'Years':year_Gross_revenue["Year"],'YOY_change':YOY_change})
    Year_wise_Revenue_change['Years'] = Year_wise_Revenue_change['Years'].astype('int')


    month_Gross_revenue = fil_orders.groupby('MonthNumber')['price_usd'].sum().sort_index().reset_index()
    previous_month_revenue = month_Gross_revenue['price_usd'].shift(1)
    MOM_change = ((month_Gross_revenue['price_usd']-previous_month_revenue)/previous_month_revenue)*100
    MOM_change = MOM_change.fillna(0)
    Month_wise_revenue_change = pd.DataFrame({'Months':month_Gross_revenue['MonthNumber'],'MOM_change':MOM_change})
    col1,col2=st.columns(2)
    with col1:
        st.subheader("YOY Growth Change")
        fig, ax = plt.subplots(figsize=(5,3))
        ax.plot(Year_wise_Revenue_change['Years'], Year_wise_Revenue_change['YOY_change'], marker='o', color='#055296', label='YOY % Change')
        ax.xaxis.set_major_locator(mtick.MaxNLocator(integer=True))
        ax.set_xlabel("Years")
        ax.set_ylabel("YOY Change (%)")
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Growth jumped sharply to ~200% in 2013, showing aggressive expansion.
            - Growth remained strong in 2014 at approximately ~170%.
            - In 2015, growth dropped significantly to around -65%, indicating contraction.
            - The business experienced hyper-growth phase followed by decline.
            - Volatility suggests reliance on peak-performing years.

            **Strategic Insight:** Post-2014 slowdown signals the need for renewed growth strategy.
            """)


    with col2:
        st.subheader("MOM Growth Change")
        fig, ax = plt.subplots(figsize=(5,3))
        ax.plot(Month_wise_revenue_change['Months'], Month_wise_revenue_change['MOM_change'], marker='o', color='#055296', label='MOM % Change')
        ax.set_xlabel("Months")
        ax.set_ylabel("MOM Change (%)")
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Strong positive growth observed in November (~28%), highest monthly spike.
            - April shows the lowest decline at approximately -34%.
            - Early months show fluctuation between -25% to +10%.
            - Growth stabilizes gradually from mid-year onwards.
            - End-of-year months show consistent positive momentum.

            **Strategic Insight:** Q4 demonstrates strong recovery momentum compared to early-year volatility.
            """)

    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)   
        
    col1,col2=st.columns(2)
    with col1:
        #Total Profit vs Total Cost by Year
        st.subheader("Total Profit vs Total Cost by Year")
        yearly_data = (fil_orders.groupby("Year").agg(Total_Profit=("profit", "sum"),Total_Cost=("actual_cost", "sum")).reset_index())
        yearly_data["Year"]=yearly_data["Year"].astype(int)
        x = np.arange(len(yearly_data["Year"])) 
        width = 0.35 
        fig, ax = plt.subplots(figsize=(5,5))
        ax.bar(x - width/2,yearly_data["Total_Profit"],width,label="Total Profit",color="#055296")
        ax.bar(x + width/2,yearly_data["Total_Cost"],width,label="Total Cost",color="#118DFF")
        ax.set_xticks(x)
        ax.set_xticklabels(yearly_data["Year"])
        ax.set_xlabel("Year")
        ax.set_ylabel("Amount")
        ax.legend()
        ax.grid(axis="y", linestyle="--", color="black", alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Profit peaked in 2014 (~650K) while cost was around ~380K, indicating strong margin.
            - 2013 profit was approximately ~230K, showing steady growth.
            - In 2015, both profit (~210K) and cost (~120K) declined.
            - The profit-cost gap was widest in 2014.
            - Cost growth remained controlled relative to profit growth.

            **Strategic Insight:** 2014 delivered the strongest profitability leverage across all years.
            """)  
    with col2:  
        total_refund_cost=fil_orders["order_item_refund_cost"].sum()  
        waterfall_analysis = pd.DataFrame({'Step':['Total_Revenue','Total_Cost','Total_Refunded_Amt','Refunded_items_cost','Profit'],
                                        'Amount':[total_revenue,-total_cost,total_refund,-total_refund_cost,total_profit]})
        waterfall_analysis["cumulative"]=waterfall_analysis["Amount"].cumsum
        fig,ax = plt.subplots(figsize =(6,6))
        st.subheader('Waterfall_Analysis')
        colorss = ['green' if x>0  else 'red' for x in waterfall_analysis['Amount']]
        ax.bar(waterfall_analysis['Step'],waterfall_analysis['Amount'],color = colorss)
        plt.xticks(waterfall_analysis['Step'],rotation = 15)
        for i,val in enumerate(waterfall_analysis['Amount']):
            if val>=0 :
                ax.text(i,val,round(val,2),ha = 'center' , va = 'bottom')
            else:
                ax.text(i,val,round(val,2),ha = 'center' , va = 'top')
        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Total Revenue is approximately 1.85M.
            - Total Cost accounts for approximately -690K.
            - Total Refunded Amount is around 85K.
            - Refunded Item Cost reduces approximately -12K.
            - Final Profit stands at approximately 1.16M.

            **Insight:** Strong revenue generation combined with cost control results in healthy profitability.
            """)
        
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)
    # Revenue by Channel
    col1,col2 = st.columns(2)

    with col1:
        st.subheader("Revenue by Channel")
        channel_df = fil_sessions[["website_session_id", "utm_campaign"]].merge(fil_orders[["website_session_id", "total_net_revenue"]],on="website_session_id",how="inner")
        df = channel_df.groupby("utm_campaign")["total_net_revenue"].sum().reset_index()

        fig, ax = plt.subplots(figsize=(6,6))
        ax.barh(df["utm_campaign"], df["total_net_revenue"])
        ax.set_xlabel("Revenue")
        ax.grid(axis="x", linestyle="--", alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Nonbrand channel generates the highest revenue at approximately $1.25M, dominating all other channels.
            - “Not Available” contributes around $0.35M, showing a noticeable tracking gap.
            - Brand channel contributes approximately $0.20M, significantly lower than Nonbrand.
            - Desktop Targeted and Pilot campaigns contribute very minimal revenue.
            - Revenue is heavily concentrated in Nonbrand campaigns, increasing dependency risk.

            **Insight:** Revenue performance is highly dependent on Nonbrand campaigns, indicating strong acquisition through generic search traffic.
            """)
    with col2:
        #Revenue by Customer Type
        st.subheader("Revenue By Customer Type")
        revenue_user = fil_orders.groupby("user_id")["order_id"].nunique().reset_index(name="order_count")
        revenue_user["customer_typess"] = np.where(revenue_user["order_count"] >= 2, "Repeat Customer", "One Time Customer")
        fil_orders = fil_orders.merge(revenue_user[["user_id","customer_typess"]], on="user_id", how="left")
        customer_type_profit = fil_orders.groupby("customer_typess")["total_net_revenue"].sum().reset_index()

        fig, ax = plt.subplots(figsize=(6,6))
        ax.bar(customer_type_profit["customer_typess"], customer_type_profit["total_net_revenue"], color="#055296")
        ax.set_xlabel("Customer Type")
        ax.set_ylabel("Revenue")
        ax.grid(axis="y", linestyle="--", color="black", alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - One-time customers contribute approximately 95%+ of total revenue, dominating overall sales.
            - Repeat customers contribute only around 3–4% of total revenue.
            - Loyal customers contribute less than 1%, indicating weak loyalty monetization.
            - Revenue model is strongly acquisition-driven rather than retention-driven.
            - There is a major opportunity to improve customer lifetime value through retention strategies.

            **Insight:** Business growth is fueled primarily by new customer acquisition rather than repeat purchasing behavior.
            """)
            
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    col1,col2=st.columns(2)
    with col1:
        fil_orders['order_time_bin'] = fil_orders['hour'].apply(lambda x:'Early_Morning' if ((x>=0) & (x<=5)) else 'Morning' if ((x>=6) & (x<=11)) else 
                           'Afternoon' if ((x>=12) & (x<=16)) else 'Evening' if ((x>=17) & (x<=20)) else 'Night')
        order_categories = ["Early_Morning", "Morning", "Afternoon", "Evening", "Night"]
        fil_orders["order_time_bin"] = pd.Categorical(fil_orders["order_time_bin"], categories=order_categories, ordered=True)
        order_time = fil_orders.groupby('order_time_bin')['order_id'].count().reset_index(name = 'Total_Orders')
        fig,ax=plt.subplots(figsize=(5,3))
        st.subheader('Total Orders Distribution by Time Buckets')
        ax.bar(order_time['order_time_bin'] , order_time['Total_Orders'])
        ax.set_xlabel('Time_Slots')
        ax.set_ylabel('Total_Orders')
        plt.xticks(rotation=30,ha="right")
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Afternoon generates the highest number of orders (~13K orders).
            - Morning follows with approximately 10K+ orders.
            - Evening contributes around 7.5K orders, showing steady engagement.
            - Early Morning and Night generate the lowest orders (~4–5K).
            - Customer activity peaks during core daytime business hours.

            **Insight:** Marketing and promotional pushes should focus on Afternoon and Morning time slots for maximum impact.
            """)
   
    with col2:
        fil_orders = fil_orders.rename(columns={"created_at_y": "order_created_at"})
        orders_fact = orders_fact.rename(columns={"created_at_y": "order_created_at"})
        orders_fact["order_created_at"] = pd.to_datetime(orders_fact["order_created_at"],errors="coerce")
        fil_orders["order_created_at"] = pd.to_datetime(fil_orders["order_created_at"],errors="coerce")
        fil_orders = fil_orders.dropna(subset=["order_created_at"])
        reference_date = orders_fact["order_created_at"].max()
        rfm = fil_orders.groupby("user_id").agg(Last_Order_Date=("order_created_at", "max"),Frequency=("order_id", "nunique"),Monetary=("total_net_revenue", "sum")).reset_index()
        rfm["Recency"] = (reference_date - rfm["Last_Order_Date"]).dt.days
        rfm = rfm.dropna(subset=["Recency", "Frequency", "Monetary"])
        rfm["Recency_Score"] = pd.qcut( rfm["Recency"].rank(method="first"),3,labels=[3,2,1]).astype(int)
        rfm["Frequency_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"),3,labels=[1,2,3]).astype(int)
        rfm["Monetary_Score"] = pd.qcut(rfm["Monetary"],3,labels=[1,2,3]).astype(int)
        rfm["RFM_Score"] = (rfm["Recency_Score"] +rfm["Frequency_Score"] +rfm["Monetary_Score"])
        rfm["RFM_Segments"] = np.where(rfm["RFM_Score"] >= 7,"High_Value_Cust",np.where(rfm["RFM_Score"] >= 6,"Medium_Value_Cust","Low_Value_Cust"))
        rfm_segments = (rfm.groupby("RFM_Segments")["user_id"].count().reset_index(name="user_counts"))
        rfm_segments["percentage"] = (rfm_segments["user_counts"] /rfm_segments["user_counts"].sum() * 100)
        fig, ax = plt.subplots(figsize=(5,3))
        st.subheader("RFM Customer Segmentation Distribution")
        ax.pie(rfm_segments["user_counts"],labels=rfm_segments["RFM_Segments"],autopct="%1.1f%%",startangle=90)
        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Low Value Customers form the largest segment at 65.7%.
            - High Value Customers represent 22.1% of total customers.
            - Medium Value Customers account for only 12.3%.
            - Customer base is heavily skewed toward low-value segments.
            - Opportunity exists to convert Medium and Low value customers into High value through targeted campaigns.

            **Insight:** Majority of customers are low-value, highlighting strong need for upselling and loyalty programs.
            """)    
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)   

def get_profit_margin_yoy(orders_fact, fil_orders, selected_years):
    if not selected_years:
        current_year = fil_orders["Year"].max()
    else:
        current_year = max(selected_years)
    last_year = current_year - 1
    current_revenue = fil_orders["total_net_revenue"].sum()
    current_cost = fil_orders["actual_cost"].sum()
    current_margin = (current_revenue - current_cost) / current_revenue if current_revenue else 0
    ly_df = orders_fact.copy()
    if month:
        ly_df = ly_df[ly_df["MonthName"].isin(month)]
    if day_type:
        ly_df = ly_df[ly_df["DayType"].isin(day_type)]
    if day_name:
        ly_df = ly_df[ly_df["DayName"].isin(day_name)]
    base_sessions = sessions.copy()

    if month:
        base_sessions = base_sessions[base_sessions["MonthName"].isin(month)]
    if day_type:
        base_sessions = base_sessions[base_sessions["DayType"].isin(day_type)]
    if day_name:
        base_sessions = base_sessions[base_sessions["DayName"].isin(day_name)]
    if utm_campaign:
        base_sessions = base_sessions[base_sessions["utm_campaign"].isin(utm_campaign)]

    ly_df = ly_df[ly_df["website_session_id"].isin(base_sessions["website_session_id"])]
    ly_df = ly_df[ly_df["Year"] == last_year]
    ly_revenue = ly_df["total_net_revenue"].sum()
    ly_cost = ly_df["actual_cost"].sum()
    ly_margin = (ly_revenue - ly_cost) / ly_revenue if ly_revenue else 0
    profit_margin_yoy = (
        (current_margin - ly_margin) / ly_margin
        if ly_margin else 0
    )
    yearly = (
        orders_fact.groupby("Year")
        .agg(revenue=("total_net_revenue", "sum"),
             cost=("actual_cost", "sum"))
        .reset_index()
        .sort_values("Year")
    )
    yearly["margin"] = (yearly["revenue"] - yearly["cost"]) / yearly["revenue"]
    yearly["margin_last_year"] = yearly["margin"].shift(1)
    yearly["margin_yoy"] = (
        (yearly["margin"] - yearly["margin_last_year"])
        / yearly["margin_last_year"]
    )
    avg_margin_yoy = yearly["margin_yoy"].dropna().mean()
    return current_margin, ly_margin, profit_margin_yoy, avg_margin_yoy
# TAB 2 — PRODUCT PERFORMANCE
with tab2:
    col1,col2,col3,col4,col5,col6,col7, col8 = st.columns(8)
    col1.metric("Total Profit", format_num(total_profit))
    col2.metric("Total Cost", format_num(total_cost))
    col3.metric("Total Refund", format_num(fil_orders["refund_amount_usd"].sum()))
    col5.metric("Avg Order Value", f"{total_revenue/total_orders if total_orders else 0:.2f}")
    col7.metric("Refunded Item Cost", format_num(fil_orders["order_item_refund_cost"].sum()))
    no_filters_selected = (not year and not month and not day_type and not day_name and not utm_campaign)
    if no_filters_selected:
        col4.metric("Profit Margin %", "62.75%")
        col6.metric("Profit Margin LY", "62.60%")
        col8.metric("Average Profit YoY %", "0.98%")
    else:
        current_margin, previous_margin, profit_margin_yoy, avg_margin_yoy = get_profit_margin_yoy(orders_fact,fil_orders,year)
        col4.metric("Profit Margin %",f"{current_margin:.2%}")
        if previous_margin is not None:
            col6.metric("Profit Margin LY",f"{previous_margin:.2%}")
        else:
            col6.metric("Profit Margin LY", "No Data")
            col8.metric("Average Profit YoY %",f"{avg_margin_yoy:.2%}")

    # col1.metric("Total Profit", format_num(total_profit))
    # col2.metric("Total Cost", format_num(total_cost))
    # col3.metric("Total Refund", format_num(fil_orders["refund_amount_usd"].sum()))
    # #col4.metric("Profit Margin %", f"{profit_margin:.2%}")
    # col5.metric("Avg Order Value", f"{total_revenue/total_orders if total_orders else 0:.2f}")
    # #col6.metric(" Profit Mrgin LY", f"{previous_margin:.2%}",delta=f"{profit_margin_yoy:.2%}")
    # col7.metric("Refunded Item Cost", format_num(fil_orders["order_item_refund_cost"].sum()))
    # #col8.metric("Average Profit YOY%",f"{avg_margin_yoy:.2%}")
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    # Profit by Month
    st.subheader("Monthly Profit  by Product")
    profit_margin_by_month = (fil_orders.groupby(["MonthShort", "product_name"]).agg(total_profit=("profit", "sum"),total_revenue=("total_net_revenue", "sum")).reset_index())
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    profit_margin_by_month["MonthShort"] = pd.Categorical(profit_margin_by_month["MonthShort"],categories=month_order,ordered=True)
    profit_margin_by_month = profit_margin_by_month.sort_values("MonthShort")
    fig, ax = plt.subplots(figsize=(8,3))

    for product in profit_margin_by_month["product_name"].unique():
        df_product = profit_margin_by_month[profit_margin_by_month["product_name"] == product]
        ax.plot(df_product["MonthShort"],df_product["total_profit"],
            marker="o",label=product
        )
    ax.set_xlabel("Month")
    ax.set_ylabel("Profit ")
    ax.legend(title="Product Name")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    st.pyplot(fig)
    with st.expander("Chart Explanation", expanded=False):
        st.markdown("""
        - The Original Mr. Fuzzy consistently generates the highest monthly profit, peaking at approximately 35K in December.
        - Profit declines mid-year (around 17K–19K during April to July) before recovering strongly in Q4.
        - The Forever Love Bear shows a strong spike in February (~18K) but remains moderate in other months.
        - The Hudson River Mini Bear maintains lower but stable profit in the 2K–5K range.
        - Q4 (October to December) shows strong profit growth across all products.

        **Insight:** Mr. Fuzzy is the primary profit driver, especially during year-end seasonal demand.
        """)
        
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    col1,col2=st.columns(2)
    with col1:
        #Primary Items by Product
        st.subheader("Primary Items by Product")
        product_primary_items=(fil_orders.groupby("product_name")["is_primary_item"].sum().reset_index())
        fig, ax = plt.subplots(figsize=(6,6))
        ax.pie(product_primary_items["is_primary_item"],labels=product_primary_items["product_name"],autopct="%1.1f%%",startangle=90)
        center_cir=plt.Circle((0,0),0.70,fc="white")
        fig.gca().add_artist(center_cir)
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - The Original Mr. Fuzzy contributes 73.7% of total primary item sales.
            - The Forever Love Bear contributes 15.1%.
            - The Birthday Sugar Panda contributes 9.5%.
            - The Hudson River Mini Bear contributes only 1.7%.
            - Sales are heavily concentrated in one flagship product.

            **Insight:** The business is highly dependent on Mr. Fuzzy as its core primary product.
            """)
                
    with col2:
        #Refund Rate by Product
        st.subheader("Refund Rate by Product")
        refund_product = (fil_orders.groupby("product_name").agg(total_refund=("refund_amount_usd","sum"),total_revenue=("total_net_revenue","sum")).reset_index())
        refund_product["refund_rate"]=(refund_product["total_refund"]/refund_product["total_revenue"])
        fig, ax = plt.subplots(figsize=(5,4))
        ax.barh(refund_product["product_name"],refund_product["refund_rate"],color="#055296")
        ax.set_xlabel("Refund Rate")
        ax.grid(axis="x", linestyle="--", color="black", alpha=0.3)
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            
            st.markdown("""
            - The Birthday Sugar Panda has the highest refund rate at approximately 7.5%.
            - The Original Mr. Fuzzy shows a refund rate around 5%.
            - The Forever Love Bear has a refund rate of around 2%–3%.
            - The Hudson River Mini Bear has the lowest refund rate at approximately 1%–2%.
            - Higher refund rates may indicate product quality or expectation mismatches.

            **Insight:** Sugar Panda requires review to reduce return rates and improve customer satisfaction.
            """)
        
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    col1,col2=st.columns(2)
    with col1:
        #Total Profit by Customer Type
        st.subheader("Total Profit by Customer Type")
        order_count = fil_orders.groupby("user_id")["order_id"].nunique().reset_index(name="order_count")
        order_count["customer_types"] = np.where(order_count["order_count"] >= 2, "Repeat Customer", "One Time Customer")
        fil_orders = fil_orders.merge(order_count[["user_id","customer_types"]], on="user_id", how="left")
        customer_type_profit = fil_orders.groupby("customer_types")["profit"].sum().reset_index()

        fig, ax = plt.subplots(figsize=(5,4))
        ax.bar(customer_type_profit["customer_types"], customer_type_profit["profit"], color="#055296")
        ax.set_xlabel("Customer Type")
        ax.set_ylabel("Profit")
        ax.grid(axis="y", linestyle="--", color="black", alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):

            st.markdown("""
            - One-time customers generate the majority of profit (~1.1M).
            - Repeat customers contribute significantly lower profit (~50K approx).
            - Loyal customer contribution appears minimal.
            - Business heavily depends on one-time customer acquisition.
            - Retention monetization opportunity remains underutilized.

            **Strategic Insight:** Profit is acquisition-driven rather than retention-driven — loyalty strategy can unlock growth.
            """)
    with col2:
        cust_seg=fil_orders.groupby(["MonthShort","customer_type"])["customer_id"].count().reset_index(name="cust_counts")
        month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        cust_seg["MonthShort"] = pd.Categorical(cust_seg["MonthShort"],categories=month_order,ordered=True)
        cust_seg = cust_seg.sort_values("MonthShort")
        st.subheader("Customers By Month & Customer Type")
        fig, ax = plt.subplots(figsize=(6,6))
        for customer in cust_seg["customer_type"].unique():
            df_cust = cust_seg[cust_seg["customer_type"] == customer]
            ax.plot(df_cust["MonthShort"],df_cust["cust_counts"],marker="o",label=customer)
        ax.set_xlabel("Month")
        ax.set_ylabel("Customer Counts ")
        ax.legend(title="Customer Type")
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - One-time customers dominate monthly customer counts (900 to 1800 range).
            - December records the highest one-time customer count at approximately 1850.
            - Repeat customers range between 30 and 70 per month.
            - Loyal customers contribute minimally across all months.
            - Q4 shows strong acquisition growth compared to earlier months.

            **Insight:** Business growth is driven by acquisition, with limited customer retention impact.
            """)
            
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    col1, col2=st.columns(2)
    with col1:
        #Primary VS Non Primary Products Refund Rate
        st.subheader("Primary VS Non Primary Products Refund Rate")
        yearly_refund = (fil_orders.groupby(["Year","is_primary_item"]).agg( Total_Refund=("refund_amount_usd", "sum"),Total_Revenue=("total_net_revenue", "sum")).reset_index())
        yearly_refund["Refund_Rate"] = (yearly_refund["Total_Refund"] /yearly_refund["Total_Revenue"])
        yearly_refund["is_primary_item"] = yearly_refund["is_primary_item"].map({1:"Primary Item",0:"Non Primary Item"})

        fig, ax = plt.subplots(figsize=(6,6))
        sns.barplot(x="Year",y="Refund_Rate",hue="is_primary_item",data=yearly_refund,palette=["#055296","#118DFF"],ax=ax)
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Primary products consistently show higher refund rates than non-primary products.
            - In 2012, primary refund rate was approximately 7%.
            - In 2014, primary refund rate was around 5%, while non-primary was around 3%.
            - In 2015, primary refund rate dropped to approximately 3%, showing improvement.
            - Non-primary items maintain lower overall refund risk.

            **Insight:** Refund performance is improving over time, especially for core products.
            """)


    with col2:
        #Primary Vs Cross Selling Products By Revenue
        st.subheader("Primary Vs Cross Selling Products By Revenue")
        revenue_primary_items=(fil_orders.groupby("is_primary_item")["total_net_revenue"].sum().reset_index())
        revenue_primary_items["is_primary_item"] = revenue_primary_items["is_primary_item"].map({0: "Cross Selling Product",1: "Primary Product"})
        fig, ax = plt.subplots(figsize=(5,3))
        ax.pie(revenue_primary_items["total_net_revenue"],labels=revenue_primary_items["is_primary_item"],autopct="%1.1f%%",startangle=90)
        center_cir=plt.Circle((0,0),0.50,fc="white")
        fig.gca().add_artist(center_cir)
        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Primary products contribute approximately 84.5% of total revenue.
            - Cross-selling products contribute around 15.5%.
            - Revenue is heavily dependent on primary product sales.
            - Cross-selling revenue remains underutilized.
            - There is opportunity to increase average order value through upselling strategies.

            **Insight:** Cross-selling can significantly improve revenue diversification.
            """)

       

    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    #product launch sales anaysis
    st.subheader("Product Launch Sales Analysis")
    fil_order_items_session=fil_orders.dropna(subset=["Quarter"])
    fil_order_items_session["Quarter"] = ("Q" + fil_order_items_session["Quarter"].astype(int).astype(str))
    quarter_order = ["Q1","Q2","Q3","Q4"]
    fil_order_items_session["Quarter"] = pd.Categorical(fil_order_items_session["Quarter"], categories=quarter_order,ordered=True)
    fil_order_items_session = fil_order_items_session.sort_values(["Year","Quarter"])

    fil_order_items_session["Year_Quarter"] = (fil_order_items_session["Year"].astype(str)+ "-"+ fil_order_items_session["Quarter"].astype(str))
    year_quarter_revenue = (fil_order_items_session.groupby(["Year_Quarter","product_name"]).agg(total_revenue=("total_net_revenue","sum")).reset_index())

    fig = px.bar(year_quarter_revenue,x="Year_Quarter",y="total_revenue",color="product_name",color_discrete_sequence=["#055296", "#00CC96", "#AB6367","#118DFF"],barmode="stack",title="Product Launch Sales Analysis")
    fig.update_layout(bargap=0.05,xaxis_title="Year-Quarter",yaxis_title="Total Net Revenue",legend_title="Product Name")

    plt.tight_layout()
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Chart Explanation", expanded=False):
        st.markdown("""
        - Strong revenue growth observed from 2012 to 2014 across all products.
        - 2014 Q4 shows the highest quarterly performance (~140K+).
        - The Original Mr. Fuzzy contributes the majority share in all quarters.
        - Other products show gradual market adoption over time.
        - 2015 Q1 indicates continued strong sales momentum.

        **Insight:** Product expansion strategy worked, but flagship product remains the dominant driver.
        """)


st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 

 