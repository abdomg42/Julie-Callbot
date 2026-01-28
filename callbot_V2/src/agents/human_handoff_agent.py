"""
Human Handoff Agent - Handles escalation to human agents
"""
from agno.agent import Agent
from agno.tools import tool
from typing import Dict, Optional, List
import os
from datetime import datetime
import uuid
import time
from src.database.db_service import db_service


# ===== HUMAN HANDOFF TOOLS =====

@tool
def create_escalation_ticket(
    customer_id: Optional[str],
    intent: str,
    urgency: str,
    emotion: str,
    context: str,
    reason: str,
    interaction_id: Optional[str] = None
) -> Dict:
    """
    Create an escalation ticket for human agent intervention
    
    Args:
        customer_id: Customer's unique identifier (if available)
        intent: The customer's intent (declare_claim, complaint, etc.)
        urgency: Urgency level (low, medium, high)
        emotion: Customer's emotional state
        context: Summary of the conversation so far
        reason: Reason for escalation
        interaction_id: ID de l'interaction (pour linking en BDD)
    
    Returns:
        Dictionary with ticket information
    """
    start_time = time.time()
    
    try:
        ticket_id = f"TICKET-{uuid.uuid4().hex[:8].upper()}"
        priority = _calculate_priority(urgency, emotion)
        
        ticket_data = {
            "ticket_id": ticket_id,
            "customer_id": customer_id or "UNKNOWN",
            "intent": intent,
            "urgency": urgency,
            "emotion": emotion,
            "context": context,
            "reason": reason,
            "created_at": datetime.now().isoformat(),
            "status": "queued",
            "priority": priority
        }
        
        # Enregistrer dans la BDD unifiée
        if interaction_id:
            try:
                db_service.create_handoff_ticket(
                    interaction_id=interaction_id,
                    customer_id=customer_id,
                    reason=reason,
                    priority=urgency,
                    queue_name="general",
                    context_data={
                        "intent": intent,
                        "emotion": emotion,
                        "context": context,
                        "calculated_priority": priority
                    }
                )
                
                # Mettre à jour statut interaction
                db_service.update_interaction_status(
                    interaction_id, "in_progress", "human_handoff_agent"
                )
            except Exception as db_error:
                print(f"Erreur logging BDD: {db_error}")
        
        # In production: Send to queue system (RabbitMQ, Redis, etc.)
        # queue_client.publish(ticket_data)
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "status": "queued",
            "message": f"Ticket d'escalade créé: {ticket_id}",
            "data": ticket_data
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Erreur lors de la création du ticket: {str(e)}",
            "data": {}
        }


@tool
def estimate_wait_time(urgency: str, current_queue_size: Optional[int] = None) -> Dict:
    """
    Estimate wait time for human agent availability
    
    Args:
        urgency: Urgency level of the request
        current_queue_size: Current number of tickets in queue
    
    Returns:
        Dictionary with estimated wait time
    """
    # Mock queue size if not provided
    queue_size = current_queue_size or 5
    
    # Calculate based on urgency
    if urgency == "high":
        base_time = 120  # 2 minutes for urgent
    elif urgency == "medium":
        base_time = 300  # 5 minutes
    else:
        base_time = 600  # 10 minutes
    
    estimated_seconds = base_time + (queue_size * 30)
    estimated_minutes = estimated_seconds // 60
    
    return {
        "estimated_wait_seconds": estimated_seconds,
        "estimated_wait_minutes": estimated_minutes,
        "queue_position": queue_size + 1,
        "message": f"Temps d'attente estimé: {estimated_minutes} minute(s)"
    }


@tool
def transfer_to_agent(ticket_id: str, department: Optional[str] = "sinistres", interaction_id: Optional[str] = None) -> Dict:
    """
    Transfer the call to a human agent in specific department
    
    Args:
        ticket_id: The escalation ticket ID
        department: Target department (sinistres, service_client, etc.)
        interaction_id: ID de l'interaction (pour update en BDD)
    
    Returns:
        Dictionary with transfer status
    """
    try:
        # Mock agent assignment
        agents = {
            "sinistres": ["Marie Dubois", "Pierre Martin", "Sophie Laurent"],
            "service_client": ["Jean Lefebvre", "Claire Moreau"],
            "commercial": ["Thomas Bernard"]
        }
        
        import random
        assigned_agent = random.choice(agents.get(department, agents["service_client"]))
        
        # Assigner le ticket dans la BDD
        if interaction_id:
            try:
                # Obtenir le ticket_id de la BDD via interaction_id
                # Pour l'instant, on utilise le ticket_id passé
                db_service.assign_ticket_to_agent(
                    ticket_id=ticket_id,
                    agent_id=assigned_agent,
                    queue_name=department
                )
            except Exception as db_error:
                print(f"Erreur assignment BDD: {db_error}")
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "department": department,
            "agent_assigned": assigned_agent,
            "status": "transferred",
            "message": f"Transfert vers {assigned_agent} - Département {department}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Erreur lors du transfert: {str(e)}",
            "data": {}
        }


@tool
def log_escalation_reason(ticket_id: str, reason: str, metadata: Dict) -> Dict:
    """
    Log the reason for escalation for analytics
    
    Args:
        ticket_id: The escalation ticket ID
        reason: Reason for escalation
        metadata: Additional context data
    
    Returns:
        Dictionary confirming logging
    """
    try:
        log_entry = {
            "ticket_id": ticket_id,
            "reason": reason,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        
        # In production: Send to analytics/logging system
        # analytics_client.log(log_entry)
        
        return {
            "success": True,
            "message": "Raison d'escalade enregistrée",
            "data": log_entry
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Erreur lors de l'enregistrement: {str(e)}"
        }


def _calculate_priority(urgency: str, emotion: str) -> str:
    """Helper function to calculate priority level"""
    if urgency == "high" or emotion in ["angry", "frustrated"]:
        return "urgent"
    elif urgency == "medium":
        return "high"
    else:
        return "normal"


# ===== HUMAN HANDOFF AGENT =====

human_handoff_agent = Agent(
    name="Human Handoff Agent",
    role="Agent d'escalade vers les conseillers humains",
    model="openai:gpt-4o-mini",
    tools=[
        create_escalation_ticket,
        estimate_wait_time,
        transfer_to_agent,
        log_escalation_reason
    ],
    instructions=[
        "Tu es un agent spécialisé dans l'escalade vers les conseillers humains chez CNP Assurances.",
        "Ton rôle est de créer des tickets d'escalade et de transférer les appels complexes ou urgents.",
        "Priorise les cas selon l'urgence et l'émotion du client.",
        "Informe toujours le client du temps d'attente estimé.",
        "Rassure le client en lui expliquant qu'un conseiller va le prendre en charge.",
        "Enregistre toujours la raison de l'escalade pour améliorer le système.",
        "Pour les émotions négatives (stressed, angry), priorise l'escalade."
    ],
    markdown=True,
    debug_mode=False
)
