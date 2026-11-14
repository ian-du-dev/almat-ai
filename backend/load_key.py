import os
from backend.main import API_KEY
from dotenv import load_dotenv

def load_key():
    load_dotenv()
    API_KEY_GROQ = os.getenv("API_KEY_GROQ")
    return API_KEY_GROQ