import sys
import time
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
import uvicorn

BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from core.entrypoint import run_ai_core
from tool_router.entrypoint.entrypoint import callbot_global_response, get_orchestrator
from tool_router.src.database.db_service import db_service

app = FastAPI(title="CNP Callbot API")

SESSIONS: Dict[str, Dict[str, Any]] = {}
QUEUE_NAME = "support"
HOLD_MUSIC_URL = "http://com.twilio.sounds.music.s3.amazonaws.com/sonatina.mp3"
HUMAN_AGENT_NUMBER = "+212628091058"

try:
    GLOBAL_ORCHESTRATOR = get_orchestrator(enable_tts=False, enable_llm=False)
except Exception as e:
    print(f"[ERROR] Orchestrator init failed: {e}")
    GLOBAL_ORCHESTRATOR = None

def finalize_conversation(call_sid: str):
    """Finalize conversation and update database."""
    if call_sid not in SESSIONS:
        return
        
    sess = SESSIONS[call_sid]
    interaction_id = sess.get("interaction_id")
    
    if interaction_id:
        try:
            db_service.update_interaction_status(interaction_id, "completed")
        except Exception as e:
            print(f"[ERROR] Finalization error: {e}")
    
    if call_sid in SESSIONS:
        del SESSIONS[call_sid]

def get_empathetic_transfer_message(user_question: str) -> str:
    """Generate empathetic transfer message based on user situation."""
    q = user_question.lower()
    
    if any(w in q for w in ["décédé", "décès", "mort", "défunt", "deuil"]):
        return "Je suis vraiment désolée pour votre perte. Nos conseillers vont vous aider. Je vous mets en relation immédiatement."
    
    if "accident grave" in q or ("accident" in q and "hôpital" in q):
        return "Je comprends que c'est une situation urgente. Un spécialiste va prendre soin de vous. Veuillez patienter."
    
    if any(w in q for w in ["fraude", "arnaque", "vol"]):
        return "Nous prenons votre situation très au sérieux. Un agent spécialisé va vous aider. Patientez un instant."
    
    if any(w in q for w in ["litige", "plainte", "avocat", "procès"]):
        return "Votre situation demande une expertise spécialisée. Je vous mets en relation avec un conseiller qualifié."
    
    return "Votre demande nécessite l'expertise de nos conseillers. Je vous mets en relation immédiatement."

def check_if_should_escalate(bot_response: str, user_question: str, call_sid: str) -> bool:
    """Check if bot should escalate to human agent."""
    bot_unsure_keywords = [
        "je ne sais pas", "je ne peux pas vous aider", "désolée je ne peux pas",
        "je n'ai pas cette information", "je ne comprends pas votre question",
        "hors de mes compétences", "je ne peux traiter cette demande",
        "information non disponible", "données manquantes"
    ]
    
    # 2. Questions complexes spécifiques (REAL complex cases only)
    complex_keywords = [
        "réclamation urgente", "litige grave", "contentieux judiciaire", "plainte officielle",
        "avocat en charge", "procès en cours", "tribunal compétent", "procédure judiciaire engagée",
        "expert médical conteste", "invalidité contestée", "médecin conseil refuse",
        "succession bloquée", "héritage contesté", "testament invalidé",
        "fraude avérée", "escroquerie confirmée", "usurpation d'identité",
        "erreur grave de votre part", "dysfonctionnement majeur", "faute lourde"
    ]
    
    # 3. Mots-clés sensibles nécessitant empathie (décès, accidents graves, urgence médicale)
    sensitive_keywords = [
        "décédé", "décès", "mort", "défunt", "deuil",
        "accident grave", "hôpital", "urgence médicale",
        "fraude", "arnaque", "vol d'identité",
        "litige", "plainte", "avocat", "procès"
    ]
    
    bot_response_lower = bot_response.lower()
    user_question_lower = user_question.lower()
    
    # Vérifier si le bot avoue ne pas savoir
    for keyword in bot_unsure_keywords:
        if keyword in bot_response_lower:
            print(f"[AUTO-ESCALATION] Uncertainty detected in bot response: '{keyword}'")
            print(f"[AUTO-ESCALATION] Triggering automatic transfer to human agent")
            return True
    
    # Vérifier si c'est une question avec mots-clés sensibles (URGENT - décès, accident grave, etc)
    for keyword in sensitive_keywords:
        if keyword in user_question_lower:
            print(f"[AUTO-ESCALATION] SENSITIVE SITUATION detected: '{keyword}'")
            print(f"[AUTO-ESCALATION] Immediate transfer to specialized agent required")
            return True
    
    # Vérifier si c'est une question complexe
    for keyword in complex_keywords:
        if keyword in user_question_lower:
            print(f"[AUTO-ESCALATION] Complex query detected: '{keyword}'")
            print(f"[AUTO-ESCALATION] Question requires specialized expertise")
            return True
    
    # Remove short response auto-escalation - too many false positives
    # Normal responses like contact info should not trigger escalation
    
    # Vérifier la confiance (si disponible dans la session)
    if call_sid in SESSIONS:
        # Obtenir la confiance de la dernière décision AI
        # (Ceci nécessiterait de stocker la confiance dans la session)
        pass
    
    return False

def run_my_pipeline(user_text: str, call_sid: str, caller_phone: str) -> str:
    """Appelle le pipeline IA et retourne la reponse texte."""
    start = time.time()
    
    if call_sid not in SESSIONS:
        SESSIONS[call_sid] = {
            "conversation_history": [],
            "session_id": f"twilio_{call_sid}_{int(time.time())}",
            "turn_count": 0,
            "interaction_id": None,  # Will be set when first interaction is created
            "customer_id": f"twilio_{call_sid[:10]}",
            "total_start_time": time.time(),
            "has_said_goodbye": False
        }
    
    sess = SESSIONS[call_sid]
    sess["turn_count"] += 1
    
    if GLOBAL_ORCHESTRATOR is None:
        return "System temporarily unavailable. Please try again later."
    
    try:
        emotion_bert = {"sentiment": "NEUTRAL", "score": 0.5}
        audio_summary = {"duration_ms": 0}
        decision = run_ai_core(user_text, emotion_bert, audio_summary)
        
        if sess["interaction_id"] is None:
            try:
                interaction_id = db_service.create_interaction(
                    customer_id=sess["customer_id"],
                    customer_phone=caller_phone,
                    session_id=sess["session_id"],
                    intent=decision.get("intent", "general_inquiry"),
                    urgency=decision.get("urgency", "low"),
                    emotion=emotion_bert.get("sentiment", "NEUTRAL"),
                    confidence=decision.get("confidence", 0.5),
                    action_taken=decision.get("action", "rag_query"),
                    priority="high" if decision.get("urgency") == "high" else "normal",
                    reason=user_text[:200],
                    metadata={
                        "call_sid": call_sid,
                        "channel": "twilio", 
                        "turn_number": sess["turn_count"],
                        "phone_number": caller_phone
                    }
                )
                sess["interaction_id"] = interaction_id
            except Exception as e:
                sess["interaction_id"] = None
        
        # Generation de la reponse
        response = callbot_global_response(
            text=user_text,
            emotion_bert=emotion_bert,
            intent=decision.get("intent", "general_inquiry"),
            urgency=decision.get("urgency", "low"),
            action=decision.get("action", "rag_query"),
            confidence=decision.get("confidence", 0.5),
            session_id=sess["session_id"],
            conversation_history=sess["conversation_history"],
            orchestrator=GLOBAL_ORCHESTRATOR,
            enable_tts=False,
            enable_llm=False
        )
        
        bot_text = response.response_text
        elapsed = (time.time() - start) * 1000
        
        sess["conversation_history"].extend([
            {"role": "user", "text": user_text},
            {"role": "assistant", "text": bot_text},
        ])
        
        if sess["interaction_id"]:
            try:
                db_service.add_conversation_message(
                    interaction_id=sess["interaction_id"],
                    speaker="customer",
                    message_text=user_text,
                    turn_number=sess["turn_count"],
                    detected_intent=decision.get("intent"),
                    detected_emotion=emotion_bert.get("sentiment"),
                    confidence=decision.get("confidence"),
                    metadata={"call_sid": call_sid, "method": "twilio_voice"}
                )
                
                db_service.add_conversation_message(
                    interaction_id=sess["interaction_id"],
                    speaker="assistant", 
                    message_text=bot_text,
                    turn_number=sess["turn_count"],
                    metadata={"generation_time_ms": int(elapsed)}
                )
                
                db_service.update_interaction_conversation(
                    interaction_id=sess["interaction_id"],
                    customer_message=user_text,
                    bot_response=bot_text,
                    conversation_history=sess["conversation_history"],
                    execution_time_ms=int(elapsed),
                    action_result='{"result": "response_generated"}',
                    success=True
                )
            except Exception:
                pass
        
        return bot_text
        
    except Exception as e:
        return "Processing error occurred. Please try again or contact support."

@app.api_route("/wait", methods=["GET", "POST"])
async def wait_music():
    """Hold music endpoint."""
    resp = VoiceResponse()
    resp.play(HOLD_MUSIC_URL, loop=0)
    return Response(str(resp), media_type="application/xml")

@app.api_route("/agent", methods=["GET", "POST"])
async def agent_connect():
    """Agent connection to queue."""
    resp = VoiceResponse()
    resp.say("Connexion à la file support.", voice="man", language="fr-FR")
    dial = resp.dial()
    dial.queue(QUEUE_NAME)
    return Response(str(resp), media_type="application/xml")

@app.post("/queue_done")
async def queue_done(request: Request):
    """Queue exit handler."""
    form_data = await request.form()
    resp = VoiceResponse()
    resp.say("Merci. Au revoir.", voice="man", language="fr-FR")
    resp.hangup()
    return Response(str(resp), media_type="application/xml")

@app.post("/call_completed")
async def call_completed(request: Request):
    """Call completion handler."""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    call_status = form_data.get("DialCallStatus", "unknown")
    
    if call_sid in SESSIONS:
        finalize_conversation(call_sid)
    
    resp = VoiceResponse()
    if call_status in ["busy", "no-answer", "failed"]:
        resp.say("Désolé, notre conseiller n'est pas disponible. Au revoir.", 
                voice="Polly.Lea", language="fr-FR")
    else:
        resp.say("Merci d'avoir utilisé nos services. Au revoir.", 
                voice="Polly.Lea", language="fr-FR")
    
    resp.hangup()
    return Response(str(resp), media_type="application/xml")

@app.post("/hangup")
async def hangup_handler(request: Request):
    """Hangup handler."""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    
    if call_sid in SESSIONS:
        finalize_conversation(call_sid)
    
    return Response("", status_code=204)

@app.get("/")
def health():
    return {"ok": True, "service": "CNP Callbot", "sessions": len(SESSIONS)}

@app.post("/")
async def twilio_root_webhook(request: Request):
    """Root webhook for Twilio."""
    return await twilio_voice_webhook(request)

@app.post("/voice")
async def twilio_voice_webhook(request: Request):
    """Main voice webhook handler."""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    caller_phone = form_data.get("From", "unknown")
    speech_result = (form_data.get("SpeechResult") or "").strip()

    if call_sid not in SESSIONS:
        SESSIONS[call_sid] = {
            "conversation_history": [],
            "session_id": f"twilio_{call_sid}_{int(time.time())}",
            "turn_count": 0,
            "interaction_id": None,
            "customer_id": f"twilio_{call_sid[:10]}",
            "total_start_time": time.time(),
            "has_said_goodbye": False
        }
    
    sess = SESSIONS[call_sid]
    sess["turn_count"] += 1

    resp = VoiceResponse()

    if not speech_result:
        gather = resp.gather(
            input="speech",
            timeout=10,
            speech_timeout="auto",
            action="/voice",
            method="POST",
            action_on_empty_result=True,
            language="fr-FR",
        )
        gather.say(
            "Bonjour ! Je suis Julie de CNP Assurances. Comment puis-je vous aider ?",
            voice="Polly.Lea",
            language="fr-FR",
            rate="1.3"
        )
        return Response(str(resp), media_type="application/xml")
    else:
        if any(keyword in speech_result.lower() for keyword in ["agent", "humain", "conseiller", "personne", "file"]):
            transfer_msg = get_empathetic_transfer_message(speech_result)
            resp.say(transfer_msg, voice="Polly.Lea", language="fr-FR", rate="1.3")
            resp.play(HOLD_MUSIC_URL, loop=0)
            dial = resp.dial(timeout=30, action="/call_completed", method="POST")
            dial.number(HUMAN_AGENT_NUMBER)
            return Response(str(resp), media_type="application/xml")
        
        prompt = run_my_pipeline(speech_result, call_sid, caller_phone)
        should_escalate = check_if_should_escalate(prompt, speech_result, call_sid)
        
        if should_escalate:
            transfer_msg = get_empathetic_transfer_message(speech_result)
            resp.say(transfer_msg, voice="Polly.Lea", language="fr-FR", rate="1.3")
            resp.play(HOLD_MUSIC_URL, loop=0)
            dial = resp.dial(timeout=30, action="/call_completed", method="POST")
            dial.number(HUMAN_AGENT_NUMBER)
            return Response(str(resp), media_type="application/xml")

    if any(ending_word in speech_result.lower() for ending_word in ["merci", "au revoir", "c'est tout", "cela suffit"]):
        goodbye_message = "Merci pour votre appel. Êtes-vous satisfait de notre service ?"
        resp.say(goodbye_message, voice="Polly.Lea", language="fr-FR", rate="1.3")
        
        gather = resp.gather(
            input="speech",
            timeout=3,
            speech_timeout="auto",
            action="/feedback",
            method="POST",
            language="fr-FR"
        )
    else:
        gather = resp.gather(
            input="speech",
            timeout=5,
            speech_timeout="auto",
            action="/voice",
            method="POST",
            action_on_empty_result=True,
            language="fr-FR",
        )
        gather.say(
            prompt, 
            voice="Polly.Lea",  
            language="fr-FR",
            rate="1.3"  
        )
    
    resp.status_callback_url = "/hangup"
    resp.status_callback_method = "POST"

    return Response(str(resp), media_type="application/xml")

@app.post("/agent_call_completed")
async def agent_call_completed(request: Request):
    """Agent transfer completion handler."""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    dial_call_status = form_data.get("DialCallStatus", "unknown")
    
    resp = VoiceResponse()
    
    if dial_call_status == "completed":
        resp.say("Merci d'avoir utilisé notre service. Au revoir !", voice="Polly.Lea", language="fr-FR", rate="1.3")
    elif dial_call_status in ["no-answer", "failed"]:
        resp.say("Notre conseiller n'est pas disponible. Au revoir !", voice="Polly.Lea", language="fr-FR", rate="1.3")
    elif dial_call_status == "busy":
        resp.say("Notre conseiller est occupé. Au revoir !", voice="Polly.Lea", language="fr-FR", rate="1.3")
    else:
        resp.say("Désolée, connexion impossible. Au revoir !", voice="Polly.Lea", language="fr-FR", rate="1.3")
    
    resp.hangup()
    
    if call_sid in SESSIONS:
        del SESSIONS[call_sid]
    
    return Response(str(resp), media_type="application/xml")

@app.post("/hangup_feedback")
async def hangup_webhook(request: Request):
    """Hangup handler - saves no-feedback status."""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    call_status = form_data.get("CallStatus", "unknown")
    
    if call_sid in SESSIONS and SESSIONS[call_sid].get("interaction_id"):
        interaction_id = SESSIONS[call_sid]["interaction_id"]
        try:
            db_service.update_satisfaction_score(
                interaction_id=interaction_id,
                satisfaction_score=0,
                feedback_metadata={
                    "method": "hangup_auto",
                    "call_status": call_status,
                    "call_sid": call_sid,
                    "collected_at": datetime.now().isoformat(),
                    "reason": "user_hangup_no_feedback"
                }
            )
        except Exception:
            pass
    
    if call_sid in SESSIONS:
        del SESSIONS[call_sid]
    
    return {"status": "ok"}

@app.post("/feedback")
async def feedback_webhook(request: Request):
    """Satisfaction feedback handler."""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    speech_result = (form_data.get("SpeechResult") or "").strip().lower()
    
    satisfaction_score = -1
    response_message = "Merci pour votre appel."
    
    if any(w in speech_result for w in ["oui", "satisfait", "content"]):
        satisfaction_score = 1
        response_message = "Merci ! Je suis ravie d'avoir pu vous aider."
    elif any(w in speech_result for w in ["non", "insatisfait", "mécontent"]):
        satisfaction_score = 2
        response_message = "Merci pour votre retour. Nous allons améliorer notre service."
    
    if call_sid in SESSIONS and SESSIONS[call_sid].get("interaction_id") and satisfaction_score in [1, 2]:
        interaction_id = SESSIONS[call_sid]["interaction_id"]
        try:
            db_service.update_satisfaction_score(
                interaction_id=interaction_id,
                satisfaction_score=satisfaction_score,
                feedback_metadata={
                    "method": "twilio_voice",
                    "raw_response": speech_result,
                    "call_sid": call_sid,
                    "collected_at": datetime.now().isoformat()
                }
            )
        except Exception:
            pass
    
    resp = VoiceResponse()
    resp.say(response_message + " Au revoir !", voice="Polly.Lea", language="fr-FR", rate="1.3")
    resp.hangup()
    
    if call_sid in SESSIONS:
        del SESSIONS[call_sid]
    
    return Response(str(resp), media_type="application/xml")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000, log_level="info")