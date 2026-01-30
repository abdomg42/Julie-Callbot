# vapi_webhook.py
import sys
import time
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Add parent directory to path
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from core.entrypoint import run_ai_core
from tool_router.entrypoint.entrypoint import callbot_global_response, get_orchestrator
from tool_router.src.database.db_service import db_service

# Import CONFIG from main.py
from main import CONFIG

app = FastAPI()
SESSIONS: Dict[str, Dict[str, Any]] = {}

@app.get("/")
def health():
    return {"ok": True}

@app.post("/vapi-webhook")
async def vapi_webhook(req: Request):
    payload = await req.json()

    msg = payload.get("message", {}) or {}
    msg_type = msg.get("type", "")

    # call id (selon l'event, ça peut être dans payload.call ou msg.call)
    call = (payload.get("call") or msg.get("call") or {})
    call_id = (call.get("id") if isinstance(call, dict) else None) or "unknown"

    # La plupart des events = info => on répond juste 200 OK. [page:2]
    if msg_type != "tool-calls":
        return JSONResponse({"ok": True})

    tool_calls = msg.get("toolCallList", [])
    if call_id not in SESSIONS:
        SESSIONS[call_id] = {
            "orchestrator": get_orchestrator(enable_tts=False, enable_llm=False),
            "conversation_history": [],
            "session_id": f"vapi_{call_id}_{int(time.time())}",
        }
    sess = SESSIONS[call_id]

    results = []
    for tc in tool_calls:
        tool_call_id = tc["id"]
        params = tc.get("parameters", {}) or {}
        user_text = params.get("text", "")

        emotion_bert = {"sentiment": "NEUTRAL", "score": 0.5}
        audio_summary = {"duration_ms": 0}
        decision = run_ai_core(user_text, emotion_bert, audio_summary)

        response = callbot_global_response(
            text=user_text,
            emotion_bert=emotion_bert,
            intent=decision.get("intent", "general_inquiry"),
            urgency=decision.get("urgency", "low"),
            action=decision.get("action", "rag_query"),
            confidence=decision.get("confidence", 0.5),
            session_id=sess["session_id"],
            conversation_history=sess["conversation_history"],
            orchestrator=sess["orchestrator"],
            enable_tts=False,   # Vapi fera le TTS
            enable_llm=False
        )

        bot_text = response.response_text
        sess["conversation_history"].extend([
            {"role": "user", "text": user_text},
            {"role": "assistant", "text": bot_text},
        ])

        # Vapi attend: {"results":[{"toolCallId": "...", "result": "..."}]} [page:2]
        results.append({
            "toolCallId": tool_call_id,
            "result": bot_text
        })

    return JSONResponse({"results": results})