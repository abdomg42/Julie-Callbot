
import sys
import time
import base64
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure all modules are importable
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from core.entrypoint import run_ai_core
from inputs.entrypoint.run import run_inputs, get_inputs_service
from tool_router.entrypoint.entrypoint import (
    callbot_global_response, 
    get_orchestrator, 
    play_audio_response
)

# 🆕 Import du service de base de données
from tool_router.src.database.db_service import db_service


# =============================================================================
# CONFIGURATION
# =============================================================================

CONFIG = {
    "enable_tts": True,           # Enable TTS for audio output
    "enable_llm": False,          # Keep disabled for faster responses (templates are good enough)
    "auto_play_audio": True,      # ✅ ACTIVÉ - Jouer automatiquement l'audio
    "max_conversation_turns": 10, # Max turns before ending
    "silence_timeout_ms": 2000,   # Reduced from 3000ms to 2000ms for faster responses
    "end_keywords": [
        "au revoir", "merci au revoir", "bye", "goodbye", "fin", "terminé", "fini",
        "c'est tout", "c est tout", "merci c'est tout", "merci c est tout", 
        "merci bonne journée", "merci à bientôt", "ça suffit", "stop", "arrêt"
    ],
    "collect_feedback": True,     # 🆕 Collecter le feedback client
    "feedback_timeout": 10,       # 🆕 Timeout en secondes pour le feedback
}


# =============================================================================
# CONVERSATION STATE
# =============================================================================
conversation_state = {
    "has_said_goodbye": False,
    "goodbye_count": 0
}


# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def print_banner():
    """Print startup banner."""
    print("\n" + "="*70)
    print("🤖 CALLBOT JULIE V2 - SYSTÈME DE RÉPONSE AUTOMATIQUE")
    print("="*70)
    print("📞 En attente d'appel...")
    print("   Parlez après le bip pour commencer")
    print("   Dites 'au revoir' pour terminer")
    print("="*70 + "\n")


def print_section(title: str, emoji: str = "📋"):
    """Print a section header."""
    print(f"\n{emoji} {title}")
    print("─" * 60)

# FeedBack 
def collect_feedback(
    interaction_id: str,
    session_id: str,
    last_action: str = None
) -> Optional[int]:
    """
    Collecte le feedback du client à la fin de l'appel.
    
    Args:
        interaction_id: ID de l'interaction dans la base de données
        session_id: ID de la session
        last_action: Dernière action effectuée (pour ne pas demander si handoff)
        
    Returns:
        satisfaction_score: 1 (Satisfait) ou 2 (Insatisfait) ou None
    """
    # Ne pas demander de feedback si transfert vers humain
    if last_action == "human_handoff":
        print("\n📊 Feedback non collecté (transfert vers agent humain)")
        return None
    
    print("\n" + "="*70)
    print("📊 FEEDBACK CLIENT")
    print("="*70)
    print("💬 Notre service vous a-t-il été utile ?")
    print("")
    print("   1️⃣  Appuyez sur la touche [1] pour OUI (Satisfait)")
    print("   2️⃣  Appuyez sur la touche [2] pour NON (Insatisfait)")
    print("")
    print(f"⏳ En attente de votre réponse (timeout: {CONFIG['feedback_timeout']}s)...")
    print("="*70)
    
    satisfaction_score = None
    start_time = time.time()
    
    # Méthode 1: Essayer avec la bibliothèque keyboard (si disponible)
    try:
        import keyboard
        timeout = CONFIG['feedback_timeout']
        
        while time.time() - start_time < timeout:
            if keyboard.is_pressed('1'):
                satisfaction_score = 1
                time.sleep(0.3)  # Éviter les doubles pressions
                break
            elif keyboard.is_pressed('2'):
                satisfaction_score = 2
                time.sleep(0.3)
                break
            time.sleep(0.1)
        
        if satisfaction_score is None:
            print("\n   ⏱️  Pas de réponse reçue (timeout)")
    
    except ImportError:
        # Méthode 2: Fallback avec input() standard
        print("\n💡 Entrez votre réponse et appuyez sur Entrée:")
        try:
            import select
            import sys
            
            # Timeout pour Windows (pas de select sur stdin)
            response = input("   (1 = Oui, 2 = Non): ").strip()
            
            if response == '1':
                satisfaction_score = 1
            elif response == '2':
                satisfaction_score = 2
            else:
                print("   ⚠️ Réponse non reconnue")
        except Exception as e:
            print(f"   ⚠️ Erreur lors de la collecte: {e}")
    
    # Afficher la réponse
    if satisfaction_score == 1:
        print("\n   ✅ Merci ! Vous avez répondu OUI (Satisfait)")
        print("   🙏 Nous sommes ravis d'avoir pu vous aider !")
    elif satisfaction_score == 2:
        print("\n   ❌ Merci pour votre retour (Insatisfait)")
        print("   📝 Nous allons améliorer notre service.")
    
    # Enregistrer dans PostgreSQL
    if satisfaction_score and interaction_id:
        try:
            response_time = time.time() - start_time
            success = db_service.update_satisfaction_score(
                interaction_id=interaction_id,
                satisfaction_score=satisfaction_score,
                feedback_metadata={
                    "method": "keyboard",
                    "response_time_seconds": round(response_time, 2),
                    "session_id": session_id,
                    "collected_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            )
            
            if success:
                # Afficher les statistiques en temps réel
                print("\n" + "-"*50)
                stats = db_service.get_satisfaction_statistics(days=7)
                print(f"📈 Statistiques (7 derniers jours):")
                print(f"   • Taux de satisfaction: {stats['satisfaction_rate']:.1f}%")
                print(f"   • Feedbacks collectés: {stats['feedbacks_collected']}/{stats['total_interactions']} ({stats['feedback_rate']:.1f}%)")
                print(f"   • ✅ Satisfaits: {stats['satisfied']} | ❌ Insatisfaits: {stats['unsatisfied']}")
                print("-"*50)
        
        except Exception as e:
            print(f"   ⚠️ Erreur enregistrement feedback: {e}")
    
    return satisfaction_score

def process_single_turn(
    orchestrator,
    conversation_history: list,
    turn_number: int = 1,
    session_id: str = None,
    interaction_id: str = None,
    inputs_service = None
) -> Dict[str, Any]:
    """
    Process a single conversation turn.
    
    Flow: Audio → STT → Emotion → Decision → RAG/Handoff → TTS → Audio Output
    
    Args:
        orchestrator: Reusable orchestrator instance
        conversation_history: List of previous exchanges
        turn_number: Current turn number
        session_id: Session identifier for DB logging
        interaction_id: Existing interaction ID (None for first turn)
        
    Returns:
        Dict with response and metadata
    """
    start_time = time.time()
    
    # =========================================================================
    # STEP 1: AUDIO INPUT (MG - Callbot_julie_inputs)
    # =========================================================================
    print_section(f"TOUR {turn_number} - ÉCOUTE EN COURS", "🎤")
    # Modèles déjà chargés - audio prêt immédiatement
    
    try:
        inputs = run_inputs()
        text = inputs.get("full_text", "")
        emotion_bert = inputs.get("emotion_bert", {"sentiment": "NEUTRAL", "score": 0.5})
        # emotion_wav2vec removed
        audio_summary = inputs.get("audio_summary", {})
        
        # Debug: Show full text details
        print(f"   ✅ Texte: \"{text}\"")
        print(f"   ✅ Émotion BERT: {emotion_bert.get('sentiment', 'N/A')}")
        print(f"   ✅ Durée audio: {audio_summary.get('duration_ms', 0)}ms")
        
    except Exception as e:
        print(f"   ❌ Erreur d'entrée audio: {e}")
        return {"error": str(e), "should_continue": False}
    
    # =========================================================================
    # CHECK CONVERSATION STATE
    # =========================================================================
    # Si on a déjà dit goodbye, arrêter immédiatement
    if conversation_state["has_said_goodbye"]:
        print("   🛑 Conversation déjà terminée - arrêt")
        return {
            "response_text": "",
            "should_continue": False,
            "action": "conversation_ended"
        }
    
    # Check for empty input or just noise
    if not text or text.strip() == "" or text.strip() in ["...", ".", ",", " "]:
        print("   ⚠️  Aucune parole détectée ou silence")
        # Si on a dit goodbye récemment et maintenant silence, terminer
        if conversation_state["goodbye_count"] > 0:
            print("   🛑 Silence après goodbye - fin de conversation")
            conversation_state["has_said_goodbye"] = True
            return {
                "response_text": "",
                "should_continue": False,
                "action": "conversation_ended"
            }
        return {
            "response_text": "Je n'ai pas entendu. Pouvez-vous répéter votre question s'il vous plaît ?",
            "should_continue": True,
            "action": "repeat_request"
        }
    
    # Check for end keywords
    text_lower = text.lower().strip()
    should_say_goodbye = False
    
    # Détecter les mots de fin (plus flexible)
    for keyword in CONFIG["end_keywords"]:
        if keyword in text_lower:
            print(f"   👋 Mot de fin détecté: '{keyword}'")
            should_say_goodbye = True
            break
    
    # Détecter aussi "merci" seul à la fin d'une phrase courte
    if not should_say_goodbye and "merci" in text_lower and len(text_lower.split()) <= 3:
        should_say_goodbye = True
        print(f"   👋 Remerciement final détecté: '{text_lower}'")
    
    # =========================================================================
    # STEP 2: AI DECISION (RED - core)
    # =========================================================================
    print_section("ANALYSE IA", "🧠")
    
    try:
        # NOTE: Order is (full_text, emotion_bert, audio_summary)
        decision = run_ai_core(text, emotion_bert, audio_summary)
        
        """
        decision = {
            "intent": "declare_claim" | "check_policy" | "update_info" | ...,
            "urgency": "low" | "med" | "high",
            "action": "rag_query" | "escalate",
            "confidence": 0.0 - 1.0
        }
        """
        
        intent = decision.get("intent", "unknown")
        urgency = decision.get("urgency", "low")
        action = decision.get("action", "rag_query")
        confidence = decision.get("confidence", 0.0)
        
        print(f"   ✅ Intention: {intent}")
        print(f"   ✅ Urgence: {urgency}")
        print(f"   ✅ Action: {action}")
        print(f"   ✅ Confiance: {confidence:.2f}")
        
    except Exception as e:
        print(f"   ⚠️  Erreur AI Core: {e}")
        # Fallback to default decision
        decision = {
            "intent": "general_inquiry",
            "urgency": "low",
            "action": "rag_query",
            "confidence": 0.5
        }
        intent, urgency, action, confidence = "general_inquiry", "low", "rag_query", 0.5
    
    # =========================================================================
    # STEP 2.5: LOGIQUE DE DÉCISION RAG vs HUMAN HANDOFF
    # =========================================================================
    print_section("ROUTAGE INTELLIGENT", "🔀")
    
    should_handoff = False
    handoff_reason = None
    should_ask_repeat = False
    
    # 🆕 DÉTECTION DE TEXTE INCOMPRÉHENSIBLE (mauvaise transcription Whisper)
    # Mais PAS pour des mots normaux comme "bonjour", "merci", etc.
    
    # Mots reconnaissables (même si AI Core ne les comprend pas parfaitement)
    recognizable_words = [
        "bonjour", "bonsoir", "salut", "hello", "hi",
        "merci", "au revoir", "aurevoir", "bye", "adieu",
        "oui", "non", "peut-être", "ok", "d'accord",
        "sinistre", "contrat", "assurance", "police",
        "remboursement", "paiement", "déclaration"
    ]
    
    # Vérifier si le texte contient au moins un mot reconnaissable
    text_words = text.lower().strip().split()
    has_recognizable_word = any(word in " ".join(text_words) for word in recognizable_words)
    
    # Détecter du vrai bruit/garbage
    is_garbage_text = False
    if not has_recognizable_word:
        # Texte très court ET confiance très basse = probable garbage
        if len(text_words) == 1 and len(text.strip()) < 4 and confidence < 0.2:
            is_garbage_text = True
        # Ou intention unknown + action escalate + confiance très basse
        elif intent == "unknown" and action == "escalate" and confidence < 0.15:
            is_garbage_text = True
    
    # Demander de répéter SEULEMENT pour du vrai garbage
    if is_garbage_text:
        should_ask_repeat = True
        print(f"   🔄 Texte non reconnu (confiance: {confidence:.0%}) → Demander de répéter")
    
    # Si on doit demander de répéter, ne pas faire d'escalade
    if should_ask_repeat:
        repeat_text = "Je n'ai pas bien compris votre demande. Pouvez-vous reformuler s'il vous plaît ?"
        
        # Générer l'audio TTS pour la demande de répétition
        audio_base64 = None
        if CONFIG["enable_tts"]:
            try:
                audio_result = orchestrator.tts.generate_speech(repeat_text, emotion="neutral")
                audio_base64 = audio_result.get("audio_base64")
                print(f"   🔊 TTS généré pour répétition")
            except Exception as e:
                print(f"   ⚠️  Erreur TTS: {e}")
        
        # Jouer l'audio
        if audio_base64:
            print_section("LECTURE AUDIO", "🔊")
            try:
                # Créer un objet response-like pour play_audio_response
                class RepeatResponse:
                    def __init__(self, text, audio):
                        self.response_text = text
                        self.audio_base64 = audio
                
                play_audio_response(RepeatResponse(repeat_text, audio_base64), blocking=True)
                print("   ✅ Audio joué")
            except Exception as e:
                print(f"   ⚠️  Erreur audio: {e}")
        
        print_section("DEMANDE DE RÉPÉTITION", "🔄")
        print(f"   {repeat_text}")
        
        return {
            "response_text": repeat_text,
            "should_continue": True,
            "action": "repeat_request",
            "interaction_id": interaction_id
        }
    
    # 1. Action de l'AI Core demande escalade (SEULEMENT si confiance > 0.5)
    if action == "escalate" and confidence > 0.5:
        should_handoff = True
        handoff_reason = "Escalade demandée par l'AI Core"
    
    # 2. Urgence élevée
    if urgency == "high":
        should_handoff = True
        handoff_reason = "Urgence élevée détectée"
    
    # 3. Émotion négative forte (client en détresse)
    emotion_score = emotion_bert.get("score", 0.5)
    emotion_label = emotion_bert.get("sentiment", "NEUTRAL").upper()
    if emotion_label in ["NEGATIVE", "ANGRY"] and emotion_score > 0.8:
        should_handoff = True
        handoff_reason = f"Client en détresse émotionnelle ({emotion_label}: {emotion_score:.0%})"
    
    # 4. Intentions nécessitant un humain
    human_required_intents = [
        "claim_dispute", "legal_issue", "complaint", 
        "contract_cancellation", "fraud_report", "death_claim"
    ]
    if intent in human_required_intents:
        should_handoff = True
        handoff_reason = f"Intention nécessitant un agent humain: {intent}"
    
    # 5. Mots-clés sensibles dans le texte
    sensitive_keywords = [
        "avocat", "plainte", "procès", "litige", "fraude", "arnaque",
        "décès", "mort", "suicide", "urgence médicale", "hôpital"
    ]
    text_lower = text.lower()
    for keyword in sensitive_keywords:
        if keyword in text_lower:
            should_handoff = True
            handoff_reason = f"Mot-clé sensible détecté: '{keyword}'"
            break
    
    if should_handoff:
        print(f"   ⚠️  TRANSFERT REQUIS: {handoff_reason}")
        action = "escalate"  # Override action
    else:
        action = "rag_query"  # Force RAG processing
    
    # =========================================================================
    # STEP 2.6: CRÉER L'INTERACTION DANS PostgreSQL (premier tour)
    # =========================================================================
    if interaction_id is None:
        try:
            customer_id = f"CUST-{session_id.split('_')[-1]}" if session_id else "CUST-UNKNOWN"
            interaction_id = db_service.create_interaction(
                customer_id=customer_id,
                session_id=session_id or "unknown",
                intent=intent,
                urgency=urgency,
                emotion=emotion_label,
                confidence=confidence,
                action_taken=action,
                priority="high" if urgency == "high" else "normal",
                reason=text[:200],
                metadata={
                    "turn_number": turn_number,
                    "audio_duration_ms": audio_summary.get("duration_ms", 0),
                    "emotion_score": emotion_score
                }
            )
            print(f"   ✅ Interaction créée: {interaction_id}")
        except Exception as db_error:
            print(f"   ⚠️  Erreur création interaction: {db_error}")
            interaction_id = None
    
    # Logger le message client
    if interaction_id:
        try:
            db_service.add_conversation_message(
                interaction_id=interaction_id,
                speaker="customer",
                message_text=text,
                turn_number=turn_number,
                detected_intent=intent,
                detected_emotion=emotion_label,
                confidence=confidence,
                metadata={"emotion_score": emotion_score, "urgency": urgency}
            )
        except Exception as db_error:
            print(f"   ⚠️  Erreur logging message client: {db_error}")
    
    # =========================================================================
    # STEP 3: RESPONSE GENERATION (IBRAHIM - tool_router)
    # =========================================================================
    print_section("GÉNÉRATION DE RÉPONSE", "🎯")
    
    # Check for goodbye BEFORE generating standard response
    if should_say_goodbye:
        # Marquer la conversation comme terminée
        conversation_state["has_said_goodbye"] = True
        conversation_state["goodbye_count"] += 1
        
        # Create a goodbye response with integrated satisfaction question
        goodbye_with_feedback = "Merci pour votre appel. Comment avez-vous trouvé notre service aujourd'hui ? Êtes-vous satisfait ?"
        
        response = type('Response', (), {
            'response_text': goodbye_with_feedback,
            'action': "end_call_with_feedback",
            'confidence': 1.0,
            'next_step': "collect_feedback",
            'documents_used': [],
            'audio_base64': None,
            'metadata': {"is_goodbye": True, "collect_feedback": True}
        })()
        
        # Generate TTS for goodbye message with feedback question if enabled
        if CONFIG["enable_tts"]:
            try:
                audio_result = orchestrator.tts.generate_speech(
                    text=response.response_text,
                    emotion="neutral"
                )
                response.audio_base64 = audio_result.get("audio_base64", "")
                print(f"   ✅ TTS généré pour au revoir + feedback en {audio_result.get('generation_time', 0):.2f}s")
            except Exception as e:
                print(f"   ⚠️  Erreur TTS au revoir: {e}")
        
        print("   🛑 Conversation marquée comme terminée avec collecte feedback")
    else:
        # Standard response generation
        response = callbot_global_response(
            text=text,
            emotion_bert=emotion_bert,
            intent=intent,
            urgency=urgency,
            action=action,
            confidence=confidence,
            session_id=session_id or ("call_" + str(int(time.time()))),
            conversation_history=conversation_history,
            orchestrator=orchestrator,
            enable_tts=CONFIG["enable_tts"],
            enable_llm=CONFIG["enable_llm"]
        )
    
    # Ajouter handoff_reason si applicable
    if should_handoff and handoff_reason:
        response.metadata["handoff_reason"] = handoff_reason
        response.action = "human_handoff"
        response.next_step = "transfer"
    
    print(f"   ✅ Action: {response.action}")
    print(f"   ✅ Confiance: {response.confidence:.2f}")
    print(f"   ✅ Documents utilisés: {len(response.documents_used)}")
    
    # =========================================================================
    # STEP 4: OUTPUT RESPONSE
    # =========================================================================
    print_section("RÉPONSE", "💬")
    print(f"   {response.response_text}")
    
    # ⚡ OPTIMIZED: Non-blocking audio playback
    if response.audio_base64:
        print_section("LECTURE AUDIO", "🔊")
        try:
            # Use non-blocking playback for better UX
            play_audio_response(response, blocking=True)
            print("   ✅ Audio joué avec succès")
        except Exception as e:
            print(f"   ⚠️  Erreur lecture audio: {e}")
    elif CONFIG["enable_tts"]:
        print("   ⚠️  Pas d'audio généré")
    
    # Update conversation history
    conversation_history.append({"role": "user", "text": text})
    conversation_history.append({"role": "assistant", "text": response.response_text})
    
    # Calculate timing
    total_time = time.time() - start_time
    
    # =========================================================================
    # STEP 4.5: LOGGER LA RÉPONSE DANS PostgreSQL
    # =========================================================================
    if interaction_id:
        try:
            # Logger le message bot
            db_service.add_conversation_message(
                interaction_id=interaction_id,
                speaker="bot",
                message_text=response.response_text,
                turn_number=turn_number,
                detected_intent=intent,
                detected_emotion=None,
                confidence=response.confidence,
                metadata={
                    "action": response.action,
                    "documents_count": len(response.documents_used),
                    "response_time_ms": int(total_time * 1000)
                }
            )
            
            # Logger l'action CRM/RAG
            db_service.log_crm_action(
                interaction_id=interaction_id,
                customer_id=f"CUST-{session_id.split('_')[-1]}" if session_id else "CUST-UNKNOWN",
                action_type=response.action,
                input_data={"query": text, "intent": intent},
                output_data={
                    "response": response.response_text[:500],
                    "documents_used": response.documents_used
                },
                success=True,
                execution_time_ms=int(total_time * 1000)
            )
        except Exception as db_error:
            print(f"   ⚠️  Erreur logging réponse: {db_error}")
    
    # Determine if conversation should continue 
    should_continue = response.next_step != "end_call" and response.action != "human_handoff"
    
    # Force arrêt si goodbye a été dit
    if conversation_state["has_said_goodbye"] or should_say_goodbye:
        should_continue = False
        print("   🛑 Conversation forcée à s'arrêter (goodbye détecté)")
        
        # Si c'est un goodbye avec feedback, capturer la réponse
        if response.action == "end_call_with_feedback":
            print("\n🎤 En attente de votre réponse à la question de satisfaction...")
            print("⏰ Vous avez 20 secondes pour répondre...")
            try:
                # Utiliser inputs_service passé en paramètre ou le récupérer
                if inputs_service is None:
                    print("🔧 Initialisation des services d'entrée...")
                    inputs_service = get_inputs_service()
                
                # Capturer l'audio de réponse avec timeout plus long
                import threading
                import time as time_module
                
                feedback_result = None
                capture_successful = False
                capture_error = None
                
                # Fonction pour capturer l'audio avec timeout
                def capture_feedback():
                    nonlocal feedback_result, capture_successful, capture_error
                    try:
                        print("🎙️  Début de l'écoute pour feedback...")
                        feedback_result = inputs_service.process_audio_input()
                        capture_successful = True
                        print("✅ Audio capturé avec succès")
                    except Exception as e:
                        capture_error = str(e)
                        print(f"❌ Erreur capture: {e}")
                
                # Lancer la capture en thread
                capture_thread = threading.Thread(target=capture_feedback, daemon=True)
                capture_thread.start()
                
                # Attendre avec timeout de 20 secondes
                timeout_seconds = 20
                start_wait = time_module.time()
                
                while not capture_successful and (time_module.time() - start_wait) < timeout_seconds:
                    remaining = timeout_seconds - int(time_module.time() - start_wait)
                    if remaining > 0:
                        print(f"⏰ Temps restant: {remaining}s", end="\r")
                    time_module.sleep(1)
                
                print()  # Nouvelle ligne après le compteur
                
                if capture_error:
                    print(f"❌ Erreur technique: {capture_error}")
                
                if feedback_result:
                    print(f"📊 Résultat feedback: {feedback_result}")
                    print(f"🔍 Type: {type(feedback_result)}")
                    print(f"🔍 Clés disponibles: {list(feedback_result.keys()) if isinstance(feedback_result, dict) else 'N/A'}")
                    
                    # Vérifier les différentes clés possibles
                    feedback_text = ""
                    if 'full_text' in feedback_result:  # 🔧 CORRECTION: clé principale
                        feedback_text = feedback_result['full_text']
                        print(f"🎯 Texte trouvé via 'full_text': {feedback_text}")
                    elif 'transcription' in feedback_result:
                        feedback_text = feedback_result['transcription']
                        print(f"🎯 Texte trouvé via 'transcription': {feedback_text}")
                    elif 'text' in feedback_result:
                        feedback_text = feedback_result['text']
                        print(f"🎯 Texte trouvé via 'text': {feedback_text}")
                    else:
                        print("❌ Aucune clé de texte trouvée dans le résultat")
                    
                    if feedback_text:
                        feedback_text = feedback_text.strip().lower()
                        print(f"🗣️  Réponse feedback: '{feedback_text}'")
                        
                        # Analyser la réponse pour déterminer satisfaction
                        satisfaction_score = None
                        if any(word in feedback_text for word in ['oui', 'satisfait', 'content', 'bien', 'parfait', 'excellent', 'très bien', 'top', 'super']):
                            satisfaction_score = 1
                            confirmation = "Merci pour votre retour positif !"
                        elif any(word in feedback_text for word in ['non', 'insatisfait', 'mécontent', 'pas bien', 'mal', 'mauvais', 'nul', 'décevant']):
                            satisfaction_score = 2
                            confirmation = "Merci pour votre retour. Nous allons améliorer notre service."
                        else:
                            # Pas de mot clé clair - pas d'enregistrement
                            confirmation = "Merci pour votre appel."
                            print(f"⚠️ Réponse ambiguë: '{feedback_text}' - pas d'enregistrement")
                        
                        # Enregistrer le feedback SEULEMENT si on a une réponse claire
                        if satisfaction_score and interaction_id:
                            try:
                                print(f"💾 Tentative d'enregistrement: interaction_id={interaction_id}, score={satisfaction_score}")
                                success = db_service.update_satisfaction_score(
                                    interaction_id=interaction_id,
                                    satisfaction_score=satisfaction_score,
                                    feedback_metadata={
                                        "method": "integrated_audio",
                                        "raw_response": feedback_text,
                                        "session_id": session_id,
                                        "collected_at": time.strftime("%Y-%m-%d %H:%M:%S")
                                    }
                                )
                                if success:
                                    score_label = "✅ SATISFAIT" if satisfaction_score == 1 else "❌ INSATISFAIT"
                                    print(f"💾 {score_label} - Feedback enregistré avec succès dans la DB")
                                else:
                                    print("❌ Échec de l'enregistrement en base de données")
                            except Exception as e:
                                print(f"❌ ERREUR enregistrement feedback: {e}")
                                import traceback
                                traceback.print_exc()
                        
                        # Jouer la confirmation finale ET le "Merci"
                        final_message = confirmation + " Merci."
                        
                        if CONFIG["enable_tts"]:
                            try:
                                print(f"🔊 Génération TTS pour: '{final_message}'")
                                final_response = orchestrator.tts.generate_speech(
                                    text=final_message,
                                    emotion="neutral"
                                )
                                if final_response.get("audio_base64"):
                                    final_audio = type('Response', (), {
                                        'audio_base64': final_response["audio_base64"]
                                    })()
                                    play_audio_response(final_audio, blocking=True)
                                    print("🔊 Message final joué avec succès")
                                else:
                                    print("⚠️ Pas d'audio généré")
                            except Exception as e:
                                print(f"❌ Erreur TTS final: {e}")
                        
                        print(f"\n💬 {final_message}")
                    else:
                        print("⚠️ Pas de texte trouvé dans la réponse audio")
                        print(f"📊 Structure complète: {feedback_result}")
                else:
                    print("⚠️ Pas de réponse audio détectée pour le feedback")
                    # Message par défaut si pas de réponse
                    default_msg = "Merci pour votre appel."
                    print(f"\n💬 {default_msg}")
                    
                    if CONFIG["enable_tts"]:
                        try:
                            default_response = orchestrator.tts.generate_speech(
                                text=default_msg,
                                emotion="neutral"
                            )
                            if default_response.get("audio_base64"):
                                default_audio = type('Response', (), {
                                    'audio_base64': default_response["audio_base64"]
                                })()
                                play_audio_response(default_audio, blocking=True)
                                print("🔊 Message par défaut joué")
                        except Exception as e:
                            print(f"⚠️ Erreur TTS défaut: {e}")
                    
            except Exception as e:
                print(f"❌ ERREUR CRITIQUE feedback audio: {e}")
                import traceback
                traceback.print_exc()
    
    # =========================================================================
    # STEP 5: GESTION DU HANDOFF (si nécessaire)
    # =========================================================================
    if response.action == "human_handoff":
        print_section("TRANSFERT VERS AGENT HUMAIN", "👤")
        print(f"   Raison: {response.metadata.get('handoff_reason', 'Demande complexe')}")
        should_continue = False
        
        # Créer le ticket de handoff dans PostgreSQL
        if interaction_id:
            try:
                ticket_id = db_service.create_handoff_ticket(
                    interaction_id=interaction_id,
                    customer_id=f"CUST-{session_id.split('_')[-1]}" if session_id else "CUST-UNKNOWN",
                    queue_type="urgent" if urgency == "high" else "standard",
                    department="assurance",
                    estimated_wait_time_seconds=180 if urgency == "high" else 300,
                    context_summary=response.metadata.get('handoff_reason', 'Demande complexe'),
                    key_information={
                        "intent": intent,
                        "urgency": urgency,
                        "emotion": emotion_label,
                        "last_message": text[:200],
                        "conversation_turns": turn_number
                    },
                    skills_required=["assurance", "expertise_sinistre"] if "sinistre" in intent else ["assurance"]
                )
                print(f"   ✅ Ticket créé: {ticket_id}")
                
                # Mettre à jour le statut de l'interaction
                db_service.update_interaction_status(
                    interaction_id=interaction_id,
                    status="transferred"
                )
            except Exception as db_error:
                print(f"   ⚠️  Erreur création ticket: {db_error}")
    
    return {
        "response_text": response.response_text,
        "audio_base64": response.audio_base64,
        "action": response.action,
        "confidence": response.confidence,
        "should_continue": should_continue,
        "turn_time_seconds": total_time,
        "documents_used": response.documents_used,
        "metadata": response.metadata,
        "interaction_id": interaction_id  # Retourner pour réutilisation
    }


def run_conversation():
    """
    Run a full conversation loop.
    
    Continues until:
    - User says goodbye
    - Max turns reached
    - Human handoff required
    - Error occurs
    """
    # Réinitialiser l'état de conversation au début
    conversation_state["has_said_goodbye"] = False
    conversation_state["goodbye_count"] = 0
    
    print_banner()
    
    # Initialize orchestrator once (reused for all turns)
    print("🔧 Initialisation du système...")
    orchestrator = get_orchestrator(
        enable_tts=CONFIG["enable_tts"],
        enable_llm=CONFIG["enable_llm"]
    )
    
    # 🆕 Pré-initialiser les services d'entrée (modèles lourds)
    print("🔧 Initialisation des services audio...")
    inputs_service = get_inputs_service()  # Charge Whisper + BERT une seule fois
    
    # 🆕 Créer un session_id unique
    session_id = f"call_{int(time.time())}"
    interaction_id = None  # Sera créé au premier tour
    
    # Conversation state
    conversation_history = []
    turn_number = 0
    total_start_time = time.time()
    
    print("\n" + "="*70)
    print("✅ SYSTÈME PRÊT - CONVERSATION DÉMARRÉE")
    print(f"   Session ID: {session_id}")
    print("="*70)
    
    # Main conversation loop
    while turn_number < CONFIG["max_conversation_turns"]:
        turn_number += 1
        
        try:
            result = process_single_turn(
                orchestrator=orchestrator,
                conversation_history=conversation_history,
                turn_number=turn_number,
                session_id=session_id,
                interaction_id=interaction_id,
                inputs_service=inputs_service
            )
            
            # 🆕 Récupérer l'interaction_id pour les tours suivants
            if not interaction_id:
                interaction_id = result.get("interaction_id")
            
            # Check if we should continue
            if not result.get("should_continue", True):
                # 🆕 Finaliser l'interaction dans PostgreSQL
                if interaction_id and result.get("action") != "human_handoff":
                    try:
                        db_service.update_interaction_status(
                            interaction_id=interaction_id,
                            status="completed"
                        )
                        print(f"   ✅ Interaction finalisée: {interaction_id}")
                    except Exception as db_error:
                        print(f"   ⚠️  Erreur finalisation: {db_error}")
                break
            
            # Check for errors
            if "error" in result:
                print(f"\n❌ Erreur: {result['error']}")
                if interaction_id:
                    db_service.update_interaction_status(interaction_id, "failed")
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Conversation interrompue par l'utilisateur")
            if interaction_id:
                db_service.update_interaction_status(interaction_id, "cancelled")
            break
        except Exception as e:
            print(f"\n❌ Erreur inattendue: {e}")
            if interaction_id:
                db_service.update_interaction_status(interaction_id, "failed")
            import traceback
            traceback.print_exc()
            break
    
    # End conversation
    total_time = time.time() - total_start_time
    
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DE LA CONVERSATION")
    print("="*70)
    print(f"   Session ID: {session_id}")
    print(f"   Interaction ID: {interaction_id}")
    print(f"   Tours de parole: {turn_number}")
    print(f"   Durée totale: {total_time:.1f}s")
    print(f"   Messages échangés: {len(conversation_history)}")
    print("="*70)
    print("👋 FIN DE L'APPEL - Merci d'avoir utilisé Callbot Julie!")
    print("="*70 + "\n")
    
    return conversation_history


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    try:
        conversation = run_conversation()
    except KeyboardInterrupt:
        print("\n\n👋 Programme interrompu")
    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()