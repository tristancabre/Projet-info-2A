"""
Streamlit page for the main user menu.

Endpoints used (to adapt to the backend):
    GET    /users
    GET    /users/{id_user}
    PUT    /users/{id_user}
    DELETE /users/{id_user}
    POST   /users
"""

import streamlit as st

from utils.api_client import api_client
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

st.title("Main menu")
logger = get_page_logger("user_menu")
check_authentification()

user = st.session_state.get("user")
if user is None:
    st.warning("Session expired, please log in again.")
    st.switch_page("pages/home.py")
    st.stop()

is_admin = bool(user.get("is_admin"))
user_id = user.get("id_user")


def logout():
    logger.info("Log out")
    st.session_state.pop("user", None)
    st.switch_page("pages/home.py")


def api_error(response, default="Server error."):
    data = response.get("data")
    detail = data.get("detail") if isinstance(data, dict) else data
    st.error(detail or default)


st.badge(f"Hello {user['username']}!", color="green")
if is_admin:
    st.badge("Administrator", color="orange")

tab_names = ["Profile", "Users", "Settings"] + (["Admin"] if is_admin else [])
tabs = st.tabs(tab_names)

# ---------------------------------------------------------------- Profile
with tabs[0]:
    st.subheader("My profile")
    st.write(f"**Id:** {user_id}")
    st.write(f"**Username:** {user['username']}")
    if user.get("email"):
        st.write(f"**Email:** {user['email']}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Play"):
            st.switch_page("pages/play_game.py")
    with col2:
        if st.button("Log out", type="primary"):
            logout()

# ------------------------------------------------------------------ Users
with tabs[1]:
    st.subheader("All users")
    response = api_client.get("/users")
    users = response["data"] if response["status_code"] == 200 else []
    if response["status_code"] != 200:
        api_error(response, "Could not load the users.")
    st.dataframe(users, use_container_width=True)

    st.subheader("Search a user")
    search_mode = st.radio("Search by", ["Username", "Id"], horizontal=True)

    if search_mode == "Username":
        query = st.text_input("Username")
        if st.button("Search", key="search_username") and query:
            # filter on the list already loaded, no extra endpoint needed
            matches = [u for u in users if u.get("username") == query]
            if matches:
                st.success(f"Found: {matches[0]}")
            else:
                st.warning("No user with this username.")
    else:
        query_id = st.number_input("Id", min_value=1, step=1)
        if st.button("Search", key="search_id"):
            response = api_client.get(f"/users/{int(query_id)}")
            if response["status_code"] == 200:
                st.success(f"Found: {response['data']}")
            elif response["status_code"] == 404:
                st.warning("No user with this id.")
            else:
                api_error(response)

# --------------------------------------------------------------- Settings
with tabs[2]:
    st.subheader("Update my account")
    with st.form("update_form"):
        new_username = st.text_input("Username", value=user["username"])
        new_password = st.text_input("New password (leave empty to keep it)", type="password")
        confirm_password = st.text_input("Confirm new password", type="password")
        submitted = st.form_submit_button("Save changes")

    if submitted:
        if new_password and new_password != confirm_password:
            st.error("The passwords do not match.")
        else:
            body = {"username": new_username}
            if new_password:
                body["password"] = new_password
            response = api_client.put(f"/users/{user_id}", json=body)
            if response["status_code"] == 200:
                st.session_state["user"]["username"] = new_username
                st.success("Account updated.")
            else:
                api_error(response)

    st.divider()
    st.subheader("Danger zone")
    confirm_delete = st.checkbox("I understand that deleting my account is permanent")
    if st.button("Delete my account", type="primary", disabled=not confirm_delete):
        response = api_client.delete(f"/users/{user_id}")
        if response["status_code"] in (200, 204):
            logger.info("Account deleted")
            logout()
        else:
            api_error(response, "The account could not be deleted.")

# ------------------------------------------------------------------ Admin
if is_admin:
    with tabs[3]:
        st.subheader("Create a user")
        with st.form("create_form", clear_on_submit=True):
            c_username = st.text_input("Username")
            c_email = st.text_input("Email")
            c_password = st.text_input("Password", type="password")
            c_is_admin = st.checkbox("Administrator")
            created = st.form_submit_button("Create")

        if created:
            response = api_client.post(
                "/users",
                json={
                    "username": c_username,
                    "email": c_email,
                    "password": c_password,
                    "is_admin": c_is_admin,
                },
            )
            if response["status_code"] in (200, 201):
                st.success(f"User {c_username} created.")
            else:
                api_error(response)
