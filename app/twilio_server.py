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

# Ajouter le repertoire parent au path
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

# Import du pipeline existant
from core.entrypoint import run_ai_core
from tool_router.entrypoint.entrypoint import callbot_global_response, get_orchestrator
from tool_router.src.database.db_service import db_service

app = FastAPI()

# Sessions en memoire
SESSIONS: Dict[str, Dict[str, Any]] = {}

# =============================================================================
# 🎵 HOLD MUSIC + QUEUE CONFIG (NEW)
# =============================================================================
QUEUE_NAME = "support"
HOLD_MUSIC_URL = "http://com.twilio.sounds.music.s3.amazonaws.com/MARKOVICHAMP-Borghestral.mp3"

# =============================================================================
# BANNER ET HELPERS (UNCHANGED)
# =============================================================================
def print_banner():
    print("\n" + "="*80)
    print("CNP ASSURANCES - CALLBOT JULIE SYSTEM v2.0")
    print("Voice AI Assistant with Human Escalation")
    print("="*80)
    print("Server Status: READY")
    print("Voice Engine: Amazon Polly Lea (French)")
    print("Database: PostgreSQL Connected")
    print("Human Escalation: +212628091058")
    print("Feedback Collection: Voice Recognition (Oui/Non)")
    print("="*80 + "\n")

def print_section(title: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {title}")
    print("-" * 80)

# =============================================================================
# PRE-CHARGEMENT DE L ORCHESTRATEUR (UNCHANGED)
# =============================================================================
print_banner()
print("[SYSTEM] Initializing CNP Assurances Callbot System...")
print("[SYSTEM] Loading AI orchestrator components...")

try:
    GLOBAL_ORCHESTRATOR = get_orchestrator(enable_tts=False, enable_llm=False)
    print("\n" + "="*80)
    print("[SUCCESS] SYSTEM OPERATIONAL - WAITING FOR TWILIO CALLS")
    print("[INFO] Natural Language Processing: ACTIVE")
    print("[INFO] RAG Knowledge Base: LOADED")
    print("[INFO] Database Logging: ENABLED")
    print("[INFO] Auto-Escalation: CONFIGURED")
    print("="*80 + "\n")
except Exception as e:
    print(f"[ERROR] System initialization failed: {e}")
    GLOBAL_ORCHESTRATOR = None

def finalize_conversation(call_sid: str):
    """Finalise une conversation et met à jour la base de données"""
    if call_sid not in SESSIONS:
        return
        
    sess = SESSIONS[call_sid]
    interaction_id = sess.get("interaction_id")
    
    if interaction_id:
        try:
            # Mettre à jour le statut de l'interaction
            db_service.update_interaction_status(interaction_id, "completed")
            
            # Calculer le temps total
            total_time = time.time() - sess.get("total_start_time", time.time())
            
            # Afficher le résumé
            print("\n" + "="*70)
            print("📊 RÉSUMÉ DE LA CONVERSATION TWILIO")
            print("="*70)
            print(f"   Session ID: {sess['session_id']}")
            print(f"   Interaction ID: {interaction_id}")
            print(f"   CallSid: {call_sid}")
            print(f"   Tours de parole: {sess['turn_count']}")
            print(f"   Durée totale: {total_time:.1f}s")
            print(f"   Messages échangés: {len(sess['conversation_history'])}")
            print("="*70)
            print("👋 FIN DE L'APPEL TWILIO - Merci d'avoir utilisé Callbot Julie!")
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"[ERROR] Erreur lors de la finalisation: {e}")
    
    # Nettoyer la session
    if call_sid in SESSIONS:
        del SESSIONS[call_sid]

def check_if_should_escalate(bot_response: str, user_question: str, call_sid: str) -> bool:
    """
    Vérifie si le bot doit escalader automatiquement vers un agent humain.
    Critères d'escalade :
    1. Le bot avoue ne pas savoir
    2. Réponse trop générique ou évasive
    3. Question très spécifique hors scope
    4. Confiance faible
    """
    
    # 1. Mots-clés indiquant que le bot ne sait pas (STRICT - only real uncertainty)
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
    
    bot_response_lower = bot_response.lower()
    user_question_lower = user_question.lower()
    
    # Vérifier si le bot avoue ne pas savoir
    for keyword in bot_unsure_keywords:
        if keyword in bot_response_lower:
            print(f"[AUTO-ESCALATION] Uncertainty detected in bot response: '{keyword}'")
            print(f"[AUTO-ESCALATION] Triggering automatic transfer to human agent")
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

def run_my_pipeline(user_text: str, call_sid: str) -> str:
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
        print_section(f"NEW SESSION CREATED: {call_sid[:15]}...", "SESSION")
        print(f"[SESSION] Customer ID: twilio_{call_sid[:10]}")
        print(f"[SESSION] Session ID: {SESSIONS[call_sid]['session_id']}")
        print(f"[SESSION] Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sess = SESSIONS[call_sid]
    sess["turn_count"] += 1
    
    if GLOBAL_ORCHESTRATOR is None:
        return "System temporarily unavailable. Please try again later."
    
    try:
        # Appel du core AI
        emotion_bert = {"sentiment": "NEUTRAL", "score": 0.5}
        audio_summary = {"duration_ms": 0}
        decision = run_ai_core(user_text, emotion_bert, audio_summary)
        
        print_section(f"AI PROCESSING", "AI")
        print(f"[INPUT] User Query: \"{user_text}\"")
        print(f"[ANALYSIS] Urgency Level: {decision.get('urgency', 'low').upper()}")
        print(f"[ANALYSIS] Confidence Score: {decision.get('confidence', 0.5):.2f}")
        print(f"[ANALYSIS] Action Required: {decision.get('action', 'rag_query')}")
        
        # Create database interaction if not exists
        # Créer l'interaction dans PostgreSQL (premier tour) comme main.py
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
                print(f"[DATABASE] Interaction created: {interaction_id}")
            except Exception as e:
                print(f"[WARNING] Database interaction creation failed: {e}")
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
        
        print(f"[PROCESSING] Response generation time: {elapsed:.0f}ms")
        print_section("BOT RESPONSE GENERATED", "RESPONSE")
        response_preview = bot_text[:150] + "..." if len(bot_text) > 150 else bot_text
        print(f"[OUTPUT] Response Length: {len(bot_text)} characters")
        print(f"[OUTPUT] Response Preview: {response_preview}")
        print(f"[SESSION] Conversation Turn: {sess['turn_count']} completed")
        
        # Mise a jour historique
        sess["conversation_history"].extend([
            {"role": "user", "text": user_text},
            {"role": "assistant", "text": bot_text},
        ])
        
        # Logger le message client et mettre à jour la DB comme main.py
        if sess["interaction_id"]:
            try:
                # Logger le message client
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
                
                # Logger la réponse du bot
                db_service.add_conversation_message(
                    interaction_id=sess["interaction_id"],
                    speaker="assistant", 
                    message_text=bot_text,
                    turn_number=sess["turn_count"],
                    metadata={"generation_time_ms": int(elapsed)}
                )
                
                # Mettre à jour l'interaction avec les données complètes
                success = db_service.update_interaction_conversation(
                    interaction_id=sess["interaction_id"],
                    customer_message=user_text,
                    bot_response=bot_text,
                    conversation_history=sess["conversation_history"],
                    execution_time_ms=int(elapsed),
                    action_result='{"result": "response_generated"}',
                    success=True
                )
                
                if success:
                    print(f"[DATABASE] Conversation data logged successfully")
                else:
                    print(f"[WARNING] Failed to update interaction data")
            except Exception as e:
                print(f"[WARNING] Database logging error: {e}")
        
        return bot_text
        
    except Exception as e:
        print(f"[ERROR] AI pipeline processing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Processing error occurred. Please try again or contact support."

# =============================================================================
# 🎵 NEW ENDPOINTS: HOLD MUSIC + AGENT
# =============================================================================
@app.api_route("/wait", methods=["GET", "POST"])
async def wait_music():
    """Hold music que la file d'attente joue en boucle"""
    resp = VoiceResponse()
    resp.play(HOLD_MUSIC_URL, loop=0)  # 0 = boucle infinie
    return Response(str(resp), media_type="application/xml")

@app.api_route("/agent", methods=["GET", "POST"])
async def agent_connect():
    """Numéro B: Agent appelle et se connecte au premier client en attente"""
    resp = VoiceResponse()
    resp.say("Connexion à la file support. Premier appel en attente...", voice="man", language="fr-FR")
    dial = resp.dial()
    dial.queue(QUEUE_NAME)
    return Response(str(resp), media_type="application/xml")

@app.post("/queue_done")
async def queue_done(request: Request):
    """Quand le client quitte la file"""
    form_data = await request.form()
    print(f"[QUEUE] Client quitté: {form_data.get('QueueResult')}")
    resp = VoiceResponse()
    resp.say("Merci. Au revoir.", voice="man", language="fr-FR")
    resp.hangup()
    return Response(str(resp), media_type="application/xml")

@app.post("/call_completed")
async def call_completed(request: Request):
    """Appelé quand un appel se termine ou quand un transfert échoue"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    call_status = form_data.get("DialCallStatus", "unknown")
    
    print(f"[CALL_COMPLETED] CallSid: {call_sid}, Status: {call_status}")
    
    # Finaliser la conversation si elle existe
    if call_sid in SESSIONS:
        finalize_conversation(call_sid)
    
    resp = VoiceResponse()
    if call_status in ["busy", "no-answer", "failed"]:
        resp.say("Désolé, notre conseiller n'est pas disponible. Veuillez réessayer plus tard. Au revoir.", 
                voice="Polly.Lea", language="fr-FR")
    else:
        resp.say("Merci d'avoir utilisé nos services. Au revoir.", 
                voice="Polly.Lea", language="fr-FR")
    
    resp.hangup()
    return Response(str(resp), media_type="application/xml")

@app.post("/hangup")
async def hangup_handler(request: Request):
    """Appelé quand l'appel se termine"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    call_status = form_data.get("CallStatus", "unknown")
    
    print(f"[HANGUP] CallSid: {call_sid}, Status: {call_status}")
    
    # Finaliser la conversation
    if call_sid in SESSIONS:
        finalize_conversation(call_sid)
    
    return Response("", status_code=204)

@app.get("/")
def health():
    return {"ok": True, "service": "Twilio Callbot", "sessions": len(SESSIONS)}

@app.post("/")
async def twilio_root_webhook(request: Request):
    """Twilio peut envoyer les appels sur /"""
    print(f"\n[ROOT] POST / reçu")
    try:
        form_data = await request.form()
        print(f"[ROOT] Form data keys: {list(form_data.keys())}")
        for key, value in form_data.items():
            print(f"[ROOT]   {key}: {value}")
    except Exception as e:
        print(f"[ROOT] Erreur parsing form: {e}")
    
    return await twilio_voice_webhook(request)

@app.post("/voice")
async def twilio_voice_webhook(request: Request):
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    caller_phone = form_data.get("From", "unknown")
    print(f"\n[VOICE] POST /voice reçu - CallSid: {call_sid}, From: {caller_phone}")
    speech_result = (form_data.get("SpeechResult") or "").strip()

    # Récupérer ou créer la session
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
    turn_count = sess["turn_count"]
    
    print(f"[VOICE] Tour #{turn_count}")

    resp = VoiceResponse()

    if not speech_result:
        # First call - wait for user to speak, don't auto-greet
        print(f"[CALL] Initial call - waiting for user input")
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
            rate="1.0"
        )
        return Response(str(resp), media_type="application/xml")
    else:
        # ✅ VERIFIER ESCALADE VERS AGENT HUMAIN - APPEL DIRECT
        if any(keyword in speech_result.lower() for keyword in ["agent", "humain", "conseiller", "personne", "file"]):
            print(f"[ESCALATION] Trigger phrase: '{speech_result}'")
            print(f"[TRANSFER] Connecting to human agent: +212628091058")
            print(f"[TRANSFER] Timeout configured: 30 seconds")
            resp.say(
                "Je vous mets en relation avec un conseiller. Veuillez patienter.",
                voice="Polly.Lea", language="fr-FR", rate="1.0"
            )
            # Appeler directement le numéro de l'agent humain
            dial = resp.dial(
                timeout=30,  # 30 secondes de sonnerie
                action="/call_completed",
                method="POST"
            )
            dial.number("+212628091058")  # Numéro de l'agent humain
            return Response(str(resp), media_type="application/xml")
        
        prompt = run_my_pipeline(speech_result, call_sid)
        
        # ✅ AUTO-ESCALADE: Vérifier si le bot ne peut pas bien répondre
        should_escalate = check_if_should_escalate(prompt, speech_result, call_sid)
        
        if should_escalate:
            print(f"[AUTO-ESCALATION] Complex query detected requiring human expertise")
            print(f"[AUTO-ESCALATION] Escalation trigger analysis completed")
            print(f"[TRANSFER] Automatic transfer to specialized agent initiated")
            print(f"[TRANSFER] Agent contact: +212628091058")
            resp.say(
                "Cette question nécessite l'expertise d'un conseiller spécialisé. Je vous mets en relation immédiatement.",
                voice="Polly.Lea", language="fr-FR", rate="1.0"
            )
            # Appeler directement le numéro de l'agent humain
            dial = resp.dial(
                timeout=30,  # 30 secondes de sonnerie
                action="/call_completed",
                method="POST"
            )
            dial.number("+212628091058")  # Numéro de l'agent humain
            return Response(str(resp), media_type="application/xml")

    # Si c'est la fin de la conversation (après 3+ tours), ajouter feedback
    if any(ending_word in speech_result.lower() for ending_word in ["merci", "au revoir", "c'est tout", "cela suffit"]):
        print(f"[CONVERSATION] End condition")
        print(f"[FEEDBACK] Initiating satisfaction survey collection")
        print(f"[FEEDBACK] Method: Voice recognition (French)")
        print(f"[FEEDBACK] Expected responses: Oui/Non")
        resp.say(prompt, voice="Polly.Lea", language="fr-FR", rate="1.0")
        
        # Ajouter le feedback de satisfaction
        resp.say(
            "Avez-vous été satisfait de notre service ? Répondez simplement par oui ou non.",
            voice="Polly.Lea",
            language="fr-FR",
            rate="1.0"
        )
        
        gather = resp.gather(
            input="speech",
            timeout=3,
            speech_timeout="auto",
            action="/feedback",
            method="POST",
            language="fr-FR"
        )
    else:
        # Conversation normale - continuer à écouter
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
            rate="1.0"  
        )
    
    # Ajouter statusCallback pour détecter les hangups
    resp.status_callback_url = "/hangup"
    resp.status_callback_method = "POST"

    return Response(str(resp), media_type="application/xml")

# ✅ ESCALADE VERS AGENT HUMAIN (REMPLACÉE PAR QUEUE)
async def escalate_to_human(call_sid: str, user_message: str) -> Response:
    """REMPLACÉE PAR FILE D'ATTENTE - À SUPPRIMER"""
    pass

@app.post("/call_completed")
async def call_completed(request: Request):
    """Appelé quand l'appel vers l'agent humain se termine"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    dial_call_status = form_data.get("DialCallStatus", "unknown")
    dial_call_duration = form_data.get("DialCallDuration", "0")
    
    print(f"\n[CALL_COMPLETED] Human agent call terminated")
    print(f"[CALL_COMPLETED] Call ID: {call_sid}")
    print(f"[CALL_COMPLETED] Agent call status: {dial_call_status}")
    print(f"[CALL_COMPLETED] Call duration: {dial_call_duration} seconds")        
    if dial_call_status == "failed":
        print(f"[ERROR] Transfer failed - Check:")
        print(f"[ERROR] - Phone number: +212628091058 (Morocco format)")
        print(f"[ERROR] - Twilio international permissions")
        print(f"[ERROR] - Account balance and limits")   
    if dial_call_status == "failed":
        print(f"[ERROR] Transfer failed - possible issues:")
        print(f"[ERROR] - Check phone number format: +212628091058")
        print(f"[ERROR] - Verify Twilio account permissions")
        print(f"[ERROR] - Check caller ID configuration")
        print(f"[ERROR] - Verify international calling enabled")    
    resp = VoiceResponse()
    
    if dial_call_status == "completed":
        # L'appel s'est bien passé
        resp.say("Merci d'avoir utilisé notre service. Au revoir !", voice="Polly.Lea", language="fr-FR", rate="1.0")
    elif dial_call_status == "no-answer" or dial_call_status == "failed":
        # Pas de réponse ou échec - proposer alternatives
        resp.say("Notre conseiller n'est pas disponible. Vous pouvez rappeler au 0800 000 000 ou laisser vos coordonnées sur notre site web. Au revoir !", 
                 voice="Polly.Lea", language="fr-FR", rate="1.0")
    elif dial_call_status == "busy":
        # Occupé
        resp.say("Notre conseiller est occupé. Veuillez rappeler dans quelques minutes au 0800 000 000. Au revoir !", 
                 voice="Polly.Lea", language="fr-FR", rate="1.0")
    else:
        # Autres erreurs
        resp.say("Désolée, impossible de vous connecter à un conseiller. Veuillez rappeler plus tard. Au revoir !", 
                 voice="Polly.Lea", language="fr-FR", rate="1.0")
    
    resp.hangup()
    
    # Nettoyer la session
    if call_sid in SESSIONS:
        del SESSIONS[call_sid]
        print(f"[SESSION] Session terminated after agent transfer: {call_sid[:15]}...")
    
    return Response(str(resp), media_type="application/xml")

@app.post("/hangup")
async def hangup_webhook(request: Request):
    """Appelé quand l'utilisateur raccroche - Enregistrer satisfaction = 0 (Quitté sans feedback)"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    call_status = form_data.get("CallStatus", "unknown")
    
    print(f"\n[HANGUP] Call termination detected")
    print(f"[HANGUP] Call ID: {call_sid}")
    print(f"[HANGUP] Call status: {call_status}")
    print(f"[HANGUP] Reason: User disconnected before feedback collection")
    
    # Auto-assign satisfaction score = 0 for hangups without feedback
    if call_sid in SESSIONS and SESSIONS[call_sid].get("interaction_id"):
        interaction_id = SESSIONS[call_sid]["interaction_id"]
        print(f"[DATABASE] Auto-assigning satisfaction score: 0 (No feedback - hangup)")
        try:
            success = db_service.update_satisfaction_score(
                interaction_id=interaction_id,
                satisfaction_score=0,  # 0 = Quit without feedback
                feedback_metadata={
                    "method": "hangup_auto",
                    "call_status": call_status,
                    "call_sid": call_sid,
                    "collected_at": datetime.now().isoformat(),
                    "reason": "user_hangup_no_feedback"
                }
            )
            if success:
                print(f"[DATABASE] Hangup satisfaction score saved successfully")
                print(f"[DATABASE] Interaction ID: {interaction_id}")
            else:
                print(f"[ERROR] Failed to save hangup satisfaction score")
        except Exception as e:
            print(f"[ERROR] Database error during hangup processing: {str(e)}")
    
    # Session cleanup
    if call_sid in SESSIONS:
        del SESSIONS[call_sid]
        print(f"[SESSION] Session cleaned up: {call_sid[:15]}...")
    
    return {"status": "ok"}

@app.post("/feedback")
async def feedback_webhook(request: Request):
    """Recueille le feedback de satisfaction (oui/non)"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    speech_result = (form_data.get("SpeechResult") or "").strip().lower()
    
    # Analyser la réponse vocale
    satisfaction_score = -1
    feedback_text = "Feedback non reçu"
    
    if "oui" in speech_result or "satisfait" in speech_result or "content" in speech_result:
        satisfaction_score = 1  # Database expects 1 for satisfied
        feedback_text = "Satisfait ✅"
        response_message = "Merci ! Je suis ravie d'avoir pu vous aider."
    elif "non" in speech_result or "insatisfait" in speech_result or "mécontent" in speech_result:
        satisfaction_score = 2  # Database expects 2 for unsatisfied
        feedback_text = "Insatisfait ⚠️"
        response_message = "Merci pour votre retour. Nous allons améliorer notre service."
    else:
        satisfaction_score = -1
        feedback_text = "Réponse non comprise"
        response_message = "Merci pour votre appel."
    
    print(f"\n[FEEDBACK] Satisfaction survey response received")
    print(f"[FEEDBACK] Call ID: {call_sid}")
    print(f"[FEEDBACK] Raw speech input: '{speech_result}'")
    print(f"[FEEDBACK] Input length: {len(speech_result)} characters")
    
    # Analyser la réponse vocale
    satisfaction_score = -1
    feedback_text = "No feedback received"
    
    if "oui" in speech_result or "satisfait" in speech_result or "content" in speech_result:
        satisfaction_score = 1  # Database expects 1 for satisfied
        feedback_text = "Customer satisfied"
        response_message = "Merci ! Je suis ravie d'avoir pu vous aider."
    elif "non" in speech_result or "insatisfait" in speech_result or "mécontent" in speech_result:
        satisfaction_score = 2  # Database expects 2 for unsatisfied
        feedback_text = "Customer unsatisfied"
        response_message = "Merci pour votre retour. Nous allons améliorer notre service."
    else:
        satisfaction_score = -1
        feedback_text = "Response not understood"
        response_message = "Merci pour votre appel."
    
    print(f"[ANALYSIS] Feedback classification: {feedback_text}")
    print(f"[ANALYSIS] Satisfaction score: {satisfaction_score}")
    print(f"[ANALYSIS] Response category: {'POSITIVE' if satisfaction_score == 1 else 'NEGATIVE' if satisfaction_score == 2 else 'UNCLEAR'}")
    
    # Database persistence
    if call_sid in SESSIONS and SESSIONS[call_sid].get("interaction_id") and satisfaction_score in [1, 2]:
        interaction_id = SESSIONS[call_sid]["interaction_id"]
        print(f"[DATABASE] Attempting to save feedback to database")
        print(f"[DATABASE] Interaction ID: {interaction_id}")
        print(f"[DATABASE] Satisfaction score: {satisfaction_score}")
        try:
            success = db_service.update_satisfaction_score(
                interaction_id=interaction_id,
                satisfaction_score=satisfaction_score,
                feedback_metadata={
                    "method": "twilio_voice",
                    "raw_response": speech_result,
                    "call_sid": call_sid,
                    "collected_at": datetime.now().isoformat()
                }
            )
            if success:
                status_label = "SATISFIED" if satisfaction_score == 1 else "UNSATISFIED"
                print(f"[DATABASE] Feedback successfully saved - Status: {status_label}")
                print(f"[DATABASE] Record ID: {interaction_id}")
            else:
                print(f"[ERROR] Database save operation failed for interaction: {interaction_id}")
        except Exception as e:
            print(f"[ERROR] Database exception during feedback save: {str(e)}")
    else:
        print(f"[WARNING] Feedback not saved to database")
        print(f"[DEBUG] Call exists in sessions: {call_sid in SESSIONS}")
        if call_sid in SESSIONS:
            print(f"[DEBUG] Interaction ID available: {SESSIONS[call_sid].get('interaction_id')}")
        print(f"[DEBUG] Satisfaction score valid: {satisfaction_score in [1, 2]}")
    
    # Dire merci et raccrocher
    resp = VoiceResponse()
    resp.say(response_message + " Au revoir !", voice="Polly.Lea", language="fr-FR", rate="1.0")
    resp.hangup()
    
    # Nettoyer la session
    if call_sid in SESSIONS:
        del SESSIONS[call_sid]
    
    return Response(str(resp), media_type="application/xml")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("CNP ASSURANCES CALLBOT JULIE - PRODUCTION DEPLOYMENT")
    print("="*80)
    print("Service Status: STARTING")
    print("Port: 8000")
    print("Protocol: HTTP/HTTPS")
    print("Human Escalation Number: +212628091058")
    print("="*80 + "\n")
    
    print("[SYSTEM] Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")