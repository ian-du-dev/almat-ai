import os
from dotenv import load_dotenv
from pathlib import Path

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

def load_harness():
    script_dir = Path(__file__).parent
    file_path = script_dir / "harness.txt"

    with open(file_path, "r", encoding="utf-8") as f:
        harness = f.read()
        return harness

def load_rounds():
    load_dotenv()

    ROUNDS = os.getenv("ROUNDS")

    return int(ROUNDS)