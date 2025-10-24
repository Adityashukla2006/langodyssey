from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.vectorstore = None
        self.conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT")
        )
        self.cursor = self.conn.cursor()
        
    def get_data(self):
        self.cursor.execute("SELECT prompt,expected_user_response,notes_for_ai,stage,level,lesson_level FROM prompts")
        rows = self.cursor.fetchall()
        data = [{"prompt": row[0],
                 "expected_user_response": row[1],
                 "notes_for_ai": row[2],
                 "stage": row[3],
                 "level": row[4],
                 "lesson_level": row[5]} for row in rows]
        self.cursor.close()
        self.conn.close()
        return data
    
    def create_vectorstore(self, data):
        docs = [Document(page_content=item["prompt"], metadata={
            "expected_user_response": item["expected_user_response"],
            "notes_for_ai": item["notes_for_ai"],
            "stage": item["stage"],
            "level": item["level"],
            "lesson_level": item["lesson_level"]
        }) for item in data]

        self.vectorstore = FAISS.from_documents(docs, self.embeddings)

        self.vectorstore.save_local("faiss_index")

def main():
    db_manager = DatabaseManager()
    data = db_manager.get_data()
    db_manager.create_vectorstore(data)
    print("Vectorstore created and saved successfully.")
    
    

if __name__ == "__main__":
    main()