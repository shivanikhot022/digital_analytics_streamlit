#importing the packges
import pandas as pd
import numpy as np
import os
import streamlit as st

@st.cache_data
def get_data():

    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, "data")

    # LOAD CSV FILES
    orders = pd.read_csv(os.path.join(data_path, "orders.csv"))
    order_items = pd.read_csv(os.path.join(data_path, "order_items.csv"))
    datetable=pd.read_csv(os.path.join(data_path,"datetable.csv"))
    products = pd.read_csv(os.path.join(data_path, "products.csv"))
    website_sessions = pd.read_csv(os.path.join(data_path, "website_sessions.csv"),nrows=200000)
    website_pageviews = pd.read_csv(os.path.join(data_path, "website_pageviews.csv"),nrows=200000,usecols=["website_pageview_id","created_at","website_session_id","pageview_url","funnel_step_final"],parse_dates=["created_at"])
    order_item_refunds = pd.read_csv(os.path.join(data_path, "order_item_refunds.csv"))
    customer_360 = pd.read_csv(os.path.join(data_path, "customer_360.csv"),usecols=["customer_id","customer_type","avg_order_value"])
    # MEMORY OPTIMIZATION
    for df in [orders, order_items, products, website_sessions, website_pageviews, order_item_refunds]:
        for col in df.select_dtypes(include=["int64"]).columns:
            df[col] = df[col].astype("int32")

        for col in df.select_dtypes(include=["float64"]).columns:
            df[col] = df[col].astype("float32")
    # DATE CONVERSIONS
    order_items["order_item_date"] = pd.to_datetime(order_items["order_item_date"], errors="coerce")
    order_items["order_item_time"] = pd.to_datetime(order_items["order_item_time"],  format='%H:%M:%S',errors="coerce")
    website_sessions["created_at"] = pd.to_datetime(website_sessions["created_at"], errors="coerce")
    website_pageviews["created_at"] = pd.to_datetime(website_pageviews["created_at"], errors="coerce")
    datetable["Date"] = pd.to_datetime(datetable["Date"], errors="coerce")

    # CREATE DATE COLUMNS (ORDER SIDE)
    order_items["Year"] = order_items["order_item_date"].dt.year
    order_items["Quarter"] = order_items["order_item_date"].dt.quarter
    order_items["MonthNumber"] = order_items["order_item_date"].dt.month
    order_items["MonthName"] = order_items["order_item_date"].dt.month_name()
    order_items["MonthShort"] = order_items["order_item_date"].dt.strftime("%b")
    order_items["DayName"] = order_items["order_item_date"].dt.day_name()
    order_items["hour"]=order_items["order_item_time"].dt.hour
    order_items["DayType"] = order_items["order_item_date"].dt.dayofweek.apply(
        lambda x: "Weekend" if x >= 5 else "Weekday"
    )
    # CREATE DATE COLUMNS
    website_sessions["session_date"] = website_sessions["created_at"].dt.date
    website_sessions["Year"] = website_sessions["created_at"].dt.year
    website_sessions["Quarter"] = website_sessions["created_at"].dt.quarter
    website_sessions["MonthNumber"] = website_sessions["created_at"].dt.month
    website_sessions["MonthName"] = website_sessions["created_at"].dt.month_name()
    website_sessions["MonthShort"] = website_sessions["created_at"].dt.strftime("%b")
    website_sessions["day_name"] = website_sessions["created_at"].dt.day_name()
    website_sessions["DayType"] = website_sessions["created_at"].dt.dayofweek.apply(lambda x: "Weekend" if x >= 5 else "Weekday")
    website_sessions["channel_type"] = np.select([website_sessions["utm_source"].isin(["gsearch", "bsearch"]),website_sessions["utm_source"] == "socialbook",website_sessions["utm_source"].isna() & website_sessions["http_referer"].str.contains("gsearch", na=False),website_sessions["utm_source"].isna() & website_sessions["http_referer"].str.contains("bsearch", na=False),website_sessions["utm_source"].isna() & website_sessions["http_referer"].str.contains("socialbook", na=False),],["Paid Search","Paid Social","Organic Search","Organic Search","Organic Social",],default="Direct")
    website_sessions["session_type"]=np.where(website_sessions["is_repeat_session"]==1,"Repeat_Session","New_Session")
    website_sessions["First Session Date"] =website_sessions.groupby("user_id")["created_at"].transform("min")
    website_sessions["days_since_first_session"] = ((website_sessions["created_at"].dt.normalize() )- (website_sessions["First Session Date"].dt.normalize())).dt.days
    def bin_days(days):
        if days == 0:
            return "0 days"
        elif days <= 3:
            return "1–3 days"
        elif days <= 7:
            return "4–7 days"
        elif days <= 14:
            return "8–14 days"
        elif days <= 30:
            return "15–30 days"
        else:
            return "30+ days"
    #creating the columns
    website_sessions["days_since_first_session_bin"] = website_sessions["days_since_first_session"].apply(bin_days)
    refund_map = order_item_refunds.set_index("order_item_id")["refund_amount_usd"]
    order_items["refund_amount_usd"] = order_items["order_item_id"].map(refund_map).fillna(0)
    order_items["order_item_refund_cost"] = np.where(order_items["refund_amount_usd"] > 0,order_items["cogs_usd"],0)
    order_items["total_net_revenue"] = order_items["price_usd"] - order_items["refund_amount_usd"]
    order_items["actual_cost"] = order_items["cogs_usd"] - order_items["order_item_refund_cost"]
    order_items["profit"] = order_items["total_net_revenue"] - order_items["actual_cost"]
    order_items["profit_margin"] = np.where(order_items["total_net_revenue"] != 0,order_items["profit"] / order_items["total_net_revenue"],0)
  #merging the datasets
    orders_fact = order_items.merge(orders[["order_id", "created_at","website_session_id", "user_id"]],on="order_id",how="left")
    orders_fact = orders_fact.merge(products,on="product_id",how="left")
    orders_fact = orders_fact.merge(customer_360,left_on="user_id",right_on="customer_id",how="left")
    #orders_fact=orders_fact.merge(datetable[["Date","Year"]],left_on="order_item_date",right_on="Date",how="right",suffixes=("","_dt"))

    sessions = website_sessions
    pageviews=website_pageviews
    #sessions = website_pageviews.merge(website_sessions,on="website_session_id",how="left")
    
    for df in [orders_fact, sessions,pageviews]:
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype("category")

    return {"orders_fact": orders_fact,"sessions": sessions,"pageviews":pageviews,"datetable":datetable}