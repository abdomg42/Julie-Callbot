"""Main entry point for the Callbot system."""

import sys
sys.path.insert(0, r'C:\Users\PC\projects\callbot\final\tool_router')
import os
from dotenv import load_dotenv
from src.teams.response_builder import response_builder, generate_response
from src.routers.tools_router import tools_router
from src.schemas import IntentData, UrgencyLevel, EmotionType, IntentType

load_dotenv()


def main():
    """Run test cases."""
    test_cases = [
        {"intent": "declare_claim", "urgency": "high", "emotion": "stressed", 
         "confidence": 0.91, "text": "J'ai eu un accident, j'ai besoin d'aide", "customer_id": "C12345"},
        {"intent": "general_info", "urgency": "low", "emotion": "neutral",
         "confidence": 0.95, "text": "Quels sont vos horaires ?"},
        {"intent": "update_info", "urgency": "medium", "emotion": "neutral",
         "confidence": 0.88, "text": "Je veux mettre à jour mon adresse", "customer_id": "C12345"},
        {"intent": "complaint", "urgency": "high", "emotion": "angry",
         "confidence": 0.93, "text": "Ma réclamation n'a pas été traitée !", "customer_id": "C67890"},
    ]
    
    for case in test_cases:
        response = generate_response(
            intent=case["intent"],
            urgency=case["urgency"],
            emotion=case["emotion"],
            confidence=case["confidence"],
            text=case["text"],
            customer_id=case.get("customer_id"),
            documents=case.get("documents", [])
        )
        print(f"{case['intent']}: {response[:80]}...")


if __name__ == "__main__":
    main()
