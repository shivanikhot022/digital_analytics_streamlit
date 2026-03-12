#import packages
import streamlit as st
import base64
import os

st.set_page_config(page_title="Login", layout="centered")

def set_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
#page background
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}

        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
        }}

        /* Make labels bigger & bold */
        label {{
            color: black !important;
            font-size: 18px !important;
            font-weight: bold !important;
        }}

        /* Make warning & error text bigger & bold */
        [data-testid="stAlert"] {{
            font-size: 18px !important;
            font-weight: bold !important;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

# IMAGE PATH
base_dir = os.path.dirname(__file__)
image_path = os.path.join(base_dir, "assets", "teady1.jpeg")
set_bg(image_path)

# TITLE 
st.markdown(
    "<h1 style='text-align:center;color:black;'>🧸 Digital Analytics Login</h1>",
    unsafe_allow_html=True
)

#  LOGIN LOGIC 
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# email and password set

email = st.text_input("Email ID")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if email and password == "scalar@123":
        st.session_state.logged_in = True
        st.success("Login Successful ✅")
        st.switch_page("pages/1_CEO.py")
    else:
        st.error("Invalid Email or Password ❌")
        