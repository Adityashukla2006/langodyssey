import os
import requests
import base64
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class SarvamAPI:
    """Client for Sarvam AI's text-to-speech and speech-to-text APIs"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Sarvam API client"""
        self.api_key = api_key or os.getenv("SARVAM_API_KEY")
        if not self.api_key:
            raise ValueError("Sarvam API key is required. Set SARVAM_API_KEY in .env file or pass it to the constructor.")
        
        self.tts_url = "https://api.sarvam.ai/text-to-speech"
        self.stt_url = "https://api.sarvam.ai/speech-to-text"
        
    
    def text_to_speech(self, text: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert text to speech using Sarvam's TTS API
        
        Args:
            text: The text to convert to speech
            output_path: Optional path to save the audio file
            
        Returns:
            Dictionary with audio data and file path if saved
        """
        payload = {
            "input": text,
        }
        headers = {
            "api-subscription-key":os.getenv("SARVAM_API_KEY")
        }
        
        try:
            response = requests.post(self.tts_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            audio_data = base64.b64decode(result.get("audio", ""))
            
            result_dict = {
                "success": True,
                "audio_base64": result.get("audio", ""),
                "file_path": None
            }
            
            # Save audio file if output_path is provided
            if output_path:
                with open(output_path, "wb") as audio_file:
                    audio_file.write(audio_data)
                result_dict["file_path"] = output_path
            
            return result_dict
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": None
            }
    
    def speech_to_text(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Convert speech to text using Sarvam's STT API
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Dictionary with transcription result
        """
        try:
            # Read audio file as binary
            file = {
                "file" : (audio_file_path, open(audio_file_path, "rb"), "audio/wav")
            }
            
            headers = {
                "api-subscription-key" : os.getenv("SARVAM_API_KEY")
            }    
            response = requests.post(self.stt_url, files = file, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return result['transcript']
            
        except (requests.exceptions.RequestException, IOError) as e:
            print(f"Error during speech-to-text: {e}")
            return ""
    
    def translate_text(self, text: str, target_language: str) -> str:
        """
        Translate text to a target language using Sarvam's Translation API
        
        Args:
            text: The text to translate
            target_language: The target language code (e.g., 'es' for Spanish)
            
        Returns:
            Translated text
        """
        translation_url = "https://api.sarvam.ai/translate"
        payload = {
            "text": text,
            "target_language": target_language
        }
        headers = {
            "api-subscription-key": os.getenv("SARVAM_API_KEY")
        }
        
        try:
            response = requests.post(translation_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("translated_text", "")
            
        except requests.exceptions.RequestException as e:
            print(f"Error during translation: {e}")
            return ""

