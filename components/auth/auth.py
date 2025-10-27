import streamlit as st
from database.user_progress_db import UserProgressDB



class Authentication:
    def __init__(self):
        self.db = UserProgressDB()

    def creds_entered(self):
        if self.db.check_user(st.session_state.user, st.session_state.passwd):
            st.session_state.authenticated = True
            st.session_state.user_id = self.db.get_user_id(st.session_state.user)
            st.session_state.prompt_id = self.db.get_user_progress(st.session_state.user_id) or 1
            return True
        else:
            st.session_state.authenticated = False
            st.error("Username/password is incorrect")
            return False
    def authentication_form(self):
        st.title("Welcome to LangOdyssey! Please authenticate yourself.")
        st.text_input(label="Name: ",value="",key="user")
        st.text_input(label="Password",value="",key="passwd",type="password")
        st.button("Login",on_click=self.creds_entered)