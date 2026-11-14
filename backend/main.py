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
            top_p=1,
            stream=True,
            stop=None
        )

        response = ""
        
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""

        return response

prompt = input("prompt: ")

total_msg = ""

total_msg += "USER: " + prompt + "\n"

current_round = 1

AI_1 = AI(client, "AI 1", MODEL_1)
AI_2 = AI(client, "AI 2", MODEL_2)
AI_3 = AI(client, "AI 3", MODEL_3)

AIs = [AI_1, AI_2, AI_3]

total_msg += "SYSTEM: " + HARNESS + "\n"

def round(current_round):
    global transcript, total_msg

    print()
    print("Round " + str(current_round) + " of " + str(ROUNDS))
    print("--------------------------------------------------")

    total_msg += "SYSTEM: Round " + str(current_round) + " of " + str(ROUNDS) + "\n"

    if current_round == ROUNDS:
        total_msg += "SYSTEM: This is the final round. Please provide a summary of the discussion and any conclusions reached.\n"
    
    transcript += [{
        "role": "user",
        "content": total_msg
    }]
    
    total_ai_msg = ""

    for ai in AIs:
        ai_response = ai.generate_response(transcript)

        total_ai_msg += ai.name + ": " + ai_response + "\n"

        print(ai.name + ": " + ai_response)
        print("--------------------------------------------------")
        print()
    
    transcript += [{
        "role": "assistant",
        "content": total_ai_msg
    }]
    
    total_msg = ""

for current_round in range(1, ROUNDS + 1):
    round(current_round)