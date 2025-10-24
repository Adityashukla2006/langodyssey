# EnglishPal: RAG-based Language Learning Application

EnglishPal is an intelligent English language learning application that uses Retrieval-Augmented Generation (RAG) to deliver personalized language instruction. The application leverages LangChain, OpenAI's API, FAISS vector database, and Sarvam's speech APIs to create an interactive and engaging learning experience.

## Features

- **Conversational Interface**: Begins with casual warm-up conversation before transitioning to structured learning
- **Speech Recognition & Synthesis**: Uses Sarvam's APIs for text-to-speech and speech-to-text capabilities
- **Personalized Learning**: Tracks user progress across lessons, stages, and levels
- **Intelligent Feedback**: Evaluates user responses against expected answers and provides helpful feedback
- **Progress Tracking**: Stores user progress in PostgreSQL database for continuous learning

## Technical Architecture

- **LLM**: OpenAI's API for natural language understanding and generation
- **Vector Database**: FAISS for storing and retrieving instructional prompts
- **Speech APIs**: Sarvam AI's text-to-speech and speech-to-text APIs
- **Database**: PostgreSQL for user progress tracking
- **Framework**: Streamlit for the web interface

## Setup Instructions

1. Ensure PostgreSQL is installed and running
2. Create a database named `learning_app_db`
3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables in `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SARVAM_API_KEY=your_sarvam_api_key
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_USER=your_postgres_user
   POSTGRES_PASSWORD=your_postgres_password
   POSTGRES_DB=learning_app_db
   ```
5. Initialize the database and FAISS vector store:
   ```
   python database/database_manager.py
   ```
6. Run the application:
   ```
   streamlit run main.py
   ```

## Database Schema

The application uses three main tables:
- **users**: Stores user information and current learning progress
- **completed_lessons**: Records completed lessons with accuracy scores
- **feedback_history**: Stores user responses and AI feedback for review

## Learning Flow

1. **Warm-up Conversation**: The AI engages in casual conversation to make the user comfortable
2. **Learning Phase Transition**: After a brief exchange, the AI asks if the user is ready to start learning
3. **Structured Learning**: The AI presents lessons from the FAISS database based on the user's level and stage
4. **Response Evaluation**: User responses are evaluated against expected answers
5. **Feedback & Progress**: The AI provides feedback and tracks progress in the database
6. **Continuous Learning**: The application remembers where the user left off for future sessions

## Requirements

See `requirements.txt` for a full list of dependencies.
