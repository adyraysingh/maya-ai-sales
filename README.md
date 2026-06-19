# Maya AI Sales Engine

Autonomous AI sales consultant for **MakeYourLabel** — Python + FastAPI + GPT-4 + Microsoft Graph + Zoho CRM.

## How It Works

New lead in Zoho → WF01 sends first email → Prospect replies → AI engine detects reply via Graph API → GPT-4 generates Maya's response → Reply sent from maya@makeyourlabel.com → Conversation summary saved to Zoho CRM lead notes → Repeat for every reply.

## Project Structure

```
maya-ai-sales/
├── main.py               # Entry point
├── config.py             # Settings from .env
├── requirements.txt
├── .env.example          # Copy to .env and fill credentials
├── zoho/
│   ├── client.py         # Zoho CRM REST API client
│   ├── leads.py          # Read lead data
│   └── summary.py        # Write conversation notes to CRM
├── email/
│   ├── graph_client.py   # Microsoft Graph API client
│   ├── sender.py         # Send emails as Maya
│   └── monitor.py        # Poll inbox for new replies
├── ai/
│   ├── maya.py           # Maya persona + NICE framework prompt
│   ├── conversation.py   # Conversation history management
│   └── response.py       # GPT-4 response generation
└── webhook/
    ├── server.py         # FastAPI app + APScheduler
    ├── zoho_hook.py      # Zoho new lead webhook handler
    └── email_loop.py     # CORE: AI conversation loop (runs every 60s)
```

## Setup

```bash
git clone https://github.com/adyraysingh/maya-ai-sales.git
cd maya-ai-sales
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill .env with your credentials
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Required Credentials (.env)

| Variable | Where to get it |
|----------|----------------|
| `OPENAI_API_KEY` | platform.openai.com |
| `MICROSOFT_TENANT_ID` | Azure Portal → App Registration |
| `MICROSOFT_CLIENT_ID` | Azure Portal → App Registration |
| `MICROSOFT_CLIENT_SECRET` | Azure Portal → App Registration |
| `ZOHO_CLIENT_ID` | Zoho Developer Console |
| `ZOHO_CLIENT_SECRET` | Zoho Developer Console |
| `ZOHO_REFRESH_TOKEN` | Zoho OAuth flow |
| `WEBHOOK_SECRET` | Any random string |

## Tech Stack

Python 3.11 · FastAPI · OpenAI GPT-4o · Microsoft Graph API · Zoho CRM REST API · APScheduler

## Maya's Identity

Maya is a Brand Launch Consultant at MakeYourLabel. She uses the NICE framework (Needs, Interest, Connection, Expectations) and never reveals she is an AI.
