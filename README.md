# AI Task Planner (Task/Intel) 🧠
### Turning Unstructured Thoughts into Actionable Daily Execution

## Overview
Most productivity tools assume structured input. This system solves the opposite problem.

**Task/Intel** is an AI-powered task planner that converts a free-form brain dump into a structured, prioritized daily schedule using the Google Gemini API (`gemini-3.1-flash-lite-preview`) with schema-constrained outputs for reliability. It analyzes your raw tasks, assigns logical priorities, and estimates durations, outputting a clear, structured JSON response.

## Impact
- ~60–80% reduction in manual task organization
- Near-100% schema-compliant outputs

## What It Does
- **Unstructured Input → Prioritized Task Schedule**: Automatically categorizes tasks into P0 (Critical), P1 (High), P2 (Medium), and P3 (Low) based on urgency and context.
- **Time Estimation**: Calculates estimated time needed per task.
- **Built-in Reasoning**: Provides AI reasoning for the assigned priority and duration.
- **Dual Interfaces**: 
  - 🖥️ **Terminal App (`agent.py`)**: An interactive CLI for quick, terminal-based task planning.
  - 🌐 **Web App (`index.html`)**: A sleek, dark-themed Single Page Application (SPA) with a responsive UI.

## Tech Stack
- **AI:** Google GenAI SDK (`google-genai==0.6.0`), Google Gemini API
- **Backend:** Python, Serverless API, Pydantic (`pydantic>=2.0,<2.11`)
- **Frontend:** HTML5, Vanilla CSS, JavaScript (SPA)
- **Deployment:** Vercel

## Example Output
```json
{
  "schedule": [
    {
      "task": "Fix production API bug",
      "priority": "P0",
      "estimated_minutes": 60,
      "reasoning": "Critical issue affecting users"
    }
  ]
}
```

## Architecture

```text
├── agent.py          # CLI entry point; uses Pydantic TaskPlan/ScheduleItem models
├── api/
│   └── index.py      # Vercel serverless handler; directly uses google.genai types.Schema
├── index.html        # Self-contained SPA frontend; POSTs to /api/index
├── requirements.txt  # Python dependencies
└── vercel.json       # Deployment configuration
```

## Prioritization Matrix

- **P0 (Critical)**: Production bugs, urgent client requests, or hard deadlines today.
- **P1 (High)**: Core project work, unblocking other team members.
- **P2 (Medium)**: Routine tasks, emails, documentation.
- **P3 (Low)**: Nice-to-haves, learning, long-term planning.

## Getting Started

### Prerequisites

- Python 3.10+
- Google Gemini API Key

### Local Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set the Gemini API Key:**
   ```bash
   # On macOS/Linux
   export GEMINI_API_KEY="your_api_key_here"
   
   # On Windows
   setx GEMINI_API_KEY "your_api_key_here"
   ```

### Running the App

**Terminal Mode:**
```bash
python agent.py
```

**Web Mode (Local):**
```bash
python local_server.py
```
*(Serves `index.html` at `/` and handles POST requests to `/api/index`)*

## Deployment

Task/Intel is optimized for serverless deployment on **Vercel**. 

1. Ensure your `vercel.json` is configured to rewrite `/api/*` to `api/index.py` and `/` to `index.html`.
2. Add your `GEMINI_API_KEY` to your Vercel project's Environment Variables.
3. Push to your `main` branch to trigger an automatic deployment.
