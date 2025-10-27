from langchain_core.prompts import PromptTemplate

class PromptTemplates:
    def __init__(self):
        pass    
    @staticmethod
    def init_prompts():
        lesson_prompt = PromptTemplate(
            input_variables=["level", "stage", "prompt", "language", "expected_user_response"],
            template="""
You are an English tutor for {language} speakers at {level} level.

Present the English phrase "{prompt}" to the learner. Explain what it means in {language} using native script. Show them how to respond in English with "{expected_user_response}". Then ask the learner in {language} (using native script) to practice responding in English.

Write everything in {language} native script except the English phrases being taught.
"""
        )

        tutor_prompt = PromptTemplate(
            input_variables=["level", "stage", "prompt", "notes_for_ai", "input", "language"],
            template="""
You are an English tutor for a {level} {stage} learner who speaks {language}.
Lesson: "{prompt}"
User said (in {language}): "{input}"

Instructions:
Give short, natural and constructive feedback in {language}, using native script.
Keep everything in {language}, except the English sentence.
"""
        )

        evaluation_prompt = PromptTemplate(
            input_variables=["level", "stage", "feedback", "expected_response", "user_response", "language"],
            template="""
Evaluate a {level}-level and {stage}-stage English learner who speaks {language}.

Feedback: {feedback}
Expected Response (in English): {expected_response}
User's Response: {user_response}

Steps:
1. Give a similarity score based on expected response and user response between 0.0 to 1.0.
2. If score >= 0.6, add "LESSON_COMPLETE" to end.

Return only the score.
"""
        )

        return lesson_prompt, tutor_prompt, evaluation_prompt
