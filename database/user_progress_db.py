import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()


class UserProgressDB:
    """Database manager for user progress and learning data."""
    
    def __init__(self):
        """Initialize the user progress database."""
        self.conn_params = {
            "dbname": os.getenv("POSTGRES_DB"),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "host": os.getenv("POSTGRES_HOST"),
            "port": os.getenv("POSTGRES_PORT")
        }
        self._create_tables_if_not_exist()

    # Context Manager for Database Connections
    @contextmanager
    def _get_connection(self, dict_cursor: bool = False):
        """
        Context manager for database connections.
        
        Args:
            dict_cursor: If True, returns results as dictionaries.
            
        Yields:
            tuple: (connection, cursor) objects
        """
        conn = None
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor(cursor_factory=RealDictCursor) if dict_cursor else conn.cursor()
            yield conn, cursor
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    # Table Setup
    def _create_tables_if_not_exist(self):
        """Create necessary tables if they don't exist."""
        with self._get_connection() as (conn, cursor):
            self._create_users_table(cursor)
            self._create_lessons_table(cursor)
            self._create_user_feedback_table(cursor)
            conn.commit()
    
    def _create_users_table(self, cursor):
        """Create the users table."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255),
                password VARCHAR(255),
                language VARCHAR(255),
                current_level VARCHAR(50),
                current_stage VARCHAR(50),
                progress_id INTEGER REFERENCES prompts(prompt_id)
            )
        """)
    
    def _create_lessons_table(self, cursor):
        """Create the lessons table."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) REFERENCES users(user_id),
                prompt_id VARCHAR(255),
                ai_feedback TEXT,
                completed_at TIMESTAMP
            )
        """)
    
    def _create_user_feedback_table(self, cursor):
        """Create the user_feedback table."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) REFERENCES users(user_id),
                prompt_id VARCHAR(255),
                feedback TEXT
            )
        """)

    # User Management Methods
    def create_user(self, user_id: str, name: Optional[str] = None) -> bool:
        """
        Create a new user in the database.
        
        Args:
            user_id: Unique identifier for the user
            name: Optional name for the user
            
        Returns:
            bool: True if user created successfully, False if user already exists
        """
        try:
            with self._get_connection() as (conn, cursor):
                # Check if user already exists
                cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
                if cursor.fetchone():
                    return False  # User already exists
                
                cursor.execute(
                    "INSERT INTO users (user_id, name, current_level, current_stage, lesson_level) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, name, "Beginner", "L1", 1)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def check_user(self, name: str, password: str) -> bool:
        """
        Check if user exists in the database with given credentials.
        
        Args:
            name: User's name
            password: User's password
            
        Returns:
            bool: True if user exists with matching credentials, False otherwise
        """
        try:
            with self._get_connection() as (conn, cursor):
                cursor.execute(
                    "SELECT user_id FROM users WHERE name = %s AND password = %s",
                    (name, password)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error checking user: {e}")
            return False

    def get_user_id(self, name: str) -> Optional[str]:
        """
        Retrieve the user ID for a given user name.
        
        Args:
            name: User's name
        Returns:
            Optional[str]: User ID if found, None otherwise
        """
        try:
            with self._get_connection() as (conn, cursor):
                cursor.execute("SELECT user_id FROM users WHERE name = %s", (name,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error retrieving user ID: {e}")
            return None
    # User Data Retrieval Methods
    def get_user_level(self, user_id: str) -> Optional[str]:
        """
        Retrieve the current lesson level of a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Optional[str]: Current level of the user, or None if not found
        """
        try:
            with self._get_connection(dict_cursor=True) as (conn, cursor):
                cursor.execute("SELECT current_level FROM users WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                return result["current_level"] if result else None
        except Exception as e:
            print(f"Error retrieving user level: {e}")
            return None
    
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve the progress ID of a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dict[str, Any]: Progress ID or empty dict if not found
        """
        try:
            with self._get_connection(dict_cursor=True) as (conn, cursor):
                cursor.execute("SELECT progress_id FROM users WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                return result["progress_id"] if result else {}
        except Exception as e:
            print(f"Error retrieving user progress: {e}")
            return {}
    
    def get_user_language(self, user_id: str) -> Optional[str]:
        """
        Retrieve the preferred language of a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Optional[str]: User's preferred language, or None if not found
        """
        try:
            with self._get_connection(dict_cursor=True) as (conn, cursor):
                cursor.execute("SELECT language FROM users WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                return result["language"] if result else None
        except Exception as e:
            print(f"Error retrieving user language: {e}")
            return None
    
    def get_user_level_and_stage(self, user_id: str) -> Optional[tuple]:
        """
        Retrieve the current level and stage of a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Optional[tuple]: (current_level, current_stage) or None if not found
        """
        try:
            with self._get_connection(dict_cursor=True) as (conn, cursor):
                cursor.execute(
                    "SELECT current_level, current_stage FROM users WHERE user_id = %s",
                    (user_id,)
                )
                result = cursor.fetchone()
                return (result["current_level"], result["current_stage"]) if result else None
        except Exception as e:
            print(f"Error retrieving user level and stage: {e}")
            return None

    # User Update Methods
    def update_user_progress(self, user_id: str, new_progress: int) -> bool:
        """
        Update the progress ID for a user.
        
        Args:
            user_id: Unique identifier for the user
            new_progress: New progress ID value
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            with self._get_connection() as (conn, cursor):
                cursor.execute(
                    "UPDATE users SET progress_id = %s WHERE user_id = %s",
                    (new_progress, user_id)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating user progress: {e}")
            return False

    # Prompt Data Retrieval Methods
    def get_prompt(self, prompt_id: int) -> str:
        """
        Retrieve a prompt by its ID.
        
        Args:
            prompt_id: Unique identifier for the prompt
            
        Returns:
            str: Prompt text, or None if not found
        """
        try:
            with self._get_connection(dict_cursor=True) as (conn, cursor):
                cursor.execute("SELECT prompt FROM prompts WHERE prompt_id = %s", (prompt_id,))
                result = cursor.fetchone()
                return result["prompt"] if result else None
        except Exception as e:
            print(f"Error retrieving lesson number: {e}")
            return None
    
    def get_notes(self, prompt_id: int) -> str:
        """
        Retrieve AI notes for a prompt.
        
        Args:
            prompt_id: Unique identifier for the prompt
            
        Returns:
            str: Notes for AI, or None if not found
        """
        try:
            with self._get_connection(dict_cursor=True) as (conn, cursor):
                cursor.execute(
                    "SELECT notes_for_ai FROM prompts WHERE prompt_id = %s",
                    (prompt_id,)
                )
                result = cursor.fetchone()
                return result["notes_for_ai"] if result else None
        except Exception as e:
            print(f"Error retrieving notes for AI: {e}")
            return None
    
    def get_expected_response(self, prompt_id: int) -> str:
        """
        Retrieve the expected user response for a prompt.
        
        Args:
            prompt_id: Unique identifier for the prompt
            
        Returns:
            str: Expected user response, or None if not found
        """
        try:
            with self._get_connection(dict_cursor=True) as (conn, cursor):
                cursor.execute(
                    "SELECT expected_user_response FROM prompts WHERE prompt_id = %s",
                    (prompt_id,)
                )
                result = cursor.fetchone()
                return result["expected_user_response"] if result else None
        except Exception as e:
            print(f"Error retrieving expected response: {e}")
            return None