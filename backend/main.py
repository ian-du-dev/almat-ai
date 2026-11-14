import load

API_KEY = load.load_key()
MODEL_1, MODEL_2, MODEL_3 = load.load_models()
HARNESS = load.load_harness()

transcript = []

client = Groq(api_key=API_KEY)

class AI:
    def __init__(self, client, name, model):
        self.client = client
        self.name = name
        self.model = model

    def generate_response(self, prompt, transcript):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=transcript + [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
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