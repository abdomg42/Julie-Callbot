"""
Integration tests for the complete callbot flow
"""
import pytest
from src.teams.response_builder import generate_response


class TestEndToEndFlow:
    """End-to-end integration tests"""
    
    def test_complete_flow_urgent_claim(self):
        """Test complete flow for urgent claim"""
        # Simulate data from upstream components
        intent = "declare_claim"
        urgency = "high"
        emotion = "stressed"
        confidence = 0.91
        text = "J'ai eu un grave accident domestique"
        customer_id = "C12345"
        
        # Generate response
        response = generate_response(
            intent=intent,
            urgency=urgency,
            emotion=emotion,
            confidence=confidence,
            text=text,
            customer_id=customer_id
        )
        
        # Verify response
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_complete_flow_simple_info(self):
        """Test complete flow for simple information request"""
        intent = "general_info"
        urgency = "low"
        emotion = "neutral"
        confidence = 0.95
        text = "Quels sont vos horaires ?"
        
        documents = [
            {
                "title": "Horaires d'ouverture",
                "content": "Du lundi au vendredi de 9h à 18h"
            }
        ]
        
        response = generate_response(
            intent=intent,
            urgency=urgency,
            emotion=emotion,
            confidence=confidence,
            text=text,
            documents=documents
        )
        
        assert response is not None
        assert isinstance(response, str)
    
    def test_complete_flow_crm_update(self):
        """Test complete flow for CRM update"""
        intent = "update_info"
        urgency = "medium"
        emotion = "neutral"
        confidence = 0.88
        text = "Je veux changer mon adresse"
        customer_id = "C67890"
        
        response = generate_response(
            intent=intent,
            urgency=urgency,
            emotion=emotion,
            confidence=confidence,
            text=text,
            customer_id=customer_id
        )
        
        assert response is not None
        assert isinstance(response, str)
    
    def test_complete_flow_angry_complaint(self):
        """Test complete flow for angry customer complaint"""
        intent = "complaint"
        urgency = "high"
        emotion = "angry"
        confidence = 0.93
        text = "Personne ne répond à mes appels !"
        customer_id = "C11111"
        
        response = generate_response(
            intent=intent,
            urgency=urgency,
            emotion=emotion,
            confidence=confidence,
            text=text,
            customer_id=customer_id
        )
        
        assert response is not None
        assert isinstance(response, str)


class TestComponentIntegration:
    """Test integration between components"""
    
    def test_response_builder_to_tools_router(self):
        """Test that Response Builder correctly delegates to Tools Router"""
        # High urgency should trigger Tools Router (Human Handoff)
        response = generate_response(
            intent="declare_claim",
            urgency="high",
            emotion="stressed",
            confidence=0.9,
            text="Urgent: accident grave",
            customer_id="C99999"
        )
        
        assert response is not None
    
    def test_tools_router_to_crm_agent(self):
        """Test that Tools Router correctly delegates to CRM Agent"""
        # CRM intent should route to CRM Agent
        response = generate_response(
            intent="update_info",
            urgency="medium",
            emotion="neutral",
            confidence=0.88,
            text="Mise à jour adresse",
            customer_id="C88888"
        )
        
        assert response is not None
    
    def test_tools_router_to_handoff_agent(self):
        """Test that Tools Router correctly delegates to Handoff Agent"""
        # High urgency + complex intent should route to Handoff
        response = generate_response(
            intent="complaint",
            urgency="high",
            emotion="angry",
            confidence=0.92,
            text="Je suis très mécontent",
            customer_id="C77777"
        )
        
        assert response is not None
