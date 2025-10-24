import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class UserProgressDB:
    def __init__(self):
        """Initialize the user progress database"""
        self.conn_params = {
            "dbname": os.getenv("POSTGRES_DB"),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "host": os.getenv("POSTGRES_HOST"),
            "port": os.getenv("POSTGRES_PORT")
        }
        self._create_tables_if_not_exist()

    
    def _create_tables_if_not_exist(self):
        """Create necessary tables if they don't exist"""
        conn = psycopg2.connect(**self.conn_params)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            language VARCHAR(255),
            current_level VARCHAR(50),
            current_stage VARCHAR(50),
            progress_id INTEGER REFERENCES prompts(prompt_id)
        )
        """)
        
        # Create lessons table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) REFERENCES users(user_id),
            prompt_id VARCHAR(255),
            ai_feedback TEXT,
            completed_at TIMESTAMP
        )
        """)
        
        # Create user_feedback table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_feedback (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) REFERENCES users(user_id),
            prompt_id VARCHAR(255),
            feedback TEXT
        )
        """)
        
        conn.commit()
        conn.close()
    
    def create_user(self, user_id: str, name: Optional[str] = None) -> bool:
        """Create a new user in the database"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            if cursor.fetchone():
                conn.close()
                return False  # User already exists
            
            cursor.execute(
                "INSERT INTO users (user_id, name, current_level, current_stage, lesson_level) VALUES (%s, %s, %s, %s, %s)",
                (user_id, name, "Beginner", "L1", 1)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def get_user_level(self, user_id: str) -> Optional[str]:
        """Retrieve the current lesson level of a user"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT current_level FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result["current_level"]
            return None
        except Exception as e:
            print(f"Error retrieving user level: {e}")
            return None
    
    def get_user_progress(self,user_id : str) -> Dict[str, Any]:
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("SELECT progress_id FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result["progress_id"]
        except Exception as e:
            print(f"Error retrieving user progress: {e}")
            return {}
    def get_prompt(self, prompt_id : int) -> str:
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("SELECT prompt FROM prompts WHERE prompt_id = %s", (prompt_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result["prompt"]
        except Exception as e:
            print(f"Error retrieving lesson number: {e}")
            return None
        
    def update_user_progress(self,user_id : str, new_progress : int) -> bool:
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE users SET progress_id = %s WHERE user_id = %s",
                (new_progress, user_id)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating user progress: {e}")
            return False
    def get_notes(self, prompt_id : int) -> str:
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("SELECT notes_for_ai FROM prompts WHERE prompt_id = %s", (prompt_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result["notes_for_ai"]
        except Exception as e:
            print(f"Error retrieving notes for AI: {e}")
            return None
    def get_user_language(self, user_id: str) -> Optional[str]:
        """Retrieve the preferred language of a user"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT language FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result["language"]
            return None
        except Exception as e:
            print(f"Error retrieving user language: {e}")
            return None 
    def get_user_level_and_stage(self, user_id: str) -> Optional[tuple]:
        """Retrieve the current level and stage of a user"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT current_level, current_stage FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result["current_level"], result["current_stage"]
            return None
        except Exception as e:
            print(f"Error retrieving user level and stage: {e}")
            return None
    
    def get_expected_response(self, prompt_id : int) -> str:
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("SELECT expected_user_response FROM prompts WHERE prompt_id = %s", (prompt_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result["expected_user_response"]
        except Exception as e:
            print(f"Error retrieving expected response: {e}")
            return None
