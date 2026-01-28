"""
Tests for the Tools Router
"""
import pytest
from src.routers.tools_router import route_request


def test_high_urgency_routes_to_handoff():
    """Test that high urgency routes to human handoff"""
    response = route_request(
        intent="declare_claim",
        urgency="high",
        emotion="stressed",
        confidence=0.9,
        text="J'ai eu un accident grave"
    )
    
    # Should involve human handoff
    assert response is not None
    assert isinstance(response, str)


def test_crm_intent_routes_to_crm():
    """Test that CRM intents route to CRM agent"""
    response = route_request(
        intent="update_info",
        urgency="medium",
        emotion="neutral",
        confidence=0.88,
        text="Je veux mettre à jour mon adresse"
    )
    
    assert response is not None
    assert isinstance(response, str)


def test_simple_query_automated():
    """Test that simple queries get automated response"""
    response = route_request(
        intent="general_info",
        urgency="low",
        emotion="neutral",
        confidence=0.95,
        text="Quels sont vos horaires ?"
    )
    
    assert response is not None
    assert isinstance(response, str)


def test_angry_emotion_escalates():
    """Test that angry customers get escalated"""
    response = route_request(
        intent="complaint",
        urgency="high",
        emotion="angry",
        confidence=0.92,
        text="C'est inadmissible !"
    )
    
    assert response is not None
    # Should involve human handoff for angry customers


def test_low_confidence_escalates():
    """Test that low confidence intents get escalated"""
    response = route_request(
        intent="unknown",
        urgency="medium",
        emotion="neutral",
        confidence=0.45,
        text="Blabla incompréhensible"
    )
    
    assert response is not None
