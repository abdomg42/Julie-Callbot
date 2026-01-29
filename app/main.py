"""
🎯 CALLBOT JULIE V2 - MAIN ENTRY POINT
======================================

Pipeline complet du callbot:
  📞 Caller → 🎤 Audio Input → 🗣️ STT → 🧠 AI Decision → 🎯 RAG Response → 🔊 TTS → 📞 Caller

Intègre les 3 parties:
  1. MG (Callbot_julie_inputs): Audio recording + STT + Emotion analysis
  2. RED (core): AI Decision making (intent, urgency, action)
  3. IBRAHIM (callbot_V2): RAG + Response generation + TTS

+ PostgreSQL logging de toutes les interactions
"""

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
from Callbot_julie_inputs.entrypoint.run import run_inputs
from callbot_V2.entrypoint.entrypoint import (
    callbot_global_response, 
    get_orchestrator, 
    play_audio_response
)

# 🆕 Import du service de base de données
from src.database.db_service import db_service


# =============================================================================
# CONFIGURATION
# =============================================================================

CONFIG = {
    "enable_tts": True,           # Enable text-to-speech
    "enable_llm": False,          # Use templates instead of LLM
    "auto_play_audio": True,      # Play audio response automatically
    "max_conversation_turns": 10, # Max turns before ending
    "silence_timeout_ms": 3000,   # Silence timeout in milliseconds
    "end_keywords": ["au revoir", "merci au revoir", "bye", "goodbye", "fin"],
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


def process_single_turn(
    orchestrator,
    conversation_history: list,
    turn_number: int = 1,
    session_id: str = None,
    interaction_id: str = None
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
    print("   Parlez maintenant...")
    
    try:
        inputs = run_inputs()
        text = inputs.get("full_text", "")
        emotion_bert = inputs.get("emotion_bert", {"label": "NEUTRAL", "score": 0.5})
        emotion_wav2vec = inputs.get("emotion_wav2vec", {"audio_sentiment": 0})
        audio_summary = inputs.get("audio_summary", {})
        
        print(f"   ✅ Texte: \"{text}\"")
        print(f"   ✅ Émotion BERT: {emotion_bert.get('label', 'N/A')}")
        print(f"   ✅ Durée audio: {audio_summary.get('duration_ms', 0)}ms")
        
    except Exception as e:
        print(f"   ❌ Erreur d'entrée audio: {e}")
        return {"error": str(e), "should_continue": False}
    
    # Check for empty input
    if not text or text.strip() == "":
        print("   ⚠️  Aucune parole détectée")
        return {
            "response_text": "Je n'ai pas entendu. Pouvez-vous répéter ?",
            "should_continue": True,
            "action": "repeat_request"
        }
    
    # Check for end keywords
    text_lower = text.lower().strip()
    for keyword in CONFIG["end_keywords"]:
        if keyword in text_lower:
            print(f"   👋 Mot de fin détecté: '{keyword}'")
            return {
                "response_text": "Merci pour votre appel. Au revoir et à bientôt !",
                "should_continue": False,
                "action": "end_call"
            }
    
    # =========================================================================
    # STEP 2: AI DECISION (RED - core)
    # =========================================================================
    print_section("ANALYSE IA", "🧠")
    
    try:
        # NOTE: Order is (full_text, emotion_bert, emotion_wav2vec, audio_summary)
        decision = run_ai_core(text, emotion_bert, emotion_wav2vec, audio_summary)
        
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
    
    # 1. Action de l'AI Core demande escalade
    if action == "escalate":
        should_handoff = True
        handoff_reason = "Escalade demandée par l'AI Core"
    
    # 2. Urgence élevée
    if urgency == "high":
        should_handoff = True
        handoff_reason = "Urgence élevée détectée"
    
    # 3. Émotion négative forte (client en détresse)
    emotion_score = emotion_bert.get("score", 0.5)
    emotion_label = emotion_bert.get("label", "NEUTRAL").upper()
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
        print(f"   ✅ TRAITEMENT RAG: Question standard")
    
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
    # STEP 3: RESPONSE GENERATION (IBRAHIM - callbot_V2)
    # =========================================================================
    print_section("GÉNÉRATION DE RÉPONSE", "🎯")
    
    response = callbot_global_response(
        text=text,
        emotion_bert=emotion_bert,
        emotion_wav2vec=emotion_wav2vec,
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
    
    # Play audio if enabled
    if CONFIG["auto_play_audio"] and response.audio_base64:
        print_section("LECTURE AUDIO", "🔊")
        try:
            play_audio_response(response)
            print("   ✅ Audio joué avec succès")
        except Exception as e:
            print(f"   ⚠️  Erreur lecture audio: {e}")
    
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
    print_banner()
    
    # Initialize orchestrator once (reused for all turns)
    print("🔧 Initialisation du système...")
    orchestrator = get_orchestrator(
        enable_tts=CONFIG["enable_tts"],
        enable_llm=CONFIG["enable_llm"]
    )
    
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
                interaction_id=interaction_id
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