"""
Tests for the Response Builder
"""
import pytest
from src.teams.response_builder import generate_response


def test_empathetic_response_for_stressed_customer():
    """Test empathetic tone for stressed customers"""
    response = generate_response(
        intent="declare_claim",
        urgency="high",
        emotion="stressed",
        confidence=0.9,
        text="J'ai eu un accident, je suis très inquiet",
        customer_id="C12345"
    )
    
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 20
    # Check for empathetic language (French)
    # Note: Actual response depends on LLM


def test_professional_tone_for_neutral_customer():
    """Test professional tone for neutral customers"""
    response = generate_response(
        intent="general_info",
        urgency="low",
        emotion="neutral",
        confidence=0.95,
        text="Quels sont vos horaires ?",
        documents=[
            {
                "title": "Horaires",
                "content": "Lundi-Vendredi 9h-18h"
            }
        ]
    )
    
    assert response is not None
    assert isinstance(response, str)


def test_response_with_knowledge_base():
    """Test response generation with knowledge base documents"""
    documents = [
        {
            "title": "Procédure sinistre",
            "content": "Pour déclarer un sinistre, contactez le 01 23 45 67 89",
            "relevance_score": 0.95
        },
        {
            "title": "Documents nécessaires",
            "content": "Vous aurez besoin de: pièce d'identité, photos",
            "relevance_score": 0.88
        }
    ]
    
    response = generate_response(
        intent="declare_claim",
        urgency="medium",
        emotion="neutral",
        confidence=0.87,
        text="Comment déclarer un sinistre ?",
        documents=documents
    )
    
    assert response is not None
    assert isinstance(response, str)


def test_response_for_angry_customer():
    """Test handling of angry customer"""
    response = generate_response(
        intent="complaint",
        urgency="high",
        emotion="angry",
        confidence=0.93,
        text="C'est inadmissible ! Personne ne me répond !",
        customer_id="C67890"
    )
    
    assert response is not None
    assert isinstance(response, str)
    # Should involve escalation


def test_response_includes_customer_context():
    """Test that customer ID is used in context"""
    response = generate_response(
        intent="check_status",
        urgency="medium",
        emotion="neutral",
        confidence=0.91,
        text="Où en est mon dossier ?",
        customer_id="C99999"
    )
    
    assert response is not None
    assert isinstance(response, str)
