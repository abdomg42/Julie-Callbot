# main_webhook.py - FastAPI webhook using main.py logic
import sys
import time
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Add parent directory to path
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

# Import everything from main.py
from main import (
    CONFIG, conversation_state, run_ai_core, 
    callbot_global_response, get_orchestrator, db_service
)

app = FastAPI()
SESSIONS: Dict[str, Dict[str, Any]] = {}

@app.get("/")
def health():
    return {"ok": True, "config": CONFIG}

@app.post("/vapi-webhook")
async def vapi_webhook(req: Request):
    payload = await req.json()
    
    print(f"🔍 DEBUG - Received payload: {payload}")  # Debug line
    
    msg = payload.get("message", {}) or {}
    msg_type = msg.get("type", "")
    
    # Get call ID
    call = (payload.get("call") or msg.get("call") or {})
    call_id = (call.get("id") if isinstance(call, dict) else None) or "unknown"
    
    # Most events are just info, respond with 200 OK
    if msg_type != "tool-calls":
        print(f"🔍 DEBUG - Non-tool-call event: {msg_type}")  # Debug line
        return JSONResponse({"ok": True})
    
    tool_calls = msg.get("toolCallList", [])
    print(f"🔍 DEBUG - Tool calls count: {len(tool_calls)}")  # Debug line
    
    # Initialize session if needed
    if call_id not in SESSIONS:
        SESSIONS[call_id] = {
            "orchestrator": get_orchestrator(
                enable_tts=CONFIG["enable_tts"], 
                enable_llm=CONFIG["enable_llm"]
            ),
            "conversation_history": [],
            "session_id": f"vapi_{call_id}_{int(time.time())}",
            "turn_count": 0,
        }
    
    sess = SESSIONS[call_id]
    results = []
    
    for tc in tool_calls:
        tool_call_id = tc["id"]
        params = tc.get("parameters", {}) or {}
        user_text = params.get("text", "")
        
        # Check for end keywords
        if any(keyword in user_text.lower() for keyword in CONFIG["end_keywords"]):
            conversation_state["has_said_goodbye"] = True
            conversation_state["goodbye_count"] += 1
        
        # Check max turns
        if sess["turn_count"] >= CONFIG["max_conversation_turns"]:
            bot_text = "Merci pour votre appel. Notre conversation se termine ici. Au revoir!"
        else:
            # Run AI core logic
            emotion_bert = {"sentiment": "NEUTRAL", "score": 0.5}
            audio_summary = {"duration_ms": 0}
            decision = run_ai_core(user_text, emotion_bert, audio_summary)
            
            # Get bot response
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
                enable_tts=CONFIG["enable_tts"],
                enable_llm=CONFIG["enable_llm"]
            )
            
            bot_text = response.response_text
            
            # Make text TTS-friendly for English voice
            bot_text = bot_text.replace("En ligne:", "Online:")
            bot_text = bot_text.replace("monespaceclient.cnp.fr", "mon espace client dot C N P dot F R")
            bot_text = bot_text.replace("Conseiller:", "Advisor:")
            bot_text = bot_text.replace("Prendre rendez-vous", "Book an appointment")
            bot_text = bot_text.replace("Téléphone:", "Phone:")
            bot_text = bot_text.replace("lun-ven", "Monday to Friday")
            bot_text = bot_text.replace("sam", "Saturday")
        
        # Update conversation history
        sess["conversation_history"].extend([
            {"role": "user", "text": user_text},
            {"role": "assistant", "text": bot_text},
        ])
        sess["turn_count"] += 1
        
        # Store in database if enabled
        if CONFIG["collect_feedback"]:
            try:
                db_service.create_interaction(
                    customer_id=call_id,
                    session_id=sess["session_id"],
                    intent=decision.get("intent", "general_inquiry"),
                    urgency=decision.get("urgency", "low"),
                    emotion="NEUTRAL",
                    confidence=decision.get("confidence", 0.5),
                    action_taken=decision.get("action", "rag_query"),
                    priority="normal",
                    reason=user_text,
                    metadata={
                        "user_input": user_text,
                        "bot_response": bot_text,
                        "timestamp": time.time(),
                        "call_id": call_id
                    }
                )
            except Exception as e:
                print(f"Database error: {e}")
        
        results.append({
            "toolCallId": tool_call_id,
            "result": bot_text
        })
    
    return JSONResponse({"results": results})