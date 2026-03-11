import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")

from data_setup import get_data

st.set_page_config(page_title="CEO Dashboard", layout="wide")
with st.sidebar:
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("Login.py")

page_bg = """
<style>

/* Page background */
[data-testid="stApp"],
[data-testid="stAppViewContainer"] { background-color:#A0D1FF;min-height:100vh;}
/* Sidebar background */
[data-testid="stSidebar"] {background-color: #055296;}
/* Sidebar label text */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {font-size: 18px !important;font-style: bold  !important;color: black !important;}
/* Sidebar header */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { font-size: 22px !important;font-weight: 600 !important;font-style: bold  !important;color: black !important;}
/* Increase tab font size */
button[data-baseweb="tab"] {font-size: 40px !important;font-weight: 600 !important; padding: 12px 25px !important;   /* increase spacing inside tab */}
/* Add space between tabs */
div[role="tablist"] {gap: 35px !important;}
button[aria-selected="true"] {border-bottom: 3px solid #055296 !important;}

</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)
data = get_data()
orders_fact = data["orders_fact"]
sessions = data["sessions"]
pageviews=data["pageviews"]

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
fil_pageview=pageviews.copy()

year = st.sidebar.multiselect("Year", sorted(fil_sessions["Year"].dropna().unique()))
if year:
    fil_sessions = fil_sessions[fil_sessions["Year"].isin(year)]

month = st.sidebar.multiselect("Month", sorted(fil_sessions["MonthName"].dropna().unique()))
if month:
    fil_sessions = fil_sessions[fil_sessions["MonthName"].isin(month)]

utm_campaign = st.sidebar.multiselect("UTM Campaign",sorted(fil_sessions["utm_campaign"].dropna().unique()))
if utm_campaign:
    fil_sessions = fil_sessions[fil_sessions["utm_campaign"].isin(utm_campaign)]

utm_source = st.sidebar.multiselect("Channel",sorted(fil_sessions["utm_source"].dropna().unique()))
if utm_source:
    fil_sessions = fil_sessions[fil_sessions["utm_source"].isin(utm_source)]
     
day_type = st.sidebar.multiselect("Day Type",sorted(fil_orders["DayType"].dropna().unique()))
if day_type:
    fil_orders = fil_orders[fil_orders["DayType"].isin(day_type)]

channel_type = st.sidebar.multiselect("Channel Type",sorted(fil_sessions["channel_type"].dropna().unique()))
if channel_type:
    fil_sessions = fil_sessions[fil_sessions["device_type"].isin(channel_type)]
    
st.title("🧸 Dashboard For Marketing Manager") 
# TABS
tab1, tab2, tab3 = st.tabs(["📢Marketing Traffic & Channel Performance","🔁 Customer Retention & Behavior Analysis","Business Insights & Performance Summary"])
with tab1:
    # st.write(fil_orders.head())
    # st.write(fil_sessions.head())

    # KPI cards
    total_visitors = fil_sessions["user_id"].nunique()
    repeat_visitors = fil_sessions[fil_sessions["is_repeat_session"] == 1]["user_id"].nunique()
    new_visitors=total_visitors-repeat_visitors
    new_visitors_pct = new_visitors / total_visitors if total_visitors else 0
    converted_sessions = fil_orders["website_session_id"].nunique()
    total_sessions = fil_sessions["website_session_id"].nunique()
    conversion_rate = converted_sessions / total_sessions if total_sessions else 0
    def calculate_session_yoy_full_year():
    
        yearly = (sessions.groupby("Year")["website_session_id"].nunique().reset_index(name="sessions").sort_values("Year"))
        yearly["last_year_sessions"] = yearly["sessions"].shift(1)
        yearly["sessions_yoy"] = ((yearly["sessions"] - yearly["last_year_sessions"]) / yearly["last_year_sessions"])
        avg_yoy = yearly["sessions_yoy"].dropna().mean()
        return avg_yoy
    avg_session_yoy_growth = calculate_session_yoy_full_year()
    #avg_session_yoy_growth, session_last_year = calculate_session_yoy_full_year()
    #avg_session_yoy_growth, _ = calculate_session_yoy_full_year()
    paid_channels = ["Paid Search","Paid Social"]
    free_channels = ["Direct","Organic Search","Organic Social"]
    channel_table=fil_sessions[["website_session_id","channel_type"]]
    session_orders=channel_table.merge(fil_orders,on="website_session_id",how="left")
    paid_revenue=session_orders[session_orders["channel_type"].isin(paid_channels)]["total_net_revenue"].sum()
    free_revenue=session_orders[session_orders["channel_type"].isin(free_channels)]["total_net_revenue"].sum()
    # Top channel by sessions
    top_channel = fil_sessions["utm_source"].value_counts().idxmax()
    top_channel_conv = top_channel_conv = ( fil_orders.merge( fil_sessions[["website_session_id","utm_source"]], on="website_session_id", how="left" ) .groupby("utm_source")["order_id"].nunique() / fil_sessions.groupby("utm_source")["website_session_id"].nunique() ).fillna(0).get(top_channel,0)
    
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    col1.metric("Total Visitors", format_num(total_visitors))
    col2.metric("New Visitors %", f"{new_visitors_pct:.2%}")
    col3.metric("Conversion Rate %", f"{conversion_rate:.2%}")
    col4.metric("Avg Session YoY %", f"{avg_session_yoy_growth:.2%}")
    col5.metric("Top Channel by Session", top_channel)
    col6.metric("Gsearch Conversion Rate", f"{top_channel_conv:.2%}")
    col7.metric("Free Channel Revenue", format_num(free_revenue))
    col8.metric("Paid Channel Revenue", format_num(paid_revenue))
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    #Total Sessions by Month & Channel Type
    st.subheader("Total Sessions by Month & Channel Type")
    monthly_channel = fil_sessions.groupby(["MonthShort", "channel_type"])["website_session_id"].nunique().reset_index(name="sessions") 
    month_order = [ "Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec" ]
    monthly_channel["MonthShort"] = pd.Categorical(monthly_channel["MonthShort"],categories=month_order,ordered=True)
    fig, ax = plt.subplots(figsize=(8,3)) 
    for channel in monthly_channel["channel_type"].unique(): 
        df_channel = monthly_channel[monthly_channel["channel_type"] == channel] 
        ax.plot(df_channel["MonthShort"], df_channel["sessions"], marker="o", label=channel)
    ax.set_ylabel("Sessions") 
    ax.legend() 
    ax.grid(axis="y", linestyle="--", alpha=0.3) 
    st.pyplot(fig)
    with st.expander("Chart Explanation", expanded=False):
        st.markdown("""
            - Paid Search generates the highest traffic, peaking near 44,000 sessions in November and December.  
            - Direct traffic remains stable between 5,000 and 10,000 sessions monthly.  
            - Paid Social contributes the lowest traffic, generally below 2,500 sessions.  
            - Strong traffic spikes are visible in Q4.  
            - Mid-year months show relatively lower performance.  

            **Insight:** Paid Search is the primary traffic driver and highly seasonal.
            """)

       
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    #Traffic Source Segment Trending
    st.subheader("Traffic Campaign Segment Trending")
    campaign_trend = fil_sessions.groupby(["MonthShort","utm_campaign"])["website_session_id"].nunique().reset_index(name="sessions")
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"] 
    campaign_trend["MonthShort"] = pd.Categorical( campaign_trend["MonthShort"], categories=month_order, ordered=True ) 
    campaign_trend = campaign_trend.sort_values("MonthShort") 
    campaign_colors = { "nonbrand": "#055296", "brand": "#118DFF", "desktop_targeted": "#F1A55A", "pilot": "#00CC96", "not available": "#AB6367" } 
    fig, ax = plt.subplots(figsize=(8,4)) 
    for campaign in campaign_trend["utm_campaign"].unique():
        df_campaign = campaign_trend[campaign_trend["utm_campaign"] == campaign] 
        color = campaign_colors.get(campaign, "#999999")
        ax.plot(df_campaign["MonthShort"], df_campaign["sessions"], marker="o", label=campaign, color=color)
    ax.legend()
    ax.set_ylabel("Sessions") 
    st.pyplot(fig)
    with st.expander("Chart Explanation", expanded=False):
        st.markdown("""
            - Nonbrand campaign leads throughout the year, rising from 30,000 to nearly 40,000 sessions in Q4.  
            - Not Available campaign remains steady between 5,000–10,000 sessions.  
            - Brand campaign gradually increases toward year-end.  
            - Desktop Targeted shows steady but low contribution.  
            - Pilot campaign declines after Q1.  

            **Insight:** Nonbrand drives scale, while Brand supports steady growth.
        """)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    col1, col2=st.columns(2)
    with col1:
        # Conversion Rate % by Channel
        st.subheader("Conversion Rate % by Channel")
        channel_sessions = fil_sessions.groupby("utm_source")["website_session_id"].nunique().reset_index(name="sessions") 
        orders_with_source = fil_orders.merge(fil_sessions[["website_session_id","utm_source"]], on="website_session_id", how="left") 
        channel_orders = orders_with_source.groupby("utm_source")["order_id"].nunique().reset_index(name="orders")
        df = channel_sessions.merge(channel_orders, on="utm_source", how="left") 
        df["conversion_rate"] = df["orders"] / df["sessions"]
        fig, ax = plt.subplots() 
        ax.bar(df["utm_source"], df["conversion_rate"], color="#055296") 
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0)) 
        ax.grid(axis="y", linestyle="--", alpha=0.3) 
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Not Available shows the highest conversion rate (~7.4%).  
            - BSearch follows closely (~7.2%).  
            - GSearch converts around 6.8%.  
            - SocialBook performs lowest (~3.2%).  
            - Search-based campaigns outperform social significantly.  

            **Insight:** Search intent traffic converts better than social traffic.
            """)


    with col2:
        # New vs Repeat Session Rate by Channel Type
        st.subheader("New vs Repeat Session Rate by Channel Type")
        # New vs Repeat Session Rate by Channel Type (Seaborn style)
        new_repeat = fil_sessions.groupby(["channel_type","session_type"])["website_session_id"].nunique().reset_index(name="sessions")
        fig, ax = plt.subplots(figsize=(6,4))
        sns.barplot(x="channel_type", y="sessions", hue="session_type", data=new_repeat, palette=["#055296","#118DFF"], ax=ax)
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Paid Search generates the highest new sessions, exceeding 350,000 users.  
            - Direct traffic shows a strong repeat session base of around 50,000 sessions.  
            - Paid Social contributes minimal repeat traffic compared to other channels.  
            - Direct channel maintains a healthier balance between new and returning users.  
            - Paid Search is acquisition-focused, while Direct supports retention.  

            **Insight:** Direct traffic indicates stronger brand recall and customer loyalty.
            """)

    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    col1,col2=st.columns(2)
    with col1:
        paid_sessions = fil_sessions[fil_sessions["channel_type"].isin(paid_channels)]["website_session_id"].nunique()
        free_sessions = fil_sessions[fil_sessions["channel_type"].isin(free_channels)]["website_session_id"].nunique()
        merged = fil_orders.merge(fil_sessions[["website_session_id","channel_type"]],on="website_session_id",how="left")
        paid_orders = merged[merged["channel_type"].isin(paid_channels)]["order_id"].nunique()
        free_orders = merged[merged["channel_type"].isin(free_channels)]["order_id"].nunique()
        paid_conversion = paid_orders / paid_sessions if paid_sessions else 0
        free_conversion = free_orders / free_sessions if free_sessions else 0
        comparison_df = pd.DataFrame({"Channel Group": ["Paid", "Free"],"Sessions": [paid_sessions, free_sessions],"Orders": [paid_orders, free_orders],"Conversion %": [paid_conversion, free_conversion]})
        st.subheader("Paid vs Free — Sessions & Orders")

        comparison_df = pd.DataFrame({"Channel Group": ["Paid", "Free"],"Sessions": [paid_sessions, free_sessions],"Orders": [paid_orders, free_orders]})
        fig, ax = plt.subplots(figsize=(6,4))
        x = np.arange(len(comparison_df))
        width = 0.35
        ax.bar(x - width/2, comparison_df["Sessions"], width, label="Sessions",color="#055296")
        ax.bar(x + width/2, comparison_df["Orders"], width, label="Orders",color="#118DFF")
        ax.set_xticks(x)
        ax.set_xticklabels(comparison_df["Channel Group"])
        ax.set_ylabel("Count")
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Paid channels generate approximately 390,000 sessions compared to around 80,000 from Free channels.  
            - Paid traffic produces about 25,000+ orders.  
            - Free traffic generates roughly 6,000 orders.  
            - Although Paid drives higher volume, Free traffic still contributes meaningful conversions.  
            - Revenue dependency is strongly tilted toward Paid acquisition.  

            **Insight:** Business growth is heavily dependent on paid marketing spend.
            """)
        
        

    with col2:
        st.subheader("Paid vs Free — Conversion Rate %")
        conversion_df = pd.DataFrame({"Channel Group": ["Paid", "Free"], "Conversion %": [paid_conversion, free_conversion]})
        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(conversion_df["Channel Group"],conversion_df["Conversion %"],color="#055296")
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        ax.set_ylabel("Conversion Rate")
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Free traffic converts at approximately 7.4%.  
            - Paid traffic converts around 6.7%.  
            - Free users show higher efficiency but lower volume.  
            - Paid campaigns drive scale but slightly lower conversion efficiency.  

            **Insight:** Optimizing paid targeting can significantly improve ROI.
            """)
        
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)     
    col1,col2=st.columns(2)
    with col1:
        #Conversion Rate % by Channel Type
        st.subheader("Conversion Rate % by Channel Type")
        channel_sessions = fil_sessions.groupby("channel_type")["website_session_id"].nunique().reset_index(name="sessions")
        orders_with_channel = fil_orders.merge( fil_sessions[["website_session_id", "channel_type"]], on="website_session_id", how="left" ) 
        channel_orders = orders_with_channel.groupby("channel_type")["order_id"].nunique().reset_index(name="orders") 
        df = channel_sessions.merge(channel_orders, on="channel_type", how="left")
        df["conversion_rate"] = df["orders"] / df["sessions"]
        colors =["#055296","#055296","#055296","#055296"]
        fig = px.bar(df, y="channel_type", x="conversion_rate", color=colors[:len(df)])
        #fig.update_traces(texttemplate="%{text:.2%}", textposition="outside")
        #fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Direct channel converts at approximately 7%.  
            - Paid Search converts around 6.5% to 6.8%.  
            - Paid Social shows the lowest conversion rate near 3%.  
            - Direct remains the most efficient channel overall.  
            - Social campaigns require optimization in targeting or landing experience.  

            **Insight:** Budget reallocation toward high-converting channels can improve overall performance.
            """)
            
    with col2:
        # Repeat Visitors by Channel Type
        st.subheader("Repeat Visitors by Channel Type")
        repeat_df = fil_sessions[fil_sessions["is_repeat_session"] == 1].groupby("channel_type")["user_id"].nunique().reset_index(name="repeat_visitors")
        fig = px.pie(repeat_df, values="repeat_visitors", names="channel_type",hole=0.4, color_discrete_sequence=["#055296","#118DFF"])
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Direct contributes around 63% of repeat visitors.  
            - Paid Search accounts for approximately 36% of repeat traffic.  
            - Paid Social contributes nearly 0% repeat visitors.  
            - Brand-driven channels dominate customer retention.  
            - Social campaigns focus more on acquisition than retention.  

            **Insight:** Retention strategies are strongest in Direct channel and weakest in Social.
            """)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
with tab2:
    #kpi cards
    total_visitors = fil_sessions["user_id"].nunique()
    repeat_visitors = fil_sessions[fil_sessions["is_repeat_session"] == 1]["user_id"].nunique()
    repeat_visitors_rate = repeat_visitors / total_visitors if total_visitors else 0
    repeat_sessions = fil_sessions[fil_sessions["is_repeat_session"] == 1]["website_session_id"].nunique()
    total_sessions = fil_sessions["website_session_id"].nunique()
    repeat_session_rate = repeat_sessions / total_sessions if total_sessions else 0
    yearly_sessions = fil_sessions.groupby("Year")["website_session_id"].nunique().reset_index()
    yearly_sessions["YoY"] = yearly_sessions["website_session_id"].pct_change()
    avg_repeat_yoy = yearly_sessions["YoY"].mean() * 100 if not yearly_sessions["YoY"].dropna().empty else 0
    #avg_days_sins_first=fil_sessions.groupby("user_id")["days_since_first_session"].max().mean()
    avg_days_sins_first=fil_sessions["days_since_first_session"].mean()

    # Top campaign by repeat visitors
    top_campaign = (fil_sessions[(fil_sessions["is_repeat_session"] == 1)& (fil_sessions["utm_campaign"] != "not available")].groupby("utm_campaign")["user_id"].nunique().reset_index().sort_values("user_id", ascending=False).head(1)["utm_campaign"].values[0]if "utm_campaign" in fil_sessions else "N/A")

    # kpi cards
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    col1.metric("Avg Days Since First Session",f"{avg_days_sins_first:.2f}") 
    col2.metric("Total Visitors", format_num(total_visitors))
    col3.metric("Repeat Visitors %", f"{repeat_visitors_rate:.2%}")
    col4.metric("Repeat Session Rate %", f"{repeat_session_rate:.2%}")
    col5.metric("Avg Repeat Visitor YoY", f"{avg_repeat_yoy:.2f}%")
    col6.metric("Top Campaign by Repeat", top_campaign)
    col7.metric("Repeat Visitors", format_num(repeat_visitors))
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 

    #Repeat Sessions by Days Bin
    sessions_by_days =  fil_sessions[fil_sessions["is_repeat_session"] == 1].groupby("days_since_first_session_bin")["website_session_id"].nunique().reset_index(name="Repeat Sessions")
    plt.figure(figsize=(8,4))
    sns.barplot(data=sessions_by_days, x="days_since_first_session_bin", y="Repeat Sessions", color="#055296")
    st.subheader("Repeat Sessions by Days Bin")
    plt.xlabel("Days Bin")
    plt.ylabel("Repeat Sessions")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)
    plt.tight_layout()
    with st.expander("Chart Explanation", expanded=False):
        st.markdown("""
            - The majority of repeat sessions fall under the 30+ days category, exceeding 53,000 sessions.  
            - The 15–30 days segment contributes around 15,000 repeat sessions.  
            - 8–14 days generates approximately 6,000 repeat sessions.  
            - Very few users return within 1–3 days.  
            - Immediate same-day repeat sessions are almost negligible.  

            **Insight:** Most customers return after a long gap, indicating weak short-term retention strategy.
            """)

    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    # Repeat Sessions Trend by Month
    st.subheader("Repeat Sessions By Month")
    monthly_repeat = fil_sessions[fil_sessions["is_repeat_session"] == 1].groupby("MonthShort")["website_session_id"].nunique().reset_index(name="Repeat Sessions")
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    monthly_repeat["MonthShort"] = pd.Categorical(monthly_repeat["MonthShort"], categories=month_order, ordered=True)
    monthly_repeat = monthly_repeat.sort_values("MonthShort")

    plt.figure(figsize=(8,3))
    sns.lineplot(data=monthly_repeat, x="MonthShort", y="Repeat Sessions", marker="o", color="#055296")
    plt.title("Repeat Sessions Trend by Month")
    plt.xlabel("Month")
    plt.ylabel("Repeat Sessions")
    plt.tight_layout()
    st.pyplot(plt)
    plt.tight_layout()
    with st.expander("Chart Explanation", expanded=False):
        st.markdown("""
            - January shows the highest repeat sessions at approximately 10,200.  
            - Repeat sessions decline sharply in April to nearly 4,200.  
            - Gradual recovery is visible from May onward.  
            - December again peaks at around 8,900 repeat sessions.  
            - Q4 shows strong improvement in customer retention.  

            **Insight:** Retention performance improves toward year-end but drops significantly in Q2.
            """)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 

    col1, col2 = st.columns(2)

    with col1:
        # Repeat Visitors by Device
        st.subheader("Repeat Visitors By Device")
        device_repeat = fil_sessions[fil_sessions["is_repeat_session"] == 1].groupby("device_type")["user_id"].nunique().reset_index(name="Visitors")

        plt.figure(figsize=(6,6))
        plt.pie(device_repeat["Visitors"], labels=device_repeat["device_type"], autopct="%1.1f%%", startangle=90)
        plt.title("Repeat Visitors by Device")
        st.pyplot(plt)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Desktop users account for approximately 60.4% of repeat visitors.  
            - Mobile contributes around 39.6% of repeat visitors.  
            - Desktop users demonstrate stronger loyalty behavior.  
            - Mobile retention is comparatively lower.  

            **Insight:** Mobile experience optimization can improve repeat engagement.
            """)

    with col2:
        # Repeat Revenue by Channel
        st.subheader("Repeat Revenue By Channel")
        merged_df = fil_orders.merge(fil_sessions[['website_session_id','utm_source']], on='website_session_id', how='left')
        channel_revenue = merged_df.groupby("utm_source")["total_net_revenue"].sum().reset_index()

        plt.figure(figsize=(6,6))
        sns.barplot(data=channel_revenue, x="utm_source", y="total_net_revenue", color="#055296")
        plt.title("Revenue by Channel")
        plt.xlabel("Channel")
        plt.ylabel("Total Net Revenue")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - GSearch generates the highest repeat revenue, exceeding 1.2 million.  
            - Not Available channel contributes around 350,000 in repeat revenue.  
            - BSearch contributes approximately 260,000.  
            - SocialBook generates minimal repeat revenue.  
            - Search-driven channels dominate repeat revenue contribution.  

            **Insight:** Search campaigns are highly valuable for long-term customer value.
            """)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    col1, col2 = st.columns(2)

    with col1:
        # Repeat Session Rate by Product
        st.subheader("Repeat Session Rate By Product")
        product_repeat = fil_orders.groupby("product_name")["website_session_id"].nunique().reset_index(name="sessions")

        plt.figure(figsize=(6,6))
        plt.pie(product_repeat["sessions"], labels=product_repeat["product_name"], autopct="%1.1f%%", startangle=90)
        plt.title("Repeat Session Rate by Product")
        st.pyplot(plt)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - The Original Mr. Fuzzy contributes the largest share at 60.5%.  
            - The Forever Love Bear contributes approximately 14.5%.  
            - The Birthday Sugar Panda and Hudson River Mini Bear each contribute around 12.5%.  
            - Repeat engagement is heavily concentrated in one flagship product.  

            **Insight:** The Original Mr. Fuzzy is the strongest product for customer loyalty.
            """)

    with col2:
        # Repeat Customers by Channel
        st.subheader("Repeat Customers By Channel")
        merged_df = fil_orders.merge(fil_sessions[['website_session_id','utm_source']], on='website_session_id', how='left')
        repeat_customers = merged_df.groupby("utm_source")["user_id"].nunique().reset_index(name="Customers")

        plt.figure(figsize=(5,3.4))
        sns.barplot(data=repeat_customers, x="utm_source", y="Customers", color="#055296")
        plt.title("Repeat Customers by Channel")
        plt.xlabel("Channel")
        plt.ylabel("Customers")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - GSearch brings the highest repeat customers at over 21,000 users.  
            - Not Available channel contributes around 6,000 repeat customers.  
            - BSearch generates approximately 4,500 repeat customers.  
            - SocialBook contributes very few repeat customers.  
            - Search channels significantly outperform social in retention.  

            **Insight:** Paid Search is effective not only for acquisition but also for retention.
            """)

    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 

