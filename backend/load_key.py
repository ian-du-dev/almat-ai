import os
from backend.main import API_KEY
from dotenv import load_dotenv

def load_key():
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    return GROQ_API_KEY