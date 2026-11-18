from backend.app.load_key import load_key
API_KEY = load_key()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.ai import prompt

app = FastAPI()

# Allow your frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["ian-du-dev.github.io/almat-ai/frontent"],  # In production, replace "*" with your frontend's actual URL
    allow_methods=["ian-du-dev.github.io/almat-ai/frontent"],
    allow_headers=["ian-du-dev.github.io/almat-ai/frontent"],
)

# Define the expected structure of the incoming JSON data
class PromptRequest(BaseModel):
    prompt: str

@app.post("/chat")
async def generate_ai_response(request: PromptRequest):
    user_prompt = request.prompt
    
    ai_reply = prompt(user_prompt)
    
    return {"reply": ai_reply}

