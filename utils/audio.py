import streamlit as st
from database.user_progress_db import UserProgressDB    
from api.sarvam_api import SarvamAPI

class Audio:
    def __init__(self):
        self.sarvam_api = SarvamAPI()
        self.db = UserProgressDB()
    def save_audio(self):
        audio_value = st.audio_input("Record your response", sample_rate=44100,width="stretch", key = f"audio_{st.session_state.prompt_id}")
        if audio_value is not None:
            with open("temp.wav", "wb") as f:
                f.write(audio_value.getbuffer())
                return True
        return False

    def expected_response_audio(self):
        expected_response = self.db.get_expected_response(st.session_state.prompt_id)
        audio_bytes = self.sarvam_api.text_to_speech(expected_response)
        st.audio(audio_bytes, format="audio/wav")