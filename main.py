import os
import streamlit as st
from dotenv import load_dotenv

from api.sarvam_api import SarvamAPI
from components.auth.auth import Authentication
from components.ai.prompt_templates import PromptTemplates
from components.ai.chains import Chains
from components.session.session import Session
from components.ai.lesson_service import LessonService
from utils.audio import Audio
from database.user_progress_db import UserProgressDB


# Load environment variables
load_dotenv()

# Initialize components
audio = Audio()
chain = Chains()
session = Session()
lesson = LessonService()
lesson_chain, evaluation_chain, tutor_chain = chain.init_apis_and_chains()
prompt_templates = PromptTemplates()
auth = Authentication()
sarvam_api = SarvamAPI()
db = UserProgressDB()

# Streamlit page config
st.set_page_config(
    page_title="Language Learning Tutor",
    page_icon="🎓",
    layout="wide"
)


def main():
    session.init_session_state()

    if not st.session_state.authenticated:
        auth.authentication_form()
        return

    level, stage, language = db.get_user_level_stage_language(st.session_state.user_id)
    threshold = 0.6

    if st.session_state.prompt_id % 26 == 0:
        st.toast("🎉 Congratulations! You’ve completed all lessons in this stage. Advancing to the next stage.")
    
    if st.session_state.prompt_id % 101 == 0:
        st.toast("🎉 Great job! You’ve completed all stages in this level. Advancing to the next level.")
    
    # Page header
    st.title("🎓 Language Learning Tutor")
    st.markdown(f"**Level:** {level} | **Stage:** {stage} | **Language:** {language}")
    st.divider()

    # Sidebar
    with st.sidebar:
        st.header("📊 Progress")
        st.metric("Current Lesson", st.session_state.prompt_id)
        st.metric("Threshold Score", f"{threshold:.1f}")

        if st.button("🔄 Reset Session", use_container_width=True):
            session.reset_lesson_state()
            st.rerun()

    # Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📚 Lesson Area")

        if not st.session_state.lesson_started:
            if st.button("▶️ Start Lesson", type="primary", use_container_width=True):
                with st.spinner("Preparing lesson..."):
                    lesson_text = lesson.start_lesson(
                        st.session_state.prompt_id, level, stage, language
                    )

                st.session_state.current_lesson = lesson_text
                st.session_state.lesson_started = True
                st.rerun()

        if st.session_state.current_lesson:
            st.info("🎯 **Current Lesson:**")
            st.write(st.session_state.current_lesson)
            st.markdown("### " + sarvam_api.translate_text("Expected Response Audio", target_language="hi"))
            audio.expected_response_audio()

    with col2:
        st.subheader("🎤 Audio Recording")
        if audio.save_audio():
            st.session_state.audio_saved = True
            st.success("✅ Audio saved!")
        else:
            st.session_state.audio_saved = False
            st.warning("⚠️ No audio recorded")

    # Process response
    if (
        st.session_state.lesson_started
        and st.session_state.audio_saved
        and not st.session_state.show_feedback
    ):
        st.divider()
        st.subheader("📝 Submit Your Response")

        if st.button("🚀 Process My Response", type="primary", use_container_width=True):
            with st.spinner("Processing your response..."):
                feedback_data = lesson.process_response(
                    st.session_state.prompt_id, level, stage, language, threshold
                )

            st.session_state.feedback_data = feedback_data
            st.session_state.show_feedback = True

    # Feedback display
    if st.session_state.show_feedback:
        st.divider()
        feedback_data = st.session_state.feedback_data

        st.write("**You said:**", feedback_data['user_input'])
        st.write("**Feedback:**", feedback_data['feedback'])
        st.metric("Score", f"{feedback_data['score']:.2f}")

        if feedback_data['lesson_complete']:
            st.success("🎉 Lesson Complete! Moving to next lesson...")
            st.balloons()

            if st.button("➡️ Continue to Next Lesson", type="primary", use_container_width=True):
                st.session_state.prompt_id += 1
                db.update_user_level_and_stage(st.session_state.user_id, level, stage)
                session.reset_lesson_state()
                st.rerun()
        else:
            st.warning("📖 Let's try that lesson again!")
            if st.button("🔄 Try Again", use_container_width=True):
                st.session_state.audio_saved = False
                st.session_state.show_feedback = False
                st.session_state.feedback_data = {}
                
                st.rerun()

    # Exit button
    if st.button("🚪 Exit Learning", type="primary"):
        db.update_user_progress(st.session_state.user_id, st.session_state.prompt_id)
        session.reset_lesson_state()
        st.session_state.authenticated = False
        st.success("You have exited the learning session. 👋")
        st.rerun()

    st.divider()
    st.caption("💡 Click 'Start Lesson' → Record your response → Save audio → Process response")


if __name__ == "__main__":
    main()
