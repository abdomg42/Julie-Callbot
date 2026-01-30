"""
Serveur webhook pour connecter le CallBot avec le numéro de téléphone
Gère les appels entrants via Twilio/ZIWO
"""

import sys
import json
import base64
import asyncio
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Connect
import uvicorn

# Import de votre logique CallBot existante
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from main import process_single_turn, get_orchestrator
from inputs.entrypoint.run import get_inputs_service
from tool_router.src.database.db_service import db_service

# =============================================================================
# CONFIGURATION
# =============================================================================

app = FastAPI(title="CallBot Julie Webhook Server")

# État global pour les sessions actives
active_sessions: Dict[str, dict] = {}

# URL publique de votre serveur (à remplacer après déploiement)
PUBLIC_URL = "https://VOTRE-URL.ngrok.io"  # Ou votre URL Render/Railway


# =============================================================================
# ENDPOINTS WEBHOOK
# =============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "CallBot Julie Webhook Server",
        "version": "2.0"
    }


@app.post("/incoming-call")
async def handle_incoming_call(request: Request):
    """
    Appelé automatiquement quand quelqu'un appelle votre numéro.
    Retourne des instructions TwiML pour établir la connexion WebSocket.
    """
    print("\n" + "="*70)
    print("📞 APPEL ENTRANT REÇU")
    print("="*70)
    
    # Récupérer les infos de l'appel
    form_data = await request.form()
    caller_number = form_data.get("From", "Unknown")
    call_sid = form_data.get("CallSid", "Unknown")
    
    print(f"   📱 Numéro appelant: {caller_number}")
    print(f"   🆔 Call SID: {call_sid}")
    
    # Créer la réponse TwiML
    response = VoiceResponse()
    
    # Message de bienvenue
    response.say(
        "Bonjour, vous êtes en communication avec Julie, "
        "votre assistante virtuelle CNP Assurances. "
        "Comment puis-je vous aider aujourd'hui ?",
        language='fr-FR',
        voice='Polly.Celine'  # Voix française féminine
    )
    
    # Établir la connexion WebSocket pour le streaming audio
    connect = Connect()
    connect.stream(url=f'wss://{PUBLIC_URL.replace("https://", "").replace("http://", "")}/media-stream')
    response.append(connect)
    
    print("   ✅ Instructions TwiML envoyées")
    print("="*70 + "\n")
    
    return Response(content=str(response), media_type="application/xml")


@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    """
    Gère le flux audio en temps réel via WebSocket.
    Reçoit l'audio de l'utilisateur et envoie les réponses du bot.
    """
    await websocket.accept()
    
    print("\n" + "="*70)
    print("🔌 WEBSOCKET CONNECTÉ - CONVERSATION DÉMARRÉE")
    print("="*70)
    
    # Initialiser la session
    call_sid = None
    session_id = None
    interaction_id = None
    turn_number = 0
    conversation_history = []
    orchestrator = None
    
    # Buffer pour accumuler l'audio entrant
    audio_buffer = b''
    
    try:
        # Initialiser l'orchestrateur une seule fois
        orchestrator = get_orchestrator(enable_tts=True, enable_llm=False)
        inputs_service = get_inputs_service()
        
        async for message in websocket.iter_text():
            data = json.loads(message)
            event = data.get('event')
            
            # =================================================================
            # EVENT: START - Début de l'appel
            # =================================================================
            if event == 'start':
                call_sid = data['start']['callSid']
                session_id = f"call_{call_sid}"
                active_sessions[call_sid] = {
                    "session_id": session_id,
                    "start_time": data['start'].get('timestamp'),
                    "conversation_history": conversation_history
                }
                print(f"   🆔 Session créée: {session_id}")
            
            # =================================================================
            # EVENT: MEDIA - Réception audio de l'utilisateur
            # =================================================================
            elif event == 'media':
                # Décoder l'audio entrant (mulaw base64)
                payload = data['media']['payload']
                chunk = base64.b64decode(payload)
                audio_buffer += chunk
                
                # Quand on a assez d'audio (ex: 3 secondes à 8kHz mulaw = ~24KB)
                if len(audio_buffer) > 24000:
                    print(f"\n   🎤 Audio reçu ({len(audio_buffer)} bytes)")
                    
                    # TODO: Convertir mulaw → WAV/MP3
                    # TODO: Transcrire avec Whisper
                    # TODO: Appeler process_single_turn()
                    # TODO: Générer réponse TTS
                    # TODO: Envoyer audio de réponse via WebSocket
                    
                    # Pour l'instant, simuler une réponse
                    turn_number += 1
                    
                    # Réinitialiser le buffer
                    audio_buffer = b''
                    
                    # Simuler une réponse (VOUS DEVEZ REMPLACER PAR VOTRE LOGIQUE)
                    response_text = "Je vous écoute. Continuez s'il vous plaît."
                    
                    # Envoyer la réponse audio (format mulaw base64)
                    # response_audio_base64 = convert_to_mulaw_base64(response_audio)
                    # await websocket.send_text(json.dumps({
                    #     'event': 'media',
                    #     'streamSid': data['streamSid'],
                    #     'media': {
                    #         'payload': response_audio_base64
                    #     }
                    # }))
            
            # =================================================================
            # EVENT: STOP - Fin de l'appel
            # =================================================================
            elif event == 'stop':
                print("\n   📴 Appel terminé")
                if call_sid and call_sid in active_sessions:
                    del active_sessions[call_sid]
                
                # Finaliser l'interaction dans la DB
                if interaction_id:
                    db_service.update_interaction_status(interaction_id, "completed")
                
                break
    
    except WebSocketDisconnect:
        print("\n   ⚠️  WebSocket déconnecté")
    except Exception as e:
        print(f"\n   ❌ Erreur WebSocket: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await websocket.close()
        print("="*70 + "\n")


# =============================================================================
# UTILITAIRES (À IMPLÉMENTER)
# =============================================================================

def convert_mulaw_to_wav(mulaw_data: bytes) -> bytes:
    """Convertir mulaw → WAV pour Whisper"""
    # TODO: Utiliser audioop ou pydub
    pass


def convert_wav_to_mulaw(wav_data: bytes) -> bytes:
    """Convertir WAV → mulaw pour Twilio"""
    # TODO: Utiliser audioop ou pydub
    pass


# =============================================================================
# LANCEMENT DU SERVEUR
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 DÉMARRAGE DU SERVEUR WEBHOOK")
    print("="*70)
    print("   📡 Serveur: http://0.0.0.0:8000")
    print("   📚 Docs: http://0.0.0.0:8000/docs")
    print("="*70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
