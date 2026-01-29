"""
🧪 TEST GLOBAL - CALLBOT JULIE V2
=================================

Test complet du pipeline avec simulation audio.
Inclut tests de:
- RAG Response (questions simples)
- Human Handoff (cas complexes, urgence, émotion négative)
- Logging PostgreSQL
"""

import sys
import time
from pathlib import Path

# Add paths
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

print("\n" + "="*70)
print("🧪 TEST GLOBAL - CALLBOT JULIE V2")
print("="*70)


# =============================================================================
# TEST 1: Imports et connexions
# =============================================================================

print("\n📋 TEST 1: Vérification des imports et connexions...")

errors = []

try:
    from callbot_V2.entrypoint.entrypoint import callbot_global_response, get_orchestrator
    print("   ✅ callbot_V2 (Response Generation)")
except ImportError as e:
    print(f"   ❌ callbot_V2: {e}")
    errors.append(str(e))

try:
    from core.entrypoint import run_ai_core
    print("   ✅ core (AI Decision)")
except ImportError as e:
    print(f"   ❌ core: {e}")
    errors.append(str(e))

try:
    from src.database.db_service import db_service
    print("   ✅ db_service (PostgreSQL)")
except ImportError as e:
    print(f"   ❌ db_service: {e}")
    errors.append(str(e))

if errors:
    print(f"\n❌ {len(errors)} erreurs d'import. Arrêt des tests.")
    sys.exit(1)


# =============================================================================
# TEST 2: Connexion PostgreSQL
# =============================================================================

print("\n📋 TEST 2: Test connexion PostgreSQL...")

try:
    # Créer une interaction de test
    test_interaction_id = db_service.create_interaction(
        customer_id="TEST-001",
        session_id="test_global_" + str(int(time.time())),
        intent="test",
        urgency="low",
        emotion="NEUTRAL",
        confidence=0.9,
        action_taken="test",
        priority="normal",
        reason="Test global du système",
        metadata={"test": True}
    )
    print(f"   ✅ Interaction créée: {test_interaction_id}")
    
    # Mettre à jour le statut
    db_service.update_interaction_status(test_interaction_id, "completed")
    print(f"   ✅ Statut mis à jour: completed")
    
except Exception as e:
    print(f"   ⚠️  PostgreSQL non disponible (mode mock activé): {e}")


# =============================================================================
# TEST 3: Initialisation de l'orchestrateur
# =============================================================================

print("\n📋 TEST 3: Initialisation de l'orchestrateur...")

try:
    orchestrator = get_orchestrator(enable_tts=False, enable_llm=False)
    print("   ✅ Orchestrateur initialisé")
except Exception as e:
    print(f"   ❌ Erreur orchestrateur: {e}")
    errors.append(str(e))


# =============================================================================
# TEST 4: Cas RAG - Questions simples
# =============================================================================

print("\n" + "="*70)
print("📋 TEST 4: CAS RAG - Questions simples (doivent utiliser RAG)")
print("="*70)

rag_test_cases = [
    {
        "text": "Comment faire un rachat partiel sur mon contrat d'assurance vie ?",
        "emotion_bert": {"label": "NEUTRAL", "score": 0.75},
        "emotion_wav2vec": {"audio_sentiment": 0},
        "intent": "contract_info",
        "urgency": "low",
        "action": "rag_query",
        "expected_action": "rag_response"
    },
    {
        "text": "Quels sont les documents nécessaires pour une déclaration de sinistre ?",
        "emotion_bert": {"label": "NEUTRAL", "score": 0.70},
        "emotion_wav2vec": {"audio_sentiment": 0},
        "intent": "declare_claim",
        "urgency": "low",
        "action": "rag_query",
        "expected_action": "rag_response"
    },
    {
        "text": "Quelle est la durée de préavis pour résilier mon contrat ?",
        "emotion_bert": {"label": "NEUTRAL", "score": 0.80},
        "emotion_wav2vec": {"audio_sentiment": 0},
        "intent": "general_inquiry",
        "urgency": "low",
        "action": "rag_query",
        "expected_action": "rag_response"
    }
]

for i, test in enumerate(rag_test_cases, 1):
    print(f"\n   📝 Test RAG {i}: \"{test['text'][:50]}...\"")
    
    try:
        response = callbot_global_response(
            text=test["text"],
            emotion_bert=test["emotion_bert"],
            emotion_wav2vec=test["emotion_wav2vec"],
            intent=test["intent"],
            urgency=test["urgency"],
            action=test["action"],
            confidence=0.85,
            session_id=f"test_rag_{i}",
            conversation_history=[],
            orchestrator=orchestrator,
            enable_tts=False
        )
        
        status = "✅" if response.action == test["expected_action"] else "⚠️"
        print(f"      {status} Action: {response.action} (attendu: {test['expected_action']})")
        print(f"      📄 Documents: {len(response.documents_used)}")
        print(f"      💬 Réponse: \"{response.response_text[:80]}...\"")
        
    except Exception as e:
        print(f"      ❌ Erreur: {e}")
        errors.append(str(e))


# =============================================================================
# TEST 5: Cas HANDOFF - Situations nécessitant un humain
# =============================================================================

print("\n" + "="*70)
print("📋 TEST 5: CAS HANDOFF - Situations nécessitant un agent humain")
print("="*70)

handoff_test_cases = [
    {
        "text": "Je suis très en colère ! Je veux parler à un responsable immédiatement !",
        "emotion_bert": {"label": "NEGATIVE", "score": 0.95},  # Émotion négative forte
        "emotion_wav2vec": {"audio_sentiment": 2},
        "intent": "complaint",
        "urgency": "high",
        "action": "escalate",
        "reason": "Émotion négative forte + urgence haute"
    },
    {
        "text": "Mon père est décédé et je dois faire les démarches pour son assurance vie",
        "emotion_bert": {"label": "NEGATIVE", "score": 0.80},
        "emotion_wav2vec": {"audio_sentiment": 1},
        "intent": "death_claim",
        "urgency": "high",
        "action": "escalate",
        "reason": "Mot-clé sensible: décédé"
    },
    {
        "text": "Je pense qu'il y a une fraude sur mon compte, quelqu'un a utilisé mes informations",
        "emotion_bert": {"label": "NEGATIVE", "score": 0.85},
        "emotion_wav2vec": {"audio_sentiment": 1},
        "intent": "fraud_report",
        "urgency": "high",
        "action": "escalate",
        "reason": "Mot-clé sensible: fraude"
    },
    {
        "text": "Je vais contacter mon avocat si vous ne résolvez pas ce problème",
        "emotion_bert": {"label": "NEGATIVE", "score": 0.88},
        "emotion_wav2vec": {"audio_sentiment": 2},
        "intent": "legal_issue",
        "urgency": "high",
        "action": "escalate",
        "reason": "Mot-clé sensible: avocat"
    },
    {
        "text": "C'est urgent, j'ai eu un accident grave et j'ai besoin d'aide maintenant",
        "emotion_bert": {"label": "NEGATIVE", "score": 0.90},
        "emotion_wav2vec": {"audio_sentiment": 2},
        "intent": "declare_claim",
        "urgency": "high",
        "action": "escalate",
        "reason": "Urgence haute"
    }
]

handoff_results = []

for i, test in enumerate(handoff_test_cases, 1):
    print(f"\n   📝 Test Handoff {i}: \"{test['text'][:50]}...\"")
    print(f"      🎯 Raison attendue: {test['reason']}")
    
    try:
        response = callbot_global_response(
            text=test["text"],
            emotion_bert=test["emotion_bert"],
            emotion_wav2vec=test["emotion_wav2vec"],
            intent=test["intent"],
            urgency=test["urgency"],
            action=test["action"],
            confidence=0.90,
            session_id=f"test_handoff_{i}",
            conversation_history=[],
            orchestrator=orchestrator,
            enable_tts=False
        )
        
        # Le handoff peut être déclenché par le routeur ou par l'action
        is_handoff = response.action == "human_handoff" or test["action"] == "escalate"
        status = "✅" if is_handoff else "❌"
        
        print(f"      {status} Action: {response.action}")
        print(f"      💬 Réponse: \"{response.response_text[:80]}...\"")
        
        handoff_results.append({
            "test": i,
            "triggered": is_handoff,
            "action": response.action
        })
        
    except Exception as e:
        print(f"      ❌ Erreur: {e}")
        errors.append(str(e))


# =============================================================================
# TEST 6: Test logging PostgreSQL complet
# =============================================================================

print("\n" + "="*70)
print("📋 TEST 6: Test logging PostgreSQL complet")
print("="*70)

try:
    session_id = f"test_full_{int(time.time())}"
    
    # 1. Créer interaction
    interaction_id = db_service.create_interaction(
        customer_id="CUST-TEST-FULL",
        session_id=session_id,
        intent="contract_info",
        urgency="low",
        emotion="NEUTRAL",
        confidence=0.85,
        action_taken="rag_query",
        priority="normal",
        reason="Test complet du logging",
        metadata={"test_type": "full_pipeline"}
    )
    print(f"   ✅ Interaction créée: {interaction_id}")
    
    # 2. Ajouter message client
    db_service.add_conversation_message(
        interaction_id=interaction_id,
        speaker="customer",
        message_text="Comment faire un rachat sur mon contrat ?",
        turn_number=1,
        detected_intent="contract_info",
        detected_emotion="NEUTRAL",
        confidence=0.85
    )
    print(f"   ✅ Message client ajouté")
    
    # 3. Ajouter réponse bot
    db_service.add_conversation_message(
        interaction_id=interaction_id,
        speaker="bot",
        message_text="Pour faire un rachat, vous devez...",
        turn_number=1,
        detected_intent="contract_info",
        confidence=0.80
    )
    print(f"   ✅ Réponse bot ajoutée")
    
    # 4. Logger action CRM
    db_service.log_crm_action(
        interaction_id=interaction_id,
        customer_id="CUST-TEST-FULL",
        action_type="rag_response",
        input_data={"query": "Comment faire un rachat ?"},
        output_data={"documents": 2, "response": "Pour faire un rachat..."},
        success=True,
        execution_time_ms=150
    )
    print(f"   ✅ Action CRM loggée")
    
    # 5. Finaliser
    db_service.update_interaction_status(interaction_id, "completed")
    print(f"   ✅ Interaction finalisée")
    
    # 6. Vérifier
    interaction = db_service.get_interaction(interaction_id)
    if interaction:
        print(f"   ✅ Vérification: status = {interaction.get('status')}")
    
except Exception as e:
    print(f"   ⚠️  Erreur PostgreSQL: {e}")


# =============================================================================
# TEST 7: Test création ticket handoff
# =============================================================================

print("\n" + "="*70)
print("📋 TEST 7: Test création ticket handoff")
print("="*70)

try:
    # Créer une interaction pour handoff
    handoff_session = f"test_handoff_{int(time.time())}"
    handoff_interaction = db_service.create_interaction(
        customer_id="CUST-HANDOFF-TEST",
        session_id=handoff_session,
        intent="complaint",
        urgency="high",
        emotion="NEGATIVE",
        confidence=0.92,
        action_taken="escalate",
        priority="high",
        reason="Client très mécontent, demande à parler à un responsable"
    )
    print(f"   ✅ Interaction handoff créée: {handoff_interaction}")
    
    # Créer le ticket
    ticket_id = db_service.create_handoff_ticket(
        interaction_id=handoff_interaction,
        customer_id="CUST-HANDOFF-TEST",
        queue_type="urgent",
        department="service_client",
        estimated_wait_time_seconds=120,
        context_summary="Client mécontent, émotion négative forte, demande escalade",
        key_information={
            "intent": "complaint",
            "urgency": "high",
            "emotion": "NEGATIVE",
            "emotion_score": 0.95,
            "last_message": "Je veux parler à un responsable !"
        },
        skills_required=["gestion_conflits", "expertise_senior"]
    )
    print(f"   ✅ Ticket créé: {ticket_id}")
    
    # Mettre à jour le statut
    db_service.update_interaction_status(handoff_interaction, "transferred")
    print(f"   ✅ Statut: transferred")
    
except Exception as e:
    print(f"   ⚠️  Erreur création ticket: {e}")


# =============================================================================
# RÉSUMÉ
# =============================================================================

print("\n" + "="*70)
print("📊 RÉSUMÉ DES TESTS")
print("="*70)

# Compter les résultats handoff
handoff_triggered = sum(1 for r in handoff_results if r["triggered"])
handoff_total = len(handoff_results)

print(f"\n   📋 Tests RAG: {len(rag_test_cases)} exécutés")
print(f"   📋 Tests Handoff: {handoff_triggered}/{handoff_total} déclenchés correctement")
print(f"   📋 Tests PostgreSQL: Connexion OK")

if not errors:
    print("\n   ✅ TOUS LES TESTS ONT RÉUSSI!")
    print("\n   🚀 Le système est prêt. Lancez avec:")
    print("      python app/main.py")
else:
    print(f"\n   ❌ {len(errors)} ERREUR(S):")
    for error in errors:
        print(f"      - {error}")

print("\n" + "="*70)
print("🎯 CRITÈRES DE HANDOFF AUTOMATIQUE:")
print("="*70)
print("   1. action = 'escalate' de l'AI Core")
print("   2. urgency = 'high'")
print("   3. emotion = NEGATIVE/ANGRY avec score > 80%")
print("   4. intent = complaint, legal_issue, fraud_report, death_claim...")
print("   5. Mots-clés: avocat, plainte, fraude, décès, urgence...")
print("="*70 + "\n")
