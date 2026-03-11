# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
# %%
from data_setup import get_data
data = get_data()
orders_fact = data["orders_fact"]
sessions = data["sessions"]
datetable=data["datetable"]
pageviews=data["pageviews"]
# %%
sessions["created_at"] = pd.to_datetime(sessions["created_at"])
sessions["Year"] = sessions["created_at"].dt.year
sessions["year_q"] = pd.to_datetime(sessions["created_at"]).dt.to_period("Q")
sessions[["created_at","Year","year_q"]].head()
page_session=pageviews.merge(sessions,on="website_session_id",how="left")
# %%
page_session.head()