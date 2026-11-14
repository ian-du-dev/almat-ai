import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import load
from groq import APIError, Groq

API_KEY = load.load_key()
MODEL_1, MODEL_2, MODEL_3 = load.load_models()
HARNESS = load.load_harness()
ROUNDS = load.load_rounds()

client = Groq(api_key=API_KEY)


class AI:
    def __init__(self, name, model):
        self.name = name
        self.model = model

    def generate_response(self, transcript):
        completion = client.chat.completions.create(
            model=self.model,
            messages=transcript,
            temperature=1,
            top_p=1,
            stream=True,
            stop=None,
        )

        response = ""
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
        return response


AIs = [
    AI("AI 1", MODEL_1),
    AI("AI 2", MODEL_2),
    AI("AI 3", MODEL_3),
]


def run_discussion(prompt):
    transcript = []
    results = []
    total_msg = "USER: " + prompt + "\nSYSTEM: " + HARNESS + "\n"

    for current_round in range(1, ROUNDS + 1):
        total_msg += "SYSTEM: Round " + str(current_round) + " of " + str(ROUNDS) + "\n"
        if current_round == ROUNDS:
            total_msg += (
                "SYSTEM: This is the final round. Please provide a summary "
                "of the discussion and any conclusions reached.\n"
            )

        transcript.append({"role": "user", "content": total_msg})
        total_ai_msg = ""

        for ai in AIs:
            response = ai.generate_response(transcript)
            results.append({
                "round": current_round,
                "name": ai.name,
                "text": response,
            })
            total_ai_msg += ai.name + ": " + response + "\n"

        transcript.append({"role": "assistant", "content": total_ai_msg})
        total_msg = ""

    return results


class APIHandler(BaseHTTPRequestHandler):
    allowed_origins = {
        "https://ian-du-dev.github.io",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    }

    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        origin = self.headers.get("Origin")
        if origin in self.allowed_origins:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        origin = self.headers.get("Origin")
        if origin in self.allowed_origins:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/ask":
            self.send_json(404, {"error": "Not found."})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 20000:
                self.send_json(400, {"error": "Enter a prompt and try again."})
                return
            data = json.loads(self.rfile.read(content_length))
        except (ValueError, json.JSONDecodeError):
            self.send_json(400, {"error": "The request was not valid JSON."})
            return

        prompt = data.get("prompt") if isinstance(data, dict) else None
        if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 4000:
            self.send_json(400, {"error": "Enter a prompt of up to 4,000 characters."})
            return

        try:
            transcript = run_discussion(prompt.strip())
        except APIError as error:
            print("AI service request failed:", error)
            self.send_json(502, {"error": "The AI service could not complete the request."})
            return

        self.send_json(200, {"transcript": transcript})


if __name__ == "__main__":
    print("Almat AI API listening on http://localhost:8000")
    ThreadingHTTPServer(("0.0.0.0", 8000), APIHandler).serve_forever()
