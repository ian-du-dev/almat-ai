import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from groq import APIError, Groq
from pydantic import BaseModel, Field

from backend import load

DEFAULT_MODEL = "openai/gpt-oss-120b"
ROLES = ["General reasoner", "Skeptical reviewer", "Practical adviser"]
API_KEY = load.load_key()
HARNESS = load.load_harness()
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="Almat AI")


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)


def build_harness(name, other_names, role, round_number, max_rounds):
    text = HARNESS
    values = {
        "AI_NAME": name,
        "NUM_AIS": "3",
        "OTHER_AI_NAMES": other_names,
        "ROLE": role,
        "ROUND": str(round_number),
        "MAX_ROUNDS": str(max_rounds),
        "MAX_WORDS_PER_TURN": "200",
    }
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def get_round_count():
    try:
        rounds = int(os.getenv("ROUNDS", "2"))
    except ValueError as error:
        raise HTTPException(status_code=500, detail="ROUNDS must be a number from 1 to 4.") from error
    if not 1 <= rounds <= 4:
        raise HTTPException(status_code=500, detail="ROUNDS must be a number from 1 to 4.")
    return rounds


@app.post("/api/chat")
def chat(request: PromptRequest):
    if not API_KEY:
        raise HTTPException(status_code=503, detail="Add GROQ_API_KEY to the Vercel environment variables.")

    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="Enter a prompt.")

    rounds = get_round_count()
    configured_models = load.load_models()
    models = [model or DEFAULT_MODEL for model in configured_models]
    participants = [
        {"name": f"AI {index + 1}", "model": model, "role": ROLES[index]}
        for index, model in enumerate(models)
    ]
    client = Groq(api_key=API_KEY)
    history = [{"role": "user", "content": prompt}]
    transcript = [{"round": 0, "name": "You", "text": prompt}]

    try:
        for round_number in range(1, rounds + 1):
            if round_number > 1:
                history.append({
                    "role": "user",
                    "content": f"Continue the discussion. This is round {round_number} of {rounds}.",
                })

            for participant in participants:
                other_names = ", ".join(
                    item["name"] for item in participants if item["name"] != participant["name"]
                )
                system_prompt = build_harness(
                    participant["name"],
                    other_names,
                    participant["role"],
                    round_number,
                    rounds,
                )
                completion = client.chat.completions.create(
                    model=participant["model"],
                    messages=[{"role": "system", "content": system_prompt}, *history],
                    max_completion_tokens=2048,
                )
                text = completion.choices[0].message.content
                if not text or not text.strip():
                    raise HTTPException(status_code=502, detail="The AI service returned an empty answer.")

                text = text.strip()
                transcript.append({
                    "round": round_number,
                    "name": participant["name"],
                    "text": text,
                })
                history.append({"role": "assistant", "content": f"{participant['name']}: {text}"})
    except APIError as error:
        raise HTTPException(status_code=502, detail="The AI service could not complete the request.") from error

    return {"transcript": transcript}


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
