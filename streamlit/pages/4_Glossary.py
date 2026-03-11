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

st.subheader("📖 KPI Glossary For CEO Dashboard")
col1 , col2=st.columns(2)
with col1:  
    with st.expander("📦 Total Orders"):
        st.write("**Meaning:** Total number of unique orders placed by customers.")
        st.write("**Formula:** COUNT(DISTINCT order_id)")
with col2: 
    with st.expander("💰 Total Revenue"):
        st.write("**Meaning:** Total revenue generated from all orders.")
        st.write("**Formula:** SUM(price_usd) - SUM(refund_amount_usd)")
col1 , col2=st.columns(2)
with col1:
    with st.expander("🌐 Total Sessions"):
        st.write("**Meaning:** Total number of website visits or sessions.")
        st.write("**Formula:** COUNT(DISTINCT website_session_id)")
with col2:
    with st.expander("📊 Profit Margin %"):
        st.write("**Meaning:** Percentage of profit earned from revenue.")
        st.write("**Formula:** (Total Profit / Total Revenue) * 100")
col1 , col2=st.columns(2)
with col1:
    with st.expander("🔁 Refund Rate %"):
        st.write("**Meaning:** Percentage of revenue refunded to customers.")
        st.write("**Formula:** (Total Refund Amount / Total Revenue) * 100")
with col2:
    with st.expander("👥 Repeat Customer %"):
        st.write("**Meaning:** Percentage of customers who placed more than one order.")
        st.write("**Formula:** (Customers with >1 orders / Total customers) * 100")
col1 , col2=st.columns(2)
with col1:
    with st.expander("🆕 One Time Customer %"):
        st.write("**Meaning:** Percentage of customers who placed only one order.")
        st.write("**Formula:** (Customers with 1 order / Total customers) * 100")
with col2:
    with st.expander("📈 Avg YoY Growth %"):
        st.write("**Meaning:** Average yearly growth rate of revenue.")
        st.write("**Formula:** (Current Year Revenue - Previous Year Revenue) / Previous Year Revenue")
col1 , col2=st.columns(2)
with col1:
    with st.expander("💵 Total Profit"):
        st.write("**Meaning:** Profit after subtracting cost from revenue.")
        st.write("**Formula:** Total Revenue - Total Cost")
with col2:
    with st.expander("💸 Total Cost"):
        st.write("**Meaning:** Total operational cost of fulfilling orders.")
        st.write("**Formula:** SUM(actual_cost) - SUM(order_item_refund_cost)")
col1 , col2=st.columns(2)
with col1:
    with st.expander("↩️ Total Refund"):
        st.write("**Meaning:** Total money refunded to customers.")
        st.write("**Formula:** SUM(refund_amount_usd)")
with col2:
    with st.expander("🛒 Average Order Value"):
        st.write("**Meaning:** Average revenue per order.")
        st.write("**Formula:** Total Revenue / Total Orders")
col1 , col2=st.columns(2)
with col1: 
    with st.expander("📊 Profit Margin %"):
        st.write("**Meaning:** Percentage of profit earned from revenue.")
        st.write("**Formula:** (Total Profit / Total Revenue) * 100")
with col2:
    with st.expander("📦 Refunded Item Cost"):
        st.write("**Meaning:** Total cost of items that were refunded.")
        st.write("**Formula:** SUM(order_item_refund_cost)")
col1 , col2=st.columns(2)
with col1:       
    with st.expander("📅 Profit Margin Last Year"):
        st.write("**Meaning:** Profit margin achieved in the previous year.")
        st.write("**Formula:** (Last Year Profit / Last Year Revenue) × 100")
with col2:
    with st.expander("📊 Average Profit YoY Growth %"):
        st.write("**Meaning:** Average yearly growth rate of profit margin.")
        st.write("**Formula:** ((Current Year Profit Margin - Last Year Profit Margin) / Last Year Profit Margin)")


st.subheader("📖 KPI Glossary For Marketing Manager Dashboard")
col1 , col2=st.columns(2)
with col1: 
    with st.expander("👥 Total Visitors"):
        st.write("**Meaning:** Total unique users who visited the website.")
        st.write("**Formula:** COUNT(DISTINCT user_id)")
with col2:
    with st.expander("🆕 New Visitors %"):
        st.write("**Meaning:** Percentage of visitors who came for the first time.")
        st.write("**Formula:** (New Visitors / Total Visitors) × 100")
col1 , col2=st.columns(2)
with col1: 
    with st.expander("📈 Conversion Rate %"):
        st.write("**Meaning:** Percentage of sessions that resulted in an order.")
        st.write("**Formula:** (Sessions with Orders / Total Sessions) × 100")
with col2:
    with st.expander("📊 Avg Session YoY Growth %"):
        st.write("**Meaning:** Average yearly growth rate of website sessions.")
        st.write("**Formula:** ((Current Year Sessions - Last Year Sessions) / Last Year Sessions)")
col1 , col2=st.columns(2)
with col1: 
    with st.expander("🏆 Top Channel by Session"):
        st.write("**Meaning:** Marketing channel that generated the highest number of sessions.")
        st.write("**Formula:** Channel with MAX(session count)")
with col2:
    with st.expander("🎯 Top Channel Conversion Rate"):
        st.write("**Meaning:** Percentage of sessions from the top channel that converted into orders.")
        st.write("**Formula:** (Orders from Channel / Sessions from Channel) × 100")
col1 , col2=st.columns(2)
with col1: 
    with st.expander("🆓 Free Channel Revenue"):
        st.write("**Meaning:** Revenue generated from free marketing channels like Direct or Organic Search.")
        st.write("**Formula:** SUM(revenue where channel in [Direct, Organic Search, Organic Social])")
with col2:
    with st.expander("💳 Paid Channel Revenue"):
        st.write("**Meaning:** Revenue generated from paid marketing campaigns.")
        st.write("**Formula:** SUM(revenue where channel in [Paid Search, Paid Social])")
col1 , col2=st.columns(2)
with col1: 
    with st.expander("👥 Repeat Visitors"):
        st.write("**Meaning:** Number of users who visited the website more than once.")
        st.write("**Formula:** COUNT(DISTINCT user_id where is_repeat_session = 1)")
with col2:
    with st.expander("🔁 Repeat Visitors %"):
        st.write("**Meaning:** Percentage of visitors who returned to the website.")
        st.write("**Formula:** (Repeat Visitors / Total Visitors) × 100")
col1 , col2=st.columns(2)
with col1: 
    with st.expander("🔁 Repeat Session Rate %"):
        st.write("**Meaning:** Percentage of sessions that are repeat visits.")
        st.write("**Formula:** (Repeat Sessions / Total Sessions) × 100")
with col2:
    with st.expander("📈 Avg Repeat Visitor YoY"):
        st.write("**Meaning:** Average yearly growth of repeat visitor sessions.")
        st.write("**Formula:** Mean of yearly session growth rates")
col1 , col2=st.columns(2)
with col1: 
    with st.expander("📅 Avg Days Since First Session"):
        st.write("**Meaning:** Average number of days since a user's first visit.")
        st.write("**Formula:** AVG(days_since_first_session)")
with col2:
    with st.expander("📢 Top Campaign by Repeat"):
        st.write("**Meaning:** Marketing campaign that generated the highest number of repeat visitors.")
        st.write("**Formula:** Campaign with MAX(repeat visitors)")



st.subheader("📖 KPI Glossary For Website Manager Dashboard")
col1 , col2=st.columns(2)
with col1: 
    with st.expander("🌐 Total Sessions"):
        st.write("**Meaning:** Total number of website visits.")
        st.write("**Formula:** COUNT(DISTINCT website_session_id)")
with col2:
    with st.expander("📦 Total Orders"):
        st.write("**Meaning:** Total number of orders placed.")
        st.write("**Formula:** COUNT(DISTINCT order_id)")
col1 , col2=st.columns(2)
with col1: 
    with st.expander("👥 Total Visitors"):
        st.write("**Meaning:** Total unique users who visited the website.")
        st.write("**Formula:** COUNT(DISTINCT user_id)")
with col2:
    with st.expander("💰 Revenue Per Session"):
        st.write("**Meaning:** Average revenue generated per website session.")
        st.write("**Formula:** Total Revenue / Total Sessions")
col1 , col2=st.columns(2)
with col1: 
    with st.expander("🆕 New Sessions"):
        st.write("**Meaning:** Sessions from users visiting the website for the first time.")
        st.write("**Formula:** COUNT(website_session_id where is_repeat_session = 0)")
with col2:
    with st.expander("🔁 Repeat Session %"):
        st.write("**Meaning:** Percentage of sessions that come from returning users.")
        st.write("**Formula:** (Repeat Sessions / Total Sessions) × 100")
col1 , col2=st.columns(2)
with col1: 
    with st.expander("👥 Repeat Visitors"):
        st.write("**Meaning:** Number of users who visited the website more than once.")
        st.write("**Formula:** COUNT(DISTINCT user_id where is_repeat_session = 1)")
with col2:
    with st.expander("📅 Session LY"):
        st.write("**Meaning:** Total sessions from the previous year.")
col1 , col2=st.columns(2)
with col1: 
    with st.expander("🚪 Bounce Sessions"):
        st.write("**Meaning:** Sessions where the user viewed only one page and left.")
        st.write("**Formula:** COUNT(session where pageviews = 1)")
with col2:
    with st.expander("⚠️ Bounce Rate"):
        st.write("**Meaning:** Percentage of sessions where users leave after viewing only one page.")
        st.write("**Formula:** (Bounce Sessions / Total Sessions) × 100")
col1 , col2=st.columns(2)
with col1: 
    with st.expander("📈 Conversion Rate"):
        st.write("**Meaning:** Percentage of sessions that resulted in an order.")
        st.write("**Formula:** (Converted Sessions / Total Sessions) × 100")
with col2:
    with st.expander("✅ Converted Sessions"):
        st.write("**Meaning:** Number of sessions that resulted in a purchase.")
        st.write("**Formula:** COUNT(DISTINCT website_session_id from orders)")
col1 , col2=st.columns(2)
with col1: 
    with st.expander("📄 Avg Pages Per Session"):
        st.write("**Meaning:** Average number of pages viewed in each session.")
        st.write("**Formula:** Total Pageviews / Total Sessions")
with col2:
    with st.expander("📊 Avg Session YoY Growth"):
        st.write("**Meaning:** Average yearly growth rate of sessions compared to the previous year.")
        st.write("**Formula:** ((Current Year Sessions - Last Year Sessions) / Last Year Sessions)")
        
