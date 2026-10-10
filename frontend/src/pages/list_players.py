"""
Streamlit page for listing all users.

Retrieves and displays a list of registered users in a table, excluding sensitive data like passwords.

Endpoint used:
    GET /player
"""

import pandas as pd
import streamlit as st

from utils.api_client import api_client
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

st.title("User list")
logger = get_page_logger("list_users")


check_authentification()

players = api_client.get("/user").get("data")

if players:
    if isinstance(players, list):
        df = pd.DataFrame(players)
        st.dataframe(df, hide_index=True)
    else:
        logger.info("No Users found.")
        st.info("No Users found.")


if st.button("Back to menu", type="primary"):
    st.switch_page("pages/user_menu.py")
