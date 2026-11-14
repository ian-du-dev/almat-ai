import load
from groq import Groq

API_KEY = load.load_key()
MODEL_1, MODEL_2, MODEL_3 = load.load_models()
HARNESS = load.load_harness()
ROUNDS = load.load_rounds()

transcript = []

client = Groq(api_key=API_KEY)

class AI:
    def __init__(self, client, name, model):
        self.client = client
        self.name = name
        self.model = model

    def generate_response(self, transcript):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=transcript,
            temperature=1,
            max_completion_tokens=2048,
            top_p=1,
            reasoning_effort="medium",
            stream=True,
            stop=None
        )

        response = ""
        
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""

        return response

prompt = input("prompt: ")

transcript += [
    {
        "role": "user",
        "content": prompt
    }
]

current_round = 1

AI_1 = AI(client, "AI 1", MODEL_1)
AI_2 = AI(client, "AI 2", MODEL_2)
AI_3 = AI(client, "AI 3", MODEL_3)

AIs = [AI_1, AI_2, AI_3]

transcript += [
    {
        "role": "system",
        "content": HARNESS
    }
]

def round(current_round):
    global transcript
    transcript += [{
        "role": "system",
        "content": f"Round {current_round} of {ROUNDS}"
    }]

    if current_round == ROUNDS:
        transcript += [{
            "role": "system",
            "content": "This is the final round. Please provide a summary of the discussion and any conclusions reached."
        }]
    
    for ai in AIs:
        ai_response = ai.generate_response(transcript)
        transcript += [{
            "role": ai.name,
            "content": ai_response
        }]

for current_round in range(1, ROUNDS + 1):
    round(current_round)

print(transcript)