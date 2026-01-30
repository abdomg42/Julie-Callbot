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

app = FastAPI()

# Sessions en memoire
SESSIONS: Dict[str, Dict[str, Any]] = {}

# =============================================================================
# BANNER ET HELPERS
# =============================================================================

def print_banner():
    print("\n" + "="*70)
    print("CALLBOT JULIE V2 - SYSTEME TWILIO")
    print("="*70)
    print("Serveur Twilio pret...")
    print("   Les appels Twilio seront traites automatiquement")
    print("="*70 + "\n")

def print_section(title: str, emoji: str = ">>"):
    print(f"\n{emoji} {title}")
    print("-" * 60)

# =============================================================================
# PRE-CHARGEMENT DE L ORCHESTRATEUR
# =============================================================================

print_banner()
print("[INIT] Initialisation du systeme...\n")

try:
    GLOBAL_ORCHESTRATOR = get_orchestrator(enable_tts=False, enable_llm=False)
    print("\n" + "="*70)
    print("[OK] SYSTEME PRET - EN ATTENTE D APPELS TWILIO")
    print("="*70 + "\n")
except Exception as e:
    print(f"[ERROR] Erreur lors de l'initialisation: {e}")
    GLOBAL_ORCHESTRATOR = None

def run_my_pipeline(user_text: str, call_sid: str) -> str:
    """Appelle le pipeline IA et retourne la reponse texte."""
    start = time.time()
    
    if call_sid not in SESSIONS:
        SESSIONS[call_sid] = {
            "conversation_history": [],
            "session_id": f"twilio_{call_sid}_{int(time.time())}",
            "turn_count": 0,
        }
        print_section(f"NOUVELLE SESSION: {call_sid[:20]}...", "[NEW]")
        print(f"   Session ID: {SESSIONS[call_sid]['session_id']}")
    
    sess = SESSIONS[call_sid]
    sess["turn_count"] += 1
    
    if GLOBAL_ORCHESTRATOR is None:
        return "Systeme indisponible. Veuillez reessayer."
    
    try:
        # Appel du core AI
        emotion_bert = {"sentiment": "NEUTRAL", "score": 0.5}
        audio_summary = {"duration_ms": 0}
        decision = run_ai_core(user_text, emotion_bert, audio_summary)
        
        print_section(f"TOUR {sess['turn_count']} - ANALYSE IA", "[AI]")
        print(f"   Texte: \"{user_text}\"")
        print(f"   Intention: {decision.get('intent', 'unknown')}")
        
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
        
        print(f"   Response in {elapsed:.0f}ms")
        print_section("REPONSE", "[BOT]")
        print(f"   {bot_text[:100]}{'...' if len(bot_text) > 100 else ''}")
        
        # Mise a jour historique
        sess["conversation_history"].extend([
            {"role": "user", "text": user_text},
            {"role": "assistant", "text": bot_text},
        ])
        
        return bot_text
        
    except Exception as e:
        print(f"[ERROR] Erreur pipeline: {e}")
        import traceback
        traceback.print_exc()
        return "Erreur lors du traitement. Veuillez reessayer."

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
    print(f"\n[VOICE] POST /voice reçu - CallSid: {call_sid}")
    speech_result = (form_data.get("SpeechResult") or "").strip()

    # Récupérer ou créer la session
    if call_sid not in SESSIONS:
        SESSIONS[call_sid] = {
            "conversation_history": [],
            "session_id": f"twilio_{call_sid}_{int(time.time())}",
            "turn_count": 0,
        }
    
    sess = SESSIONS[call_sid]
    sess["turn_count"] += 1
    turn_count = sess["turn_count"]
    
    print(f"[VOICE] Tour #{turn_count}")

    resp = VoiceResponse()

    if not speech_result:
        prompt = "Bonjour ! Je suis Julie de CNP Assurances. Comment puis-je vous aider ?"
    else:
        # ✅ VÉRIFIER SI L'UTILISATEUR VEUT UN AGENT HUMAIN
        if any(keyword in speech_result.lower() for keyword in ["agent", "humain", "parler à", "personne"]):
            print(f"[ESCALADE] Demande d'escalade détectée")
            return await escalate_to_human(call_sid, speech_result)
        
        prompt = run_my_pipeline(speech_result, call_sid)

    # 🔊 VOIX MEILLEURE + VITESSE OPTIMISÉE
    # Voice: woman (plus naturel), alice, man
    # Rate: 0.5-1.5 (0.9 = bon équilibre)
    
    # Si c'est la fin de la conversation (après 3+ tours), ajouter feedback
    if turn_count >= 3:
        print(f"[VOICE] Fin de conversation détectée - Ajout du feedback")
        resp.say(prompt, voice="woman", language="fr-FR", rate="0.9")
        
        # Ajouter le feedback de satisfaction
        resp.say(
            "Comment avez-vous trouvé notre service ? Appuyez sur 1 pour très satisfait, 2 pour satisfait, ou 3 pour insatisfait.",
            voice="woman",
            language="fr-FR",
            rate="0.9"
        )
        
        gather = resp.gather(
            input="dtmf",
            numDigits=1,
            timeout=10,
            action="/feedback",
            method="POST"
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
            voice="woman",  # ✅ Meilleure voix (femme)
            language="fr-FR",
            rate="0.9"  # ✅ Vitesse optimisée
        )

    return Response(str(resp), media_type="application/xml")

# ✅ ESCALADE VERS AGENT HUMAIN
AGENT_PHONE = "+33612345678"  # 👈 À REMPLACER PAR TON NUMÉRO D'AGENT

async def escalate_to_human(call_sid: str, user_message: str) -> Response:
    """Escalade l'appel vers un agent humain"""
    print(f"[ESCALADE] Transfert vers agent pour appel {call_sid}")
    
    resp = VoiceResponse()
    
    # Option 1 : Rediriger vers un numéro (si tu as un centre d'appels)
    resp.say(
        "D'accord, je vous mets en relation avec un de nos agents. Veuillez patienter.",
        voice="woman",
        language="fr-FR",
        rate="0.9"
    )
    
    # Rediriger l'appel
    resp.dial(AGENT_PHONE)
    
    # Si pas de réponse, raccrocher
    resp.hangup()
    
    return Response(str(resp), media_type="application/xml")

@app.post("/feedback")
async def feedback_webhook(request: Request):
    """Recueille le feedback de satisfaction (1=très satisfait, 2=satisfait, 3=insatisfait)"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    digits = form_data.get("Digits", "0")
    
    feedback_map = {
        "1": "Très satisfait ✅",
        "2": "Satisfait ✅",
        "3": "Insatisfait ⚠️"
    }
    
    feedback_text = feedback_map.get(digits, "Feedback non reçu")
    print(f"\n[FEEDBACK] Call {call_sid} - Note: {feedback_text}")
    
    # Dire merci et raccrocher
    resp = VoiceResponse()
    resp.say("Merci pour votre feedback. Au revoir !", voice="woman", language="fr-FR", rate="0.9")
    resp.hangup()
    
    # Nettoyer la session
    if call_sid in SESSIONS:
        del SESSIONS[call_sid]
    
    return Response(str(resp), media_type="application/xml")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("DEMARRAGE DU SERVEUR TWILIO")
    print("="*70)
    print("🚀 Serveur sur http://localhost:8000")
    print("📞 Webhook URL: http://localhost:8000/voice")
    print("🌐 Exposed via ngrok: ngrok http 8000")
    print("="*70 + "\n")
    
    # Demarrer le serveur
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
