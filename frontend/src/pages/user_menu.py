"""
Streamlit page for the main user menu.

Gives access to the features of UserService: profile, user list and search,
account settings (update / delete) and, for administrators, user creation.
"""

import logging

import streamlit as st  # noqa: E402
from business_object.user import Administrator  # noqa: E402
from service.user_service import UserService  # noqa: E402

st.title("Main menu")
logger = logging.getLogger("user_menu")

# Remplace check_authentification()
session_user = st.session_state.get("user")
if session_user is None:
    st.warning("Please log in first.")
    if st.button("Go to login"):
        st.switch_page("pages/home.py")
    st.stop()

service = UserService()
user = service.find_by_username(session_user["username"])
if user is None:
    st.error("Your account no longer exists.")
    del st.session_state["user"]
    st.stop()
# On recharge l'utilisateur depuis la base pour avoir un vrai objet User
session_user = st.session_state.get("user")
user = service.find_by_username(session_user["username"])
if user is None:
    st.error("Your account no longer exists.")
    del st.session_state["user"]
    st.switch_page("pages/home.py")

is_admin = isinstance(user, Administrator)

st.badge(f"Hello {user.username}!", color="green")
if is_admin:
    st.badge("Administrator", color="orange")

tab_names = ["Profile", "Users", "Settings"]
if is_admin:
    tab_names.append("Admin")
tabs = st.tabs(tab_names)

# ---------------------------------------------------------------- Profile
with tabs[0]:
    st.subheader("My profile")
    st.write(f"**Id:** {user.id_user}")
    st.write(f"**Username:** {user.username}")
    st.write(f"**Email:** {getattr(user, 'email', '-')}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Play"):
            st.switch_page("pages/play_game.py")
    with col2:
        if st.button("Log out", type="primary"):
            logger.info("Log out")
            del st.session_state["user"]
            st.switch_page("pages/home.py")

# ------------------------------------------------------------------ Users
with tabs[1]:
    st.subheader("All users")
    users = service.list_all()
    st.dataframe(
        [{"id": u.id_user, "username": u.username} for u in users],
        use_container_width=True,
    )

    st.subheader("Search a user")
    search_mode = st.radio("Search by", ["Username", "Id"], horizontal=True)

    if search_mode == "Username":
        query = st.text_input("Username")
        if st.button("Search", key="search_username") and query:
            found = service.find_by_username(query)
            if found:
                st.success(f"Found: {found.username} (id {found.id_user})")
            else:
                st.warning("No user with this username.")
    else:
        query_id = st.number_input("Id", min_value=1, step=1)
        if st.button("Search", key="search_id"):
            found = service.find_by_id(int(query_id))
            if found:
                st.success(f"Found: {found.username} (id {found.id_user})")
            else:
                st.warning("No user with this id.")

# --------------------------------------------------------------- Settings
with tabs[2]:
    st.subheader("Update my account")
    with st.form("update_form"):
        new_username = st.text_input("Username", value=user.username)
        new_password = st.text_input("New password (leave empty to keep it)", type="password")
        confirm_password = st.text_input("Confirm new password", type="password")
        submitted = st.form_submit_button("Save changes")

    if submitted:
        old_username = user.username
        if new_password and new_password != confirm_password:
            st.error("The passwords do not match.")
        else:
            try:
                user.username = new_username
                service.update(user, new_password=new_password or None)
                st.session_state["user"]["username"] = new_username
                st.success("Account updated.")
            except ValueError as e:
                user.username = old_username  # on annule le changement en mémoire
                st.error(str(e))

    st.divider()
    st.subheader("Danger zone")
    confirm_delete = st.checkbox("I understand that deleting my account is permanent")
    if st.button("Delete my account", type="primary", disabled=not confirm_delete):
        if service.delete(user):
            logger.info("Account deleted")
            del st.session_state["user"]
            st.switch_page("pages/home.py")
        else:
            st.error("The account could not be deleted.")

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
            try:
                service.create(c_username, c_password, c_email, is_admin=c_is_admin)
                st.success(f"User {c_username} created.")
            except ValueError as e:
                st.error(str(e))
