"""
Main entry point for the Callbot system
Demonstrates the complete flow
"""

import sys


sys.path.insert(0, r'C:\Users\PC\projects\callbot\final\tool_router')
import os
from dotenv import load_dotenv
from src.teams.response_builder import response_builder, generate_response
from src.routers.tools_router import tools_router
from src.schemas import IntentData, UrgencyLevel, EmotionType, IntentType

# Load environment variables
load_dotenv()


def main():
    """Main demonstration function"""
    
    print("=" * 60)
    print("🤖 CALLBOT JULIE - CNP ASSURANCES")
    print("=" * 60)
    print()
    
    # ===== TEST CASE 1: High urgency claim (Human Handoff) =====
    print("📞 CAS 1: Sinistre urgent - Escalade humaine")
    print("-" * 60)
    
    test_case_1 = {
        "intent": "declare_claim",
        "urgency": "high",
        "emotion": "stressed",
        "confidence": 0.91,
        "text": "J'ai eu un grave accident domestique, j'ai besoin d'aide immédiatement",
        "customer_id": "C12345"
    }
    
    response_1 = generate_response(
        intent=test_case_1["intent"],
        urgency=test_case_1["urgency"],
        emotion=test_case_1["emotion"],
        confidence=test_case_1["confidence"],
        text=test_case_1["text"],
        customer_id=test_case_1["customer_id"]
    )
    
    print(f"Réponse: {response_1}")
    print()
    
    # ===== TEST CASE 2: Simple info request (Automated) =====
    print("📞 CAS 2: Demande d'information simple")
    print("-" * 60)
    
    test_case_2 = {
        "intent": "general_info",
        "urgency": "low",
        "emotion": "neutral",
        "confidence": 0.95,
        "text": "Quels sont vos horaires d'ouverture ?",
        "documents": [
            {
                "title": "Horaires CNP Assurances",
                "content": "Nos conseillers sont disponibles du lundi au vendredi de 9h à 18h. Email disponible 24h/24."
            }
        ]
    }
    
    response_2 = generate_response(
        intent=test_case_2["intent"],
        urgency=test_case_2["urgency"],
        emotion=test_case_2["emotion"],
        confidence=test_case_2["confidence"],
        text=test_case_2["text"],
        documents=test_case_2["documents"]
    )
    
    print(f"Réponse: {response_2}")
    print()
    
    # ===== TEST CASE 3: CRM operation =====
    print("📞 CAS 3: Mise à jour d'information - CRM")
    print("-" * 60)
    
    test_case_3 = {
        "intent": "update_info",
        "urgency": "medium",
        "emotion": "neutral",
        "confidence": 0.88,
        "text": "Je veux mettre à jour mon adresse",
        "customer_id": "C12345"
    }
    
    response_3 = generate_response(
        intent=test_case_3["intent"],
        urgency=test_case_3["urgency"],
        emotion=test_case_3["emotion"],
        confidence=test_case_3["confidence"],
        text=test_case_3["text"],
        customer_id=test_case_3["customer_id"]
    )
    
    print(f"Réponse: {response_3}")
    print()
    
    # ===== TEST CASE 4: Angry customer (Empathetic + Handoff) =====
    print("📞 CAS 4: Client mécontent - Ton empathique")
    print("-" * 60)
    
    test_case_4 = {
        "intent": "complaint",
        "urgency": "high",
        "emotion": "angry",
        "confidence": 0.93,
        "text": "C'est inadmissible ! Ma réclamation n'a toujours pas été traitée !",
        "customer_id": "C67890"
    }
    
    response_4 = generate_response(
        intent=test_case_4["intent"],
        urgency=test_case_4["urgency"],
        emotion=test_case_4["emotion"],
        confidence=test_case_4["confidence"],
        text=test_case_4["text"],
        customer_id=test_case_4["customer_id"]
    )
    
    print(f"Réponse: {response_4}")
    print()
    
    print("=" * 60)
    print("✅ Tests terminés")
    print("=" * 60)


if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  ATTENTION: Variable OPENAI_API_KEY non définie")
        print("Créez un fichier .env avec votre clé API OpenAI")
        print()
    
    main()
