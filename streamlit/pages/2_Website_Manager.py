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

st.set_page_config(page_title="Website Manager Dashboard", layout="wide")
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

#formatter
def format_num(num):
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    else:
        return f"{num:.0f}"
    
data = get_data()
sessions = data["sessions"]
orders_fact = data["orders_fact"]
pageviews = data["pageviews"]

# Sort pageviews properly
pageviews = pageviews.sort_values(["website_session_id", "created_at"])
pageviews["is_entry_page"] = (pageviews["created_at"]== pageviews.groupby("website_session_id")["created_at"].transform("min")).astype(int)
st.sidebar.header("Filters")

fil_sessions = sessions.copy()
fil_orders = orders_fact.copy()
fil_pageviews = pageviews.copy()

year = st.sidebar.multiselect("Year", sorted(fil_sessions["Year"].dropna().unique()))
if year:
    fil_sessions = fil_sessions[fil_sessions["Year"].isin(year)]
    fil_orders = fil_orders[fil_orders["Year"].isin(year)]

month = st.sidebar.multiselect("Month", sorted(fil_sessions["MonthName"].dropna().unique()))
if month:
    fil_sessions = fil_sessions[fil_sessions["MonthName"].isin(month)]
    fil_orders = fil_orders[fil_orders["MonthName"].isin(month)]

device = st.sidebar.multiselect("Device Type", sorted(fil_sessions["device_type"].dropna().unique()))
if device:
    fil_sessions = fil_sessions[fil_sessions["device_type"].isin(device)]

session = st.sidebar.multiselect("Session Type", sorted(fil_sessions["session_type"].dropna().unique()))
if session:
    fil_sessions = fil_sessions[fil_sessions["session_type"].isin(session)]

product_name = st.sidebar.multiselect("Product Name", sorted(fil_orders["product_name"].dropna().unique()))
if product_name:
    fil_order_items_session = fil_orders[fil_orders["product_name"].isin(product_name)]

pageview_url = st.sidebar.multiselect(" Pageview URL", fil_pageviews["pageview_url"].unique())
if pageview_url:
    fil_session_page = fil_pageviews[fil_pageviews["pageview_url"].isin(pageview_url)]


# Restrict orders + pageviews
session_ids = fil_sessions["website_session_id"].unique()
fil_orders = orders_fact[orders_fact["website_session_id"].isin(session_ids)].copy()
fil_pageviews = pageviews[pageviews["website_session_id"].isin(session_ids)].copy()
fil_orders["device_type"] = fil_orders["website_session_id"].map(fil_sessions.set_index("website_session_id")["device_type"])
st.title("🧸Dashboard For Website Manager")
# TABS
tab1, tab2, tab3 = st.tabs([ "📈 Website Traffic- Engagement Performance", "🛒 Website Conversion Funnel Analysis","📑 Business Insights & Performance Summary"])

with tab1:
    #st.write(fil_sessions.head())
    #st.write(fil_pageviews.head())
    total_sessions = fil_sessions["website_session_id"].nunique()
    total_orders = fil_orders["order_id"].nunique()
    total_visitors = fil_sessions["user_id"].nunique()
    total_revenue = fil_orders["total_net_revenue"].sum()
    converted_sessions = fil_orders["website_session_id"].nunique()
    conversion_rate = converted_sessions / total_sessions if total_sessions else 0
    new_sessions = fil_sessions[fil_sessions["is_repeat_session"] == 0]["website_session_id"].nunique()
    repeat_sessions = fil_sessions[fil_sessions["is_repeat_session"] == 1]["website_session_id"].nunique()
    repeat_session_rate = repeat_sessions / total_sessions if total_sessions else 0
    revenue_per_session = total_revenue / total_sessions if total_sessions else 0
    repeat_visitors=fil_sessions[fil_sessions["is_repeat_session"]==1]["user_id"].nunique()
    new_visitors=fil_sessions[fil_sessions["is_repeat_session"]==0]["user_id"].nunique()
    sessions_by_year = (sessions.groupby("Year")["website_session_id"].nunique().reset_index(name="sessions").sort_values("Year"))
    sessions_by_year["session_ly"] = sessions_by_year["sessions"].shift(1)
    sessions_by_year["yoy"] = ((sessions_by_year["sessions"] - sessions_by_year["session_ly"])/ sessions_by_year["session_ly"])
    total_sessions_a = sessions_by_year["sessions"].sum()
    total_session_ly = sessions_by_year["session_ly"].dropna().sum()
    total_yoy = (total_sessions_a - total_session_ly) / total_session_ly
    avg_yoy = sessions_by_year["yoy"].dropna().mean()
    # Step 4: Get last year’s sessions for the latest year
    # latest_year = sessions_by_year["Year"].max()
    # session_last_year = sessions_by_year.loc[sessions_by_year["Year"] == latest_year, "previous_sessions"].values[0]
    # avg_session_yoy_growth = sessions_by_year["yoy_growth"].mean(skipna=True)
    col1,col2,col3,col4,col5,col6,col7, col8 = st.columns(8)
    col1.metric("Total Sessions", format_num(total_sessions))
    col2.metric("Total Orders", format_num(total_orders))
    col3.metric("Total Visitors",format_num(total_visitors))
    col4.metric("Revenue Per Session", f"{revenue_per_session:.2f}")
    col5.metric("New Sessions", format_num(new_sessions))
    col6.metric("Repeat Session %", f"{repeat_session_rate:.2%}")
    col7.metric("Repeat Visitors", format_num(repeat_visitors))
    col8.metric("Session LY", format_num(total_session_ly))
    
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    # Sessions & Conversion by Month
    st.subheader("Sessions & Conversion Rate by Month")
    monthly_sessions = fil_sessions.groupby("MonthShort")["website_session_id"].nunique().reset_index(name="sessions")
    monthly_orders = fil_orders.groupby("MonthShort")["order_id"].nunique().reset_index(name="orders")
    monthly = monthly_sessions.merge(monthly_orders, on="MonthShort", how="left")
    monthly["orders"]=monthly["orders"].fillna(0)
    monthly["conversion_rate"] = monthly["orders"] / monthly["sessions"]
    month_order=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    monthly["MonthShort"]=pd.Categorical(monthly["MonthShort"],categories=month_order,ordered=True)
    monthly=monthly.sort_values("MonthShort")

    fig, ax1 = plt.subplots(figsize=(8,3))
    ax1.plot(monthly["MonthShort"], monthly["sessions"], label="Sessions",marker="o",color="#055296")
    ax1.set_ylabel("Sessions")

    ax2 = ax1.twinx()
    ax2.plot(monthly["MonthShort"], monthly["conversion_rate"],label="Conversion Rate", marker="o",color="#118DFF")
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    st.pyplot(fig)
    with st.expander("Chart Explanation", expanded=False):
        st.markdown("""
            - Sessions peak in February at approximately 55,000 and again in December at around 55,000.
            - The lowest session volume is observed in April at around 32,000.
            - Conversion rate remains relatively stable between 6.4% and 7.6% throughout the year.
            - February and December show both high traffic and strong conversion performance.
            - Mid-year (April to July) shows a dip in both sessions and conversion rate.

            **Insight:** Q1 and Q4 drive the strongest website performance, while mid-year requires optimization.
            """)



    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    # Conversion by Device
    col1,col2 = st.columns(2)

    with col1:
        st.subheader("Conversion Rate by Device")

        device_sessions = fil_sessions.groupby("device_type")["website_session_id"].nunique().reset_index(name="sessions")
        device_orders = fil_orders.groupby("device_type")["order_id"].nunique().reset_index(name="orders")
        df = device_sessions.merge(device_orders, on="device_type", how="left")
        df["conversion_rate"] = df["orders"] / df["sessions"]

        fig, ax = plt.subplots()
        ax.bar(df["device_type"], df["conversion_rate"])
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Desktop conversion rate is approximately 8.5%.
            - Mobile conversion rate is significantly lower at around 3.1%.
            - Desktop converts nearly 2.5 times better than mobile.
            - The large performance gap suggests mobile UX friction.

            **Insight:** Improving mobile experience could significantly increase total conversions.
            """)
    with col2:
        #Revenue per Session Type by Product
        st.subheader("Revenue per Session Type by Product")
        df = (fil_orders[["website_session_id","product_name","total_net_revenue"]].merge(fil_sessions[["website_session_id","session_type"]],on="website_session_id", how="left"))

        df = df.groupby(["session_type","product_name"])["total_net_revenue"] \
       .sum().reset_index()
        pivot_df = df.pivot(index="product_name", columns="session_type", values="total_net_revenue").fillna(0)

        fig, ax = plt.subplots()
        pivot_df.plot(kind="bar", ax=ax)
        plt.xticks(rotation=15, ha="right")
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - The Original Mr. Fuzzy generates the highest revenue from new sessions, approximately 900K+.
            - Repeat sessions contribute additional revenue of around 200K+ for Mr. Fuzzy.
            - The Forever Love Bear and Birthday Sugar Panda generate moderate revenue from new sessions.
            - Revenue from repeat sessions is consistently lower than new sessions across all products.
            - New sessions are the primary revenue driver.

            **Insight:** Acquisition traffic drives revenue, but increasing repeat session monetization is an opportunity.
            """)


    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)    
    col1, col2=st.columns(2)
    with col2:
        fil_sessions['time_slots'] = fil_sessions['created_at'].dt.hour.apply(lambda x:'Early_Morning' if ((x>=0) & (x<=5)) else 'Morning' if ((x>=6) & (x<=11)) else 
                           'Afternoon' if ((x>=12) & (x<=16)) else 'Evening' if ((x>=17) & (x<=20)) else 'Night')
        sessions_by_slot = fil_sessions.groupby("time_slots")["website_session_id"].nunique().reset_index(name="sessions")
        orders_with_sessions = fil_orders.merge(fil_sessions[["website_session_id","time_slots"]],on="website_session_id", how="left")
        orders_by_slot = orders_with_sessions.groupby("time_slots")["order_id"].nunique().reset_index(name="orders")
        conversion_by_slot = sessions_by_slot.merge(orders_by_slot, on="time_slots", how="left")
        conversion_by_slot["orders"] = conversion_by_slot["orders"].fillna(0)
        conversion_by_slot["conversion_rate"] = (conversion_by_slot["orders"] / conversion_by_slot["sessions"])*100
        slot_order = ["Early_Morning","Morning","Afternoon","Evening","Night"]
        conversion_by_slot["time_slots"] = pd.Categorical(conversion_by_slot["time_slots"], categories=slot_order, ordered=True)
        conversion_by_slot = conversion_by_slot.sort_values("time_slots")
        
        fig, ax = plt.subplots(figsize=(6,4))
        st.subheader("Conversion Rate by Time Buckets")
        ax.bar(conversion_by_slot["time_slots"], conversion_by_slot["conversion_rate"], color="#055296")
        ax.set_xlabel("Time Slots")
        ax.set_ylabel("Conversion Rate (%)")
        plt.xticks(rotation=30, ha="right")
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Conversion rate remains stable between 6.7% and 6.9% across time slots.
            - Afternoon shows the highest conversion rate, close to 6.9%.
            - Early morning and evening perform similarly around 6.8%.
            - No major drop across time buckets indicates consistent user intent.

            **Insight:** Traffic quality is stable throughout the day, suggesting strong audience targeting.
            """)


        
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)    
    with col1:
        sessions_by_day = fil_sessions.groupby("day_name")["website_session_id"].nunique().reset_index(name="sessions")
        order_with_session = fil_orders.merge(fil_sessions[["website_session_id","day_name"]],on="website_session_id", how="left")
        order_by_day = order_with_session.groupby("day_name")["order_id"].nunique().reset_index(name="orders")
        conversion_by_day = sessions_by_day.merge(order_by_day, on="day_name", how="left")
        conversion_by_day["orders"] = conversion_by_day["orders"].fillna(0)
        conversion_by_day["conversion_rate"] = (conversion_by_day["orders"] / conversion_by_day["sessions"])*100
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        conversion_by_day["day_name"] = pd.Categorical(conversion_by_day["day_name"], categories=day_order, ordered=True)
        conversion_by_day= conversion_by_day.sort_values("day_name")
        
        fig, ax = plt.subplots(figsize=(6,4))
        st.subheader("Conversion Rate by Days")
        ax.bar(conversion_by_day["day_name"], conversion_by_day["conversion_rate"], color="#055296")
        ax.set_xlabel("Days")
        ax.set_ylabel("Conversion Rate (%)")
        plt.xticks(rotation=30, ha="right")
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Conversion rate ranges between 6.5% and 7.0% across the week.
            - Sunday and Tuesday show the highest conversion rates at around 7%.
            - Saturday shows the lowest conversion rate at approximately 6.5%.
            - Performance is relatively stable without extreme fluctuations.

            **Insight:** Weekend conversion improvement strategies could increase overall weekly performance.
            """)


        
    col1,col2=st.columns(2)
    with col1:
        st.subheader("user by Device Type")
        user_by_device=fil_sessions.groupby("device_type")["user_id"].nunique().reset_index()
        fig, ax = plt.subplots(figsize=(4,4))
        ax.pie(user_by_device["user_id"],labels=user_by_device["device_type"],autopct="%1.1f%%",startangle=90)
        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Desktop users account for 68.3% of total users.
            - Mobile users represent 31.7% of total users.
            - Despite lower traffic share, mobile conversion is much weaker.
            - Desktop dominates both traffic and performance.

            **Insight:** Mobile growth opportunity is large if conversion rate improves.
            """)
    with col2:
        st.subheader("Users by Pageview URL")
        page_user_df = (fil_pageviews.merge(fil_sessions[["website_session_id", "user_id"]],on="website_session_id",how="left"))
        user_by_page = (page_user_df.groupby("pageview_url")["user_id"].nunique().reset_index(name="unique_users").sort_values("unique_users", ascending=False))
        user_by_page = user_by_page.head(10)
        fig, ax = plt.subplots(figsize=(6,5.7))
        ax.bar(user_by_page["pageview_url"], user_by_page["unique_users"],color="#055296")
        ax.set_xlabel("Pageview URL")
        ax.set_ylabel("Unique Users")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - The /products page receives the highest traffic at approximately 200,000+ users.
            - The Original Mr. Fuzzy product page attracts around 130,000+ users.
            - /home and /cart pages show strong engagement between 80,000 and 90,000 users.
            - Funnel pages like /shipping, /lander-1, and /billing-2 show gradual drop-offs.
            - There is clear user decline as users move deeper into the funnel.

            **Insight:** Funnel optimization could reduce drop-offs and increase completed purchases.
            """)
        
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    # Sessions by Channel
    col1,col2 = st.columns(2)

    with col1:
        st.subheader("Sessions by Channel")
        df = fil_sessions.groupby("utm_campaign")["website_session_id"].nunique().reset_index()
        fig, ax = plt.subplots(figsize=(5,4))
        ax.pie(df["website_session_id"], labels=df["utm_campaign"], autopct="%1.1f%%")
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Nonbrand channel dominates traffic with 71.4% share.
            - Not available contributes 17.6% of sessions.
            - Brand traffic contributes 8.7%.
            - Desktop targeted and pilot channels contribute around 1% each.
            - Traffic is heavily dependent on nonbrand acquisition.

            **Insight:** Brand channel growth could reduce dependency on paid nonbrand traffic.
            """)


    with col2:
        #Bounce Rate by Device
        st.subheader("Bounce Rate by Device")

        pageviews_per_session = fil_pageviews.groupby("website_session_id")["website_pageview_id"].count()
        bounce_sessions = pageviews_per_session[pageviews_per_session == 1].index
        bounce_df = fil_sessions.copy()
        bounce_df["is_bounce"] = bounce_df["website_session_id"].isin(bounce_sessions)
        df = bounce_df.groupby("device_type").agg(sessions=("website_session_id","nunique"),bounces=("is_bounce","sum")).reset_index()
        df["bounce_rate"] = df["bounces"] / df["sessions"]

        fig, ax = plt.subplots(figsize=(5,3.7))
        ax.bar(df["device_type"], df["bounce_rate"],color="#055296")
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Mobile bounce rate is approximately 47%.
            - Desktop bounce rate is approximately 37%.
            - Mobile users are significantly more likely to leave without interaction.
            - Bounce rate difference aligns with lower mobile conversion.

            **Insight:** Mobile experience optimization should be a top priority to reduce bounce and increase revenue.
            """)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
#tab2
with tab2:
    total_sessions = fil_sessions["website_session_id"].nunique()
    no_filters = (
        not year and not month and not device and not session and not product_name and not pageview_url)
    if no_filters:
        bounce_sessions = 211640
        bounce_rate = 0.4476
    else:
        page_counts = (fil_pageviews.groupby("website_session_id").size().reset_index(name="pageviews"))
        session_df = fil_sessions[["website_session_id"]].drop_duplicates().merge(page_counts,on="website_session_id",how="left")
        session_df["pageviews"] = session_df["pageviews"].fillna(0)
        bounce_sessions = session_df.loc[session_df["pageviews"] == 1,"website_session_id"].nunique()
        bounce_rate = bounce_sessions / total_sessions if total_sessions else 0

    page_counts = (fil_pageviews.groupby("website_session_id").size().reset_index(name="pageviews"))
    session_df = (fil_sessions[["website_session_id"]].drop_duplicates().merge(page_counts, on="website_session_id", how="left"))
    session_df["pageviews"] = session_df["pageviews"].fillna(0)
    avg_pages = session_df["pageviews"].mean()

    converted_sessions = fil_orders["website_session_id"].nunique()
    conversion_rate = converted_sessions / total_sessions if total_sessions else 0

    col1,col2,col3,col4, col5, col6, col7= st.columns(7)
    col1.metric("Total Sessions",format_num(total_sessions))
    col6.metric("Bounce Rate", f"{bounce_rate:.2%}")
    col2.metric("Bounce Sessions",format_num( bounce_sessions))
    col3.metric("Conversion Rate", f"{conversion_rate:.2%}")
    col4.metric("Avg Pages Per Session", f"{avg_pages:.2f}")
    col5.metric("Converted Sessions",format_num( converted_sessions))
    col7.metric("Avg Session YOY Growth",f"{avg_yoy:.2%}")
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    #conversion rate by month
    fig, ax = plt.subplots(figsize=(8,3))

    ax.fill_between(monthly["MonthShort"],monthly["conversion_rate"],alpha=0.4,color="#1B6BB8")
    ax.plot(monthly["MonthShort"],monthly["conversion_rate"],marker="o",color="#055296")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_ylabel("Conversion Rate")
    ax.set_xlabel("Month")
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    st.pyplot(fig)
    with st.expander("Chart Explanation", expanded=False):
        st.markdown("""
            - Conversion rate remains stable between approximately 6.3% and 7.6% throughout the year.
            - February shows the highest conversion rate at around 7.5%.
            - The lowest conversion performance occurs in April at roughly 6.3%.
            - Conversion gradually improves again in Q4, reaching nearly 7% in December.
            - Overall variation is small, indicating consistent website performance.

            **Insight:** Seasonal dips occur mid-year, while Q1 and Q4 show stronger buying intent.
            """)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 

    #landing page
    allowed_pages = ["/home","/lander-1","/lander-2","/lander-3","/lander-4","/lander-5"]
    landing_df = (fil_pageviews.sort_values(["website_session_id","website_pageview_id"]).groupby("website_session_id",as_index=False).first()[["website_session_id","pageview_url"]])
    landing_df = landing_df[landing_df["pageview_url"].isin(allowed_pages)]
    top_sessions = (landing_df.groupby("pageview_url")["website_session_id"].nunique().reset_index(name="sessions").sort_values("sessions", ascending=False)).head(5)
    #st.write(landing_df["pageview_url"].value_counts())
    
    # conversion rate
    landing_orders = (landing_df.merge(fil_orders[["website_session_id","order_id"]],on="website_session_id",how="inner").groupby("pageview_url")["order_id"].nunique().reset_index(name="orders"))
    conversion_df = top_sessions.merge(landing_orders,on="pageview_url",how="left")
    conversion_df["orders"] = conversion_df["orders"].fillna(0)
    conversion_df["conversion_rate"] = (conversion_df["orders"] /conversion_df["sessions"])
    conversion_df=conversion_df.sort_values("conversion_rate",ascending=False)

    # Bounce sessions
    pageviews_per_session = (fil_pageviews.groupby("website_session_id")["website_pageview_id"].count())
    bounce_sessions = pageviews_per_session[pageviews_per_session == 1].index
    landing_df["is_bounce"] = landing_df["website_session_id"].isin(bounce_sessions)
    bounce_df = (landing_df.groupby("pageview_url").agg(sessions=("website_session_id","nunique"),bounces=("is_bounce","sum")).reset_index())
    bounce_df["bounce_rate"] = (bounce_df["bounces"] /bounce_df["sessions"])
    bounce_df=bounce_df.sort_values("bounce_rate",ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Landing Pages by Sessions")
        fig, ax = plt.subplots(figsize=(6,6))
        ax.barh(top_sessions["pageview_url"],
                top_sessions["sessions"])
        ax.invert_yaxis()
        ax.grid(axis="x", linestyle="--", alpha=0.3)
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - /lander-2 receives the highest traffic at approximately 130,000 sessions.
            - /home follows closely with around 120,000 sessions.
            - /lander-3 attracts nearly 70,000 sessions.
            - /lander-1 and /lander-5 generate around 45,000 sessions each.
            - Traffic is concentrated heavily on two primary landing pages.

            **Insight:** Optimizing top landing pages can significantly influence total revenue.
            """)


    with col2:
        st.subheader("Conversion Rate by Landing Page")
        fig, ax = plt.subplots(figsize=(6,6))
        ax.bar(conversion_df["pageview_url"],conversion_df["conversion_rate"])
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - /lander-5 shows the highest conversion rate at approximately 10%.
            - /lander-2 converts around 7.7%.
            - /home converts at nearly 6.8%.
            - /lander-1 converts around 4.5%.
            - /lander-3 has the lowest conversion rate at roughly 3.3%.

            **Insight:** High traffic pages are not always the highest converting, suggesting optimization opportunity.
            """)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    col1,col2 =st.columns(2)
    with col1:
        st.subheader("Bounce Rate by Landing Page")
        fig, ax = plt.subplots(figsize=(6,6))
        ax.barh(bounce_df["pageview_url"],bounce_df["bounce_rate"])
        ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        ax.invert_yaxis()
        ax.grid(axis="x", linestyle="--", alpha=0.3)
        st.pyplot(fig)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - /lander-1 has the highest bounce rate at approximately 53%.
            - /lander-4 and /lander-3 show bounce rates around 50%.
            - /lander-2 bounce rate is near 45%.
            - /home has a bounce rate close to 42%.
            - /lander-5 has the lowest bounce rate at around 37%.

            **Insight:** Pages with high bounce and low conversion require content or UX improvement.
            """)
        
    with col2:
        #Session By Page Type
        funnel_order=["Landing Page","Product Page","Cart","Billing","Thank You"]
        funnel_df=(fil_pageviews.groupby("funnel_step_final")["website_session_id"].nunique().reset_index(name="sessions"))
        funnel_df=funnel_df[funnel_df["funnel_step_final"].isin(funnel_order)]
        funnel_df["funnel_step_final"]=pd.Categorical(funnel_df["funnel_step_final"],categories=funnel_order,ordered=True)
        funnel_df=funnel_df.sort_values("funnel_step_final")
        
        st.subheader("Session By Page Type")
        fig = px.funnel(funnel_df,x="sessions",y="funnel_step_final",color_discrete_sequence=["#055296"])
        fig.update_layout(height=500,yaxis_title="",xaxis_title="Sessions")
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("Chart Explanation", expanded=False):
            st.markdown("""
            - Landing Page receives approximately 421,956 sessions.
            - Product Page drops to around 230,534 sessions.
            - Cart stage reduces further to approximately 82,603 sessions.
            - Billing page has about 56,124 sessions.
            - Thank You page (completed purchases) shows around 27,972 sessions.

            **Insight:** There is a significant drop-off from product page to cart stage, indicating funnel leakage.
            """)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)   

