from backend.app.load_key import load_key
API_KEY = load_key()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow your frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your frontend's actual URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the expected structure of the incoming JSON data
class PromptRequest(BaseModel):
    prompt: str

@app.post("/chat")
async def generate_ai_response(request: PromptRequest):
    user_prompt = request.prompt
    
    # --- YOUR AI LOGIC GOES HERE ---
    # e.g., response = openai_client.chat.completions.create(...)
    ai_reply = 
    # --------------------------------
    
    return {"reply": ai_reply}

