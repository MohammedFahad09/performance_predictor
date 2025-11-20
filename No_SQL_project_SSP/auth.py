# auth.py
import streamlit as st
from db import get_users_collection, seed_default_users
from datetime import datetime



def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "role" not in st.session_state:
        st.session_state.role = None



def login_ui():
    """
    Renders login UI in sidebar. Allows selecting role (student/admin) for delegation.
    Auth checks username/password against users collection and selected role.
    """
    seed_default_users()
    users = get_users_collection()

    st.sidebar.header("🔐 Login")
    with st.sidebar.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        role = st.selectbox("Role", ["student", "admin"], key="login_role")
        submit = st.form_submit_button("Login")
    if submit:
        # simple check
        doc = users.find_one({"username": username, "role": role})
        if doc and doc.get("password") == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.sidebar.success(f"Logged in as {username} ({role})")
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials or role mismatch.")
            return False
    return st.session_state.logged_in



def logout_ui():
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()



def require_login_or_redirect():
    init_session_state()
    if not st.session_state.logged_in:
        login_ui()
        st.title("Please log in")
        st.info("Use the sidebar to login. ")
        st.stop()
    else:
        # show small current user info
        st.sidebar.write(f"👤 {st.session_state.username} ({st.session_state.role})")
        logout_ui()
