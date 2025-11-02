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

db = UserProgressDB()

# Streamlit page config
st.set_page_config(
    page_title="Language Learning Tutor",
    page_icon="🎓",
    layout="wide"
)


def main():
    session.init_session_state()
    
    # Hide running indicator and prevent component fading
    # st.markdown("""
    #     <style>
    #     /* Hide running indicator */
    #     [data-testid="stStatusWidget"] {
    #         display: none !important;
    #     }
        
    #     /* Prevent component fading during reruns */
    #     .stApp [data-testid="stVerticalBlock"] > div {
    #         transition: none !important;
    #     }
        
    #     .stApp section[data-testid="stSidebar"] > div {
    #         transition: none !important;
    #     }
        
    #     /* Remove opacity changes during reruns */
    #     .stApp * {
    #         transition: opacity 0s !important;
    #     }
        
    #     /* Force full opacity at all times */
    #     .element-container {
    #         opacity: 1 !important;
    #     }
    #     </style>
    # """, unsafe_allow_html=True)

    if not st.session_state.authenticated:
        auth.authentication_form()
        return

    level, stage, language = db.get_user_level_stage_language(st.session_state.user_id)
    threshold = 0.6  
    sarvam_api = SarvamAPI(language)
    

    # Add loading states to session
    if 'is_loading_lesson' not in st.session_state:
        st.session_state.is_loading_lesson = False
    
    if 'is_processing_response' not in st.session_state:
        st.session_state.is_processing_response = False
    
    # Only show toast if we're viewing the lesson after completion
    if st.session_state.prompt_id != st.session_state.last_toast_prompt:
        if st.session_state.prompt_id > 0:
            if st.session_state.prompt_id % 101 == 0:
                st.toast(sarvam_api.t("🎉 Great job! You've completed all stages in this level. Advancing to the next level."))
                st.session_state.last_toast_prompt = st.session_state.prompt_id
            elif st.session_state.prompt_id % 26 == 0:
                st.toast(sarvam_api.t("🎉 Congratulations! You've completed all lessons in this stage. Advancing to the next stage."))
                st.session_state.last_toast_prompt = st.session_state.prompt_id

    
    # Page header
    st.title("🎓 LangOdyssey")
    st.markdown(f"**{sarvam_api.t('Level')}:** {level} | **{sarvam_api.t('Stage')}:** {stage} | **{sarvam_api.t('Language')}:** {language}")
    
    # Instructions for user
    st.info(sarvam_api.t("📋 How to use: Click 'Start Lesson' to begin → Listen to the lesson → Record your response → Click 'Save Audio' → Click 'Process My Response' to get feedback"))
    
    st.divider()

    # Sidebar
    with st.sidebar:
        st.header(sarvam_api.t("📊 Progress"))
        st.metric(sarvam_api.t("Current Lesson"), st.session_state.prompt_id)
        st.metric(sarvam_api.t("Threshold Score"), f"{threshold:.1f}")

        if st.button(sarvam_api.t("🔄 Reset Session"), use_container_width=True, key="reset_session"):
            session.reset_lesson_state()
            st.session_state.is_loading_lesson = False
            st.session_state.is_processing_response = False
            st.rerun()

    # Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(sarvam_api.t("📚 Lesson Area"))
        
        # Use a placeholder to prevent flashing
        lesson_area = st.empty()

        # Show Start Lesson button
        if not st.session_state.lesson_started and not st.session_state.is_loading_lesson:
            with lesson_area.container():
                if st.button(sarvam_api.t("▶️ Start Lesson"), type="primary", use_container_width=True, key="start_lesson"):
                    st.session_state.is_loading_lesson = True
                    st.rerun()
        
        # Load lesson after button click
        if st.session_state.is_loading_lesson and not st.session_state.lesson_started:
            with lesson_area.container():
                with st.spinner(sarvam_api.t("Preparing lesson...")):
                    try:
                        lesson_text = lesson.start_lesson(
                            st.session_state.prompt_id, level, stage, language
                        )
                        if lesson_text:
                            st.session_state.current_lesson = lesson_text
                            st.session_state.lesson_started = True
                            st.session_state.is_loading_lesson = False
                            st.rerun()
                        else:
                            st.error(sarvam_api.t("❌ Failed to load lesson. Please try again."))
                            st.session_state.is_loading_lesson = False
                    except Exception as e:
                        st.error(f"❌ {sarvam_api.t('Error loading lesson')}: {e}")
                        st.session_state.is_loading_lesson = False
                        import traceback
                        st.text(traceback.format_exc())
        
        # Display lesson content
        elif st.session_state.current_lesson and st.session_state.lesson_started:
            with lesson_area.container():
                st.info(f"🎯 **{sarvam_api.t('Current Lesson')}:**")
                st.write(st.session_state.current_lesson)
                
                # Only show expected response audio if not showing feedback
                if not st.session_state.show_feedback:
                    st.markdown("### " + sarvam_api.t("Expected Response Audio"))
                    try:
                        audio.expected_response_audio()
                    except Exception as e:
                        st.warning(f"⚠️ {sarvam_api.t('Could not load audio')}: {e}")

    with col2:
        st.subheader(sarvam_api.t("🎤 Audio Recording"))
    
    # Create a stable placeholder to prevent ghosting
        audio_placeholder = st.empty()
        status_placeholder = st.empty()
    
    # Only show audio recorder if lesson has started and not processing/showing feedback
        if (st.session_state.lesson_started 
            and not st.session_state.is_processing_response 
            and not st.session_state.show_feedback):
        
            with audio_placeholder:
                audio_result = audio.save_audio()
        
        # Show status after recording attempt
            if audio_result:
                st.session_state.audio_saved = True
                with status_placeholder:
                    st.success(sarvam_api.t("✅ Audio saved!"))
            elif st.session_state.lesson_started:  # Only show warning if lesson is active
                st.session_state.audio_saved = False
                with status_placeholder:
                    st.warning(sarvam_api.t("⚠️ No audio recorded"))
    
    # Show "Recording complete" ONLY during processing or feedback
        elif (st.session_state.audio_saved 
            and (st.session_state.is_processing_response or st.session_state.show_feedback)):
        # Clear the audio placeholder
            audio_placeholder.empty()
            with status_placeholder:
                st.info(sarvam_api.t("🎤 Recording complete"))

    # Process response button - only show when NOT processing
    # Show button only when not processing
    if (
        st.session_state.lesson_started
        and st.session_state.audio_saved
        and not st.session_state.show_feedback
        and not st.session_state.is_processing_response
    ):
        st.divider()
        st.subheader(sarvam_api.t("📝 Submit Your Response"))

        if st.button(
            sarvam_api.t("🚀 Process My Response"), 
            type="primary", 
            use_container_width=True, 
            key="process_response_btn"
        ):
            # Set flag and rerun to hide button and show spinner
            st.session_state.is_processing_response = True
            st.rerun()

# Show spinner when processing (button will be hidden)
    elif (
        st.session_state.lesson_started
        and st.session_state.audio_saved
        and not st.session_state.show_feedback
        and st.session_state.is_processing_response
    ):
        st.divider()
        st.subheader(sarvam_api.t("📝 Submit Your Response"))
    
        with st.spinner(sarvam_api.t("Processing your response...")):
            try:
                feedback_data = lesson.process_response(
                st.session_state.prompt_id, level, stage, language, threshold
                )
                st.session_state.feedback_data = feedback_data
                st.session_state.show_feedback = True
                st.session_state.is_processing_response = False
                st.rerun()
            except Exception as e:
                st.session_state.is_processing_response = False
                st.error(f"❌ {sarvam_api.t('Error during response processing')}: {e}")
                import traceback
                st.text(traceback.format_exc())

    # Feedback display
    if st.session_state.show_feedback and st.session_state.feedback_data:
        st.divider()
        feedback_data = st.session_state.feedback_data

        st.write(f"**{sarvam_api.t('You said')}:**", feedback_data['user_input'])
        st.write(f"**{sarvam_api.t('Feedback')}:**", feedback_data['feedback'])
        st.metric(sarvam_api.t("Score"), f"{feedback_data['score']:.2f}")

        if feedback_data['lesson_complete']:
            st.success(sarvam_api.t("🎉 Lesson Complete! Moving to next lesson..."))
            st.balloons()

            if st.button(sarvam_api.t("➡️ Continue to Next Lesson"), type="primary", use_container_width=True, key="continue_lesson"):
                # Update progress and move to next lesson
                st.session_state.prompt_id += 1
                db.update_user_level_and_stage(st.session_state.user_id, level, stage)
                session.reset_lesson_state()
                st.session_state.is_loading_lesson = False
                st.session_state.is_processing_response = False
                st.rerun()
        else:
            st.warning(sarvam_api.t("📖 Let's try that lesson again!"))
            if st.button(sarvam_api.t("🔄 Try Again"), use_container_width=True, key="try_again"):
                # Reset only the necessary states for retry
                st.session_state.audio_saved = False
                st.session_state.show_feedback = False
                st.session_state.feedback_data = {}
                st.session_state.is_processing_response = False
                st.rerun()

    # Exit button
    if st.button(sarvam_api.t("🚪 Exit Learning"), type="primary", key="exit_learning"):
        db.update_user_progress(st.session_state.user_id, st.session_state.prompt_id)
        session.reset_lesson_state()
        st.session_state.authenticated = False
        st.session_state.is_loading_lesson = False
        st.session_state.is_processing_response = False
        st.success(sarvam_api.t("You have exited the learning session. 👋"))
        st.rerun()

    st.divider()
    st.caption(sarvam_api.t("💡 Click 'Start Lesson' → Record your response → Save audio → Process response"))


if __name__ == "__main__":
    main()