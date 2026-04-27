from http.server import BaseHTTPRequestHandler
import json
import os
from google import genai
from google.genai import types
from google.genai import errors
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else genai.Client()

RESPONSE_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "schedule": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "task":               types.Schema(type=types.Type.STRING),
                    "priority":           types.Schema(type=types.Type.STRING),
                    "estimated_minutes":  types.Schema(type=types.Type.INTEGER),
                    "reasoning":          types.Schema(type=types.Type.STRING),
                },
                required=["task", "priority", "estimated_minutes", "reasoning"],
            )
        )
    },
    required=["schedule"],
)

SYSTEM_PROMPT = """
You are an expert productivity AI agent. Your job is to take an unstructured list of tasks
from a professional and convert them into a structured, prioritized daily schedule.

Rules for prioritization:
1. P0 (Critical): Production bugs, urgent client requests, or hard deadlines today.
2. P1 (High): Core project work, unblocking other team members.
3. P2 (Medium): Routine tasks, emails, documentation.
4. P3 (Low): Nice-to-haves, learning, long-term planning.
"""

@retry(
    retry=retry_if_exception_type(errors.APIError),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True
)
def call_gemini(user_input, model_name):
    return client.models.generate_content(
        model=model_name,
        contents=user_input,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
        ),
    )

def generate_schedule_with_fallback(user_input):
    models_to_try = ["gemini-3.1-flash-lite-preview", "gemini-2.5-pro"]
    last_error = None
    
    for model_name in models_to_try:
        try:
            return call_gemini(user_input, model_name)
        except errors.APIError as e:
            last_error = e
            # Skip to the next model if this one fails
            pass
            
    # If both models fail after all retries, raise the final error
    raise last_error

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            body = json.loads(post_data.decode('utf-8'))
            user_input = body.get("user_input", "")

            if not user_input:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "user_input is required"}).encode('utf-8'))
                return

            response = generate_schedule_with_fallback(user_input)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.text.encode('utf-8'))

        except errors.APIError as e:
            status_code = 503 if ("503" in str(e) or getattr(e, 'code', None) == 503) else 500
            error_msg = "AI model is currently overloaded. Please retry." if status_code == 503 else f"AI Error: {str(e)}"
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": error_msg}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            try:
                with open('index.html', 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content)
                return
            except Exception:
                pass

        self.send_response(405)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Method Not Allowed. This API only accepts POST requests."}).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
