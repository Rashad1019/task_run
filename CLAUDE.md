# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

**Task/Intel** — an AI task planner that takes a free-form brain dump and returns a prioritized daily schedule. It uses the Google Gemini API (`gemini-3.1-flash-lite-preview`) with structured JSON output.

Two entry points:
- **Terminal app** (`agent.py`): interactive CLI, prompts for API key at startup, uses Pydantic models for response parsing.
- **Web app** (`api/index.py` + `index.html`): Vercel serverless function (`BaseHTTPRequestHandler`) + dark-themed single-page frontend.

## Running locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set the Gemini API key (required)
export GEMINI_API_KEY="your_key_here"   # bash/zsh
# or: setx GEMINI_API_KEY "your_key_here"  (Windows, then restart shell)

# Terminal mode
python agent.py

# Local web server (serves index.html at / and handles POST /api/index)
python local_server.py
```

## Deploying

Deployed on Vercel. `vercel.json` rewrites `/api/*` → `api/index.py` and `/` → `index.html`. Push to main to deploy.

## Architecture

```
agent.py          — CLI entry point; uses Pydantic TaskPlan/ScheduleItem models
api/index.py      — Vercel serverless handler; uses google.genai types.Schema directly
                    (avoids Pydantic SDK bug present in pydantic>=2.11)
index.html        — Self-contained SPA; POSTs to /api/index, renders task cards
requirements.txt  — google-genai==0.6.0, pydantic>=2.0,<2.11
```

**Critical schema note**: `api/index.py` intentionally uses `types.Schema` (not Pydantic models) for `response_schema` because passing a Pydantic model to the `google-genai` SDK causes a validation error (`Extra inputs are not permitted` on `$ref` fields) with `pydantic>=2.11`. `agent.py` uses Pydantic models safely because it calls `response.parsed` / `model_validate_json` directly.

## Response schema

Both entry points produce the same JSON shape:

```json
{
  "schedule": [
    {
      "task": "string",
      "priority": "P0 | P1 | P2 | P3",
      "estimated_minutes": 30,
      "reasoning": "string"
    }
  ]
}
```

Priority rules: P0 = critical/production bugs, P1 = high/blocking work, P2 = medium/routine, P3 = low/nice-to-have.

## Environment variables

| Variable | Required | Notes |
|----------|----------|-------|
| `GEMINI_API_KEY` | Yes (production) | Falls back to ADC if unset locally |
