# Callbot Julie V2 — AI-Powered Call Center Assistant

An intelligent voice assistant for CNP Assurances that handles customer inquiries via phone using Twilio, RAG-based knowledge retrieval, and AI decision making.

## Features

- **Voice Integration** — Twilio-powered phone calls with speech recognition
- **AI Decision Engine** — LangGraph orchestration with rules-based or LLM mode
- **RAG Knowledge Base** — FAISS vector search for insurance documentation
- **Smart Routing** — Automatic escalation to human agents when needed
- **Customer Feedback** — Post-call satisfaction collection
- **Dashboard** — React-based analytics dashboard

## Project Structure

```
final/
├── app/                      # Main application
│   ├── twilio_server.py      # Twilio webhook server (main entry)
│   ├── main.py               # CLI interface
│   └── twilio_client.py      # Twilio API client
├── core/                     # AI Decision Engine
│   ├── entrypoint.py         # Main entry point
│   ├── graph.py              # LangGraph orchestration
│   ├── rules.py              # Rule-based decisions
│   └── llm_ollama.py         # Ollama LLM client
├── tool_router/              # Response Generation
│   ├── src/services/         # Orchestrator, TTS, Response Builder
│   ├── src/agents/           # CRM & Human Handoff agents
│   └── src/database/         # Database service
├── RAG/                      # Knowledge Base
│   ├── rag_api.py            # RAG API
│   ├── smart_router.py       # Query routing
│   └── faiss_index/          # Vector index
├── inputs/                   # Audio input processing
│   ├── audio/                # Audio recording & barge-in
│   ├── models/               # Whisper, BERT sentiment
│   └── pipeline/             # Parallel processing pipeline
└── Dashboard/                # React analytics dashboard
```

## Quick Start

### 1. Setup Environment

```bash
cd final

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
# source venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example and edit with your values
copy .env.example .env
```

### 3. Start Server

```bash
# Development
python app/twilio_server.py

# Expose via ngrok (for Twilio webhooks)
ngrok http 8000
```

### 4. Configure Twilio

Set your ngrok URL as the webhook in Twilio console:
- Voice webhook: `https://your-ngrok-url.ngrok.io/voice`

## Ollama Setup (Optional - for LLM mode)

```bash
# Install Ollama from https://ollama.ai
ollama serve
ollama pull llama3.2:1b-instruct

# Verify
curl http://localhost:11434/api/tags
```

Enable LLM mode in `.env`:
```
CALLBOT_USE_LLM=true
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/voice` | POST | Twilio voice webhook |
| `/feedback` | POST | Customer feedback |

## Architecture

```
Phone Call → Twilio → /voice webhook
                         ↓
              Speech Recognition (Twilio)
                         ↓
              AI Core (intent + urgency)
                         ↓
              Tool Router (RAG or Escalate)
                         ↓
              Response Builder (template/LLM)
                         ↓
              TwiML Response → Twilio → Phone
```

## Configuration

See `.env.example` for all configuration options:
- `TWILIO_*` — Twilio credentials
- `DATABASE_URL` — PostgreSQL connection
- `CALLBOT_USE_LLM` — Enable/disable LLM mode
- `ENABLE_TTS` — Enable text-to-speech

## License

Proprietary — CNP Assurances
