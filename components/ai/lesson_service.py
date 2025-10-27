import os
from database.user_progress_db import UserProgressDB
from components.ai.chains import Chains
from api.sarvam_api import SarvamAPI

class LessonService:
    def __init__(self):
        self.db = UserProgressDB()
        self.chain = Chains()
        lesson_chain, evaluation_chain, tutor_chain = self.chain.init_apis_and_chains()
        self.lesson_chain = lesson_chain  # fixed typo: lesson_chainchain → lesson_chain
        self.evaluation_chain = evaluation_chain
        self.tutor_chain = tutor_chain
        self.sarvam_api = SarvamAPI()

    def start_lesson(self, prompt_id, level, stage, language):
        prompt = self.db.get_prompt(prompt_id)
        expected_user_response = self.db.get_expected_response(prompt_id)

        lesson = self.lesson_chain.run(
            level=level,
            stage=stage,
            prompt=prompt,
            language=language,
            expected_user_response=expected_user_response
        )

        return lesson

    def process_response(self, prompt_id, level, stage, language, threshold):
        prompt = self.db.get_prompt(prompt_id)
        notes_for_ai = self.db.get_notes(prompt_id)

        # Get transcription
        full_path = os.path.abspath("temp.wav")
        user_input = self.sarvam_api.speech_to_text(full_path)
        expected_response = self.db.get_expected_response(prompt_id)

        # Get feedback
        feedback = self.tutor_chain.run(
            level=level,
            stage=stage,
            prompt=prompt,
            notes_for_ai=notes_for_ai,
            input=user_input,
            expected_response=expected_response,
            language=language,
        )

        # Evaluate
        score_result = self.evaluation_chain.run(
            level=level,
            stage=stage,
            feedback=feedback,
            expected_response=expected_response,
            user_response=user_input,
            language=language,
        )

        # Parse score
        try:
            score = float(score_result.split()[0])
        except Exception:
            score = 0.0

        lesson_complete = score >= threshold

        return {
            'user_input': user_input,
            'feedback': feedback,
            'score': score,
            'lesson_complete': lesson_complete
        }
