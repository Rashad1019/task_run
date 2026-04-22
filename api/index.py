from http.server import BaseHTTPRequestHandler
import json
import os
from google import genai
from google.genai import types

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

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview",
                contents=user_input,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.1,
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                ),
            )

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.text.encode('utf-8'))

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
