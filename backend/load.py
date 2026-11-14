import os
from dotenv import load_dotenv

def load_key():
    load_dotenv()

    API_KEY = os.getenv("GROQ_API_KEY")

    return API_KEY

def load_models():
    load_dotenv()

    MODEL_1 = os.getenv("MODEL_1")
    MODEL_2 = os.getenv("MODEL_2")
    MODEL_3 = os.getenv("MODEL_3")

    return MODEL_1, MODEL_2, MODEL_3