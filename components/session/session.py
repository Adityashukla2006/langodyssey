import streamlit as st 


class Session:
    def __init__(self):
        pass
    def init_session_state(self):
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'lesson_started' not in st.session_state:
            st.session_state.lesson_started = False
        if 'current_lesson' not in st.session_state:
            st.session_state.current_lesson = None
        if 'audio_saved' not in st.session_state:
            st.session_state.audio_saved = False
        if 'prompt_id' not in st.session_state:
            st.session_state.prompt_id = None
        if 'show_feedback' not in st.session_state:
            st.session_state.show_feedback = False
        if 'feedback_data' not in st.session_state:
            st.session_state.feedback_data = {}
    def reset_lesson_state(self):
        st.session_state.lesson_started = False
        st.session_state.current_lesson = None
        st.session_state.audio_saved = False
        st.session_state.show_feedback = False
        st.session_state.feedback_data = {}