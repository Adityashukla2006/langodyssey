# LangOdyssey 🌍

An AI-powered English learning application designed specifically for Indian learners. LangOdyssey combines the power of LangChain and OpenAI GPT-4 to deliver personalized, interactive English lessons with explanations in native Indian languages.

## Features

- **Multilingual Support**: Explanations and guidance in native Indian languages while teaching English
- **Real-time Conversational Practice**: Interactive chat interface for practicing English
- **Intelligent Evaluation**: AI-driven feedback on user responses
- **Progress Tracking**: Monitor learning improvements across vocabulary, grammar, and fluency
- **Adaptive Learning**: Personalized lessons based on user level and progress
- **Voice Integration**: Text-to-speech (TTS) and speech-to-text (STT) capabilities via SarvamAI

## Technology Stack

- **Frontend**: Streamlit (Interactive chat interface)
- **LLM Framework**: LangChain with OpenAI GPT-4
- **Session Management**: LangChain ConversationBufferMemory
- **Database**: PostgreSQL (User progress tracking)
- **Translation & Voice**: SarvamAI API (Translation, TTS, STT)
- **Semantic Search**: LangChain vector stores for content retrieval

## Prerequisites

- Python 3.8+
- PostgreSQL database
- OpenAI API key
- SarvamAI API key

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=langodyssey
```

4. **Set up the database**

First, create your PostgreSQL database, then load the initial data:

```bash
# Connect to your PostgreSQL database
psql -h localhost -U your_postgres_user -d langodyssey

# Load prompts data
\copy prompts FROM 'database/prompts.csv' WITH (FORMAT csv, HEADER true);

# Load prompt IDs
\copy promptid FROM 'database/promptid.csv' WITH (FORMAT csv, HEADER true);
```

Alternatively, you can use the command line:

```bash
psql -h localhost -U your_postgres_user -d langodyssey -c "\copy prompts FROM 'database/prompts.csv' WITH (FORMAT csv, HEADER true);"
psql -h localhost -U your_postgres_user -d langodyssey -c "\copy promptid FROM 'database/promptid.csv' WITH (FORMAT csv, HEADER true);"
```

**Note**: Ensure the `prompts` and `promptid` tables exist in your database before running these commands. Adjust the file paths if your CSV files are in a different location.

## Usage

1. **Start the application**
```bash
streamlit run main.py
```

2. **Access the interface**

Open your browser and navigate to `http://localhost:8501`

3. **Begin learning**
- Select your native language
- Choose your current English proficiency level
- Start conversing with the AI tutor
- Receive personalized feedback and track your progress

## Features in Detail

### Personalized Learning
- Adaptive difficulty based on user performance
- Custom lesson paths for different proficiency levels
- Real-time adjustment to learner needs

### Interactive Conversations
- Natural language processing for understanding context
- Conversational memory for coherent dialogue
- Immediate feedback on grammar, vocabulary, and pronunciation

### Progress Tracking
- UserProgressDB stores learning milestones
- Visual dashboards for tracking improvement
- Detailed analytics on strengths and areas for improvement

### Multilingual Support
- Native language explanations via SarvamAI translation
- Support for major Indian languages
- Code-switching capabilities for gradual English immersion

## API Services

### OpenAI GPT-4
Used for generating intelligent responses, evaluating user input, and providing contextual English lessons.

### SarvamAI
- **Translation**: Converts explanations to user's native language
- **TTS**: Converts text to speech for pronunciation practice
- **STT**: Converts spoken input to text for conversation practice

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


---

**Happy Learning! 🚀**

