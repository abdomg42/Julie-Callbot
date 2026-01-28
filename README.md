# Callbot Julie — AI Core (Decision Engine)

## What’s included
- **LangGraph** orchestration (structural, testable)
- **Ollama** decision model client (local)
- **SentenceTransformers** embedder (optional; used for local testing only)
- **Strict JSON schema validation** (stdlib only)
- **Mock retrieval node** (RAG retrieval call left as comments — plug FAISS later)

## Requirements
- Python 3.10+
- Ollama installed and running locally
- A small instruct model pulled (example):
  - `ollama pull llama3.2:1b-instruct`

## Install
```bash
pip install -r requirements.txt
```

## Run (CLI)
```bash
python -m app.main
```

## Notes on RAG
Retrieval is mocked .
Replace `core/retrieval.py::retrieve()` with your FAISS function.
The expected retrieval output format is documented in that file.

## Ollama (required for LLM mode)

This project uses Ollama to run a small local model.

## Windows install

- Download and install Ollama for Windows from the official site.
- Open a new terminal and verify:

```bash
ollama -v
```

## Start Ollama

Ollama must be running and listening on localhost:11434.
You can start it by opening the Ollama app, or in PowerShell:

```
ollama serve
```

## Pull a small model 

```
ollama pull llama3.2:1b-instruct
```

## Quick health check

```
curl http://localhost:11434/api/tags
```
## Integration 

Import the fonction **run_ai_core** from core/entrypont.

*Consumes*

```json
{
"text_query": "string" ,
"text_context": "string",
"vector_embedding": "(768-dim vector: list[float] or numpy.ndarray)"
}

```
*Returns*

decision_json:

```json
{
  "intent": "string",
  "urgency": "low|med|high",
  "action": "rag_query|escalate",
  "confidence": [0.0~1.0]
}
```
