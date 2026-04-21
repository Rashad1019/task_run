import json
from typing import Literal
from pydantic import BaseModel
from google import genai
from google.genai import types


class ScheduleItem(BaseModel):
    task: str
    priority: Literal["P0", "P1", "P2", "P3"]
    estimated_minutes: int
    reasoning: str


class TaskPlan(BaseModel):
    schedule: list[ScheduleItem]


SYSTEM_PROMPT = """
You are an expert productivity AI agent. Your job is to take an unstructured list of tasks
from a professional and convert them into a structured, prioritized daily schedule.

Rules for prioritization:
1. P0 (Critical): Production bugs, urgent client requests, or hard deadlines today.
2. P1 (High): Core project work, unblocking other team members.
3. P2 (Medium): Routine tasks, emails, documentation.
4. P3 (Low): Nice-to-haves, learning, long-term planning.
"""


def generate_schedule(client: genai.Client, user_input: str) -> TaskPlan:
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=user_input,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=TaskPlan,
        ),
    )

    return response.parsed


if __name__ == "__main__":
    import getpass
    
    print("\n\033[96m==========================================\033[0m")
    print("\033[96m  🤖 AI TASK PLANNER TERMINAL ACTIVATED  \033[0m")
    print("\033[96m==========================================\033[0m")
    
    print("\n--- API Key Setup ---")
    api_key = getpass.getpass("Please paste your fresh Gemini API key (hidden as you type): ")
    client = genai.Client(api_key=api_key)
    
    print("\nType 'quit' or 'exit' at any time to stop.\n")
    
    while True:
        print("\033[93m\n> Drop your messy brain dump here (or type 'quit'):\033[0m")
        user_input = input()
        
        if user_input.strip().lower() in ['quit', 'exit']:
            print("\033[95mShutting down... Goodbye!\033[0m")
            break
            
        if not user_input.strip():
            continue
            
        print("\033[90m\nThinking...\033[0m")
        try:
            plan = generate_schedule(client, user_input)
            
            print("\n\033[92mYOUR OPTIMIZED SCHEDULE\033[0m")
            print("\033[92m" + "-" * 30 + "\033[0m")

            for item in plan.schedule:
                # Color code priorities
                color = "\033[91m" if item.priority == "P0" else "\033[93m" if item.priority == "P1" else "\033[96m" if item.priority == "P2" else "\033[94m"
                print(f"{color}[{item.priority}] {item.task} ({item.estimated_minutes} min)\033[0m")
                print(f"    \033[3m{item.reasoning}\033[0m\n")
                
        except Exception as e:
            print(f"\n\033[91mError generating schedule: {e}\033[0m")
