import os
from api.sarvam_api import SarvamAPI
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_classic.chains import LLMChain
from langchain_classic.memory import ConversationBufferMemory
from dotenv import load_dotenv
import streamlit as st 
import streamlit_authenticator as stauth
from database.user_progress_db import UserProgressDB
    
load_dotenv()
sarvam_api = SarvamAPI()
llm = ChatOpenAI()
db = UserProgressDB()

# Page config
st.set_page_config(
    page_title="Language Learning Tutor",
    page_icon="🎓",
    layout="wide"
)

def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'memory' not in st.session_state:
        st.session_state.memory = ConversationBufferMemory()
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


def creds_entered():
    if db.check_user(st.session_state.user, st.session_state.passwd):
        st.session_state.authenticated = True
        st.session_state.user_id = db.get_user_id(st.session_state.user)
        st.session_state.prompt_id = db.get_user_progress(st.session_state.user_id) or 1
        return True
    else:
        st.session_state.authenticated = False
        st.error("Username/password is incorrect")
        return False
def authentication():
    st.text_input(label="Name: ",value="",key="user")
    st.text_input(label="Password",value="",key="passwd",type="password")
    st.button("Login",on_click=creds_entered)


def init_prompts():
    lesson_prompt = PromptTemplate(
    input_variables=["level", "stage", "prompt", "language"],
    template="""
You are a tutor helping a {level}-level and {stage}-stage {language} learner.
Give the lesson: {prompt} to the user.

Start with what we're going to be learning today: {prompt}
Then explain what {prompt} means in {language}, using the native script of {language}.
Tell the user how to reply to the prompt in English, using the native script.
Then ask the user in {language}, using the native script, to respond in English to the prompt.
Everything should be written in the {language} language and script except the English prompt.
"""
)


    tutor_prompt = PromptTemplate(
    input_variables=["level", "stage", "prompt", "notes_for_ai", "input", "language"],
    template="""
You are an English tutor for a {level}-level, {stage}-stage learner who speaks {language}. 
Lesson: "{prompt}"
Notes: {notes_for_ai}
User said (in {language}): "{input}"

Instructions:
1. Interpret what the user meant.
2. Correct their English sentence if needed (show only the correction).
3. Explain the correction in {language} if needed, using native script.
4. Give feedback and guide them to respond naturally, in {language}, using native script.
5. If the sentence means something different, explain in {language} what they said and be strict about the meaning.
Keep everything in {language} except the corrected English sentence.
"""
)


    evaluation_prompt = PromptTemplate(
        input_variables=["level", "stage", "feedback", "expected_response", "user_response", "language"],
        template="""
Evaluate a {level}-level and {stage}-stage English learner who speaks {language}.

Feedback: {feedback}
Expected Response (in English): {expected_response}
User's Response : {user_response}

Steps:
1. Give a similarity score based on expected response and user response between 0.0 to 1.0.
2. If score >= 0.6, add "LESSON_COMPLETE" to end.

Return only the score.
"""
    )
    
    return lesson_prompt, tutor_prompt, evaluation_prompt

def init_apis_and_chains():    
    lesson_prompt, tutor_prompt, evaluation_prompt = init_prompts()
    
    lesson_chain = LLMChain(llm=llm, prompt=lesson_prompt)
    evaluation_chain = LLMChain(llm=llm, prompt=evaluation_prompt)
    tutor_chain = LLMChain(llm=llm, prompt=tutor_prompt)
    
    return sarvam_api, db, lesson_chain, evaluation_chain, tutor_chain

def get_user_data(db, user_id):
    language = db.get_user_language(user_id)
    stage = db.get_user_level_and_stage(user_id)[0]
    level = db.get_user_level_and_stage(user_id)[1]
    return language, stage, level

def updateUserLevelAndStage():
    level, stage, language = db.get_user_level_stage_language(st.session_state.user_id)
    db.update_user_level_and_stage(st.session_state.user_id, level, stage)

def start_lesson(db, lesson_chain, prompt_id, level, stage, language):
    prompt = db.get_prompt(prompt_id)
    
    lesson = lesson_chain.run(
        level=level,
        stage=stage,
        prompt=prompt,
        language=language
    )
    
    return lesson
    

def save_audio():
    audio_value = st.audio_input("Record your response", sample_rate=44100,width="stretch")
    if audio_value is not None:
        with open("temp.wav", "wb") as f:
            f.write(audio_value.getbuffer())
            return True
    return False

def expectedResponseAudio():
    expected_response = db.get_expected_response(st.session_state.prompt_id)
    print(expected_response)
    audio_bytes = sarvam_api.text_to_speech(expected_response)
    st.audio(audio_bytes, format="audio/wav")

def process_response(sarvam_api, db, tutor_chain, evaluation_chain, prompt_id, level, stage, language, threshold):
    prompt = db.get_prompt(prompt_id)
    notes_for_ai = db.get_notes(prompt_id)
    
    # Get transcription
    full_path = os.path.abspath("temp.wav")
    user_input = sarvam_api.speech_to_text(full_path)
    print(user_input)
    expected_response = db.get_expected_response(prompt_id)
    
    # Get feedback
    feedback = tutor_chain.run(
        level=level,
        stage=stage,    
        prompt=prompt,  
        notes_for_ai=notes_for_ai,
        input=user_input,
        expected_response=expected_response,
        language=language,
    )
    
    # Evaluate
    score_result = evaluation_chain.run(
        level=level,
        stage=stage,
        feedback=feedback,
        expected_response=expected_response,
        user_response=user_input,
        language=language
    )
    
    # Parse score
    try:
        score = float(score_result.split()[0])
    except:
        score = 0.0
    
    lesson_complete = score >= threshold
    
    return {
        'user_input': user_input,
        'feedback': feedback,
        'score': score,
        'lesson_complete': lesson_complete
    }

def reset_lesson_state():
    st.session_state.lesson_started = False
    st.session_state.current_lesson = None
    st.session_state.audio_saved = False
    st.session_state.show_feedback = False
    st.session_state.feedback_data = {}

def main():
    init_session_state()
    st.title("Welcome to LangOdyssey! Please authenticate yourself.")
    if not st.session_state.authenticated:
        authentication()
        return
    sarvam_api, db, lesson_chain, evaluation_chain, tutor_chain = init_apis_and_chains()
    level, stage, language = db.get_user_level_stage_language(st.session_state.user_id)
    threshold = 0.6

    if(st.session_state.prompt_id % 26 ==0):
        st.success("🎉 Congratulations! You have completed all lessons in this stage." \
        "You will be advanced to the next stage.")
    
    if(st.session_state.prompt_id % 101 ==0):
        st.success("🎉 Congratulations! You have completed all stages in this level." \
        "You will be advanced to the next level.")
    
    # UI Layout
    st.title("🎓 Language Learning Tutor")
    st.markdown(f"**Level:** {level} | **Stage:** {stage} | **Language:** {language}")
    st.divider()
    
    # Sidebar for controls
    with st.sidebar:
        st.header("📊 Progress")
        st.metric("Current Lesson", st.session_state.prompt_id)
        st.metric("Threshold Score", f"{threshold:.1f}")
        
        if st.button("🔄 Reset Session", use_container_width=True):
            reset_lesson_state()
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📚 Lesson Area")
        
        # Start lesson button
        if not st.session_state.lesson_started:
            if st.button("▶️ Start Lesson", type="primary", use_container_width=True):
                with st.spinner("Preparing lesson..."):
                    lesson = start_lesson(db, lesson_chain, st.session_state.prompt_id, level, stage, language)
                
                st.session_state.current_lesson = lesson
                st.session_state.lesson_started = True
                st.rerun()
        
        # Display current lesson
        if st.session_state.current_lesson:
            st.info("🎯 **Current Lesson:**")
            st.write(st.session_state.current_lesson)
            st.markdown("### " + sarvam_api.translate_text("Expected Response Audio", target_language="hi"))
            expectedResponseAudio()
    
    with col2:
        st.subheader("🎤 Audio Recording")
        if save_audio():
            st.session_state.audio_saved = True
            st.success("✅ Audio saved!")
        else:
            st.session_state.audio_saved = False
            st.warning("⚠️ No audio recorded")
    
    # Process response section
    if st.session_state.lesson_started and st.session_state.audio_saved and not st.session_state.show_feedback:
        st.divider()
        st.subheader("📝 Submit Your Response")
        
        if st.button("🚀 Process My Response", type="primary", use_container_width=True):
            with st.spinner("Processing your response..."):
                feedback_data = process_response(
                    sarvam_api, db, tutor_chain, evaluation_chain, 
                    st.session_state.prompt_id, level, stage, language, threshold
                )
            
            st.session_state.feedback_data = feedback_data
            st.session_state.show_feedback = True
            st.rerun()
    
    # Display feedback
    if st.session_state.show_feedback:
        st.divider()
        feedback_data = st.session_state.feedback_data  
        
        st.write("**You said:**", feedback_data['user_input'])
        st.write("**Feedback:**", feedback_data['feedback'])
        st.metric("Score", f"{feedback_data['score']:.2f}")
        
        # Check completion
        if feedback_data['lesson_complete']:
            st.success("🎉 Lesson Complete! Moving to next lesson...")
            st.balloons()
            
            if st.button("➡️ Continue to Next Lesson", type="primary", use_container_width=True):
                st.session_state.prompt_id += 1
                updateUserLevelAndStage()
                reset_lesson_state()
                st.rerun()
        else:
            st.warning("📖 Let's try that lesson again!")
            
            if st.button("🔄 Try Again", use_container_width=True):
                # Reset only for retry
                st.session_state.audio_saved = False
                st.session_state.show_feedback = False
                st.session_state.feedback_data = {}
                st.rerun()
    
    # Exit button
    if st.button("🚪 Exit Learning", type="primary"):
        db.update_user_progress(st.session_state.user_id, st.session_state.prompt_id)
        reset_lesson_state()
        st.session_state.authenticated = False
        st.success("You have exited the learning session. 👋")
        st.rerun()
    
    # Footer
    st.divider()
    st.caption("💡 Click 'Start Lesson' → Record your response → Save audio → Process response")

if __name__ == "__main__":
    main()