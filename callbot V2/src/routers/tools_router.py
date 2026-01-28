"""
Tools Router - Routes requests to CRM or Human Handoff agents
Pattern: Router (respond_directly=True)
"""
from agno.team import Team
from src.agents.crm_agent import crm_agent
from src.agents.human_handoff_agent import human_handoff_agent
from src.database.db_service import db_service
from typing import Dict, Optional
from datetime import datetime
import uuid


# ===== TOOLS ROUTER TEAM =====

tools_router = Team(
    name="Tools Router",
    role="Router intelligent vers CRM ou escalade humaine",
    members=[crm_agent, human_handoff_agent],
    respond_directly=True,  # Pattern Router - pas de synthèse
    determine_input_for_members=False,
    instructions=[
        "Tu es un routeur intelligent qui décide quelle action prendre.",
        "",
        "RÈGLES DE ROUTAGE:",
        "",
        "1. ESCALADE HUMAINE (Human Handoff Agent) si:",
        "   - Urgence = HIGH",
        "   - Intent = declare_claim, complaint, cancel_policy",
        "   - Émotion = angry, frustrated, stressed (et cas complexe)",
        "   - Confiance < 0.7",
        "",
        "2. OPÉRATIONS CRM (CRM Agent) si:",
        "   - Intent = update_info, check_status, payment_info",
        "   - Urgence = LOW ou MEDIUM",
        "   - Demandes de mise à jour de données",
        "",
        "3. RÈGLES SPÉCIALES:",
        "   - Sinistre urgent → TOUJOURS escalade humaine",
        "   - Client en colère + cas complexe → escalade humaine",
        "   - Simple consultation de données → CRM",
        "",
        "Délègue DIRECTEMENT à l'agent approprié sans reformuler la demande."
    ],
    markdown=True,
    debug_mode=False
)


def route_request(
    intent: str, 
    urgency: str, 
    emotion: str, 
    confidence: float, 
    text: str,
    customer_id: Optional[str] = None,
    channel: str = "phone"
) -> Dict:
    """
    Helper function to route requests programmatically
    
    Args:
        intent: Customer intent
        urgency: Urgency level
        emotion: Customer emotion
        confidence: Intent confidence score
        text: Customer's original text
        customer_id: Optional customer identifier
        channel: Communication channel (phone, chat, email)
    
    Returns:
        Dict with response and interaction_id
    """
    # 1. Créer l'interaction dans la BDD unifiée
    interaction_id = None
    try:
        # Générer un session_id unique
        session_id = f"SESSION-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        interaction_id = db_service.create_interaction(
            customer_id=customer_id or "UNKNOWN",
            session_id=session_id,
            intent=intent,
            urgency=urgency,
            emotion=emotion,
            confidence=confidence,
            action_taken="routing",
            priority="high" if urgency == "high" else "normal",
            reason=f"Customer request: {text[:100]}"
        )
        
        # 2. Logger le message initial du client
        db_service.add_conversation_message(
            interaction_id=interaction_id,
            speaker="customer",
            message_text=text,
            turn_number=1,
            detected_intent=intent,
            detected_emotion=emotion,
            confidence=confidence
        )
    except Exception as db_error:
        print(f"Erreur création interaction BDD: {db_error}")
    
    # 3. Build context for the router
    context = f"""
    Intent: {intent}
    Urgence: {urgency}
    Émotion: {emotion}
    Confiance: {confidence}
    Demande client: "{text}"
    Interaction ID: {interaction_id}
    """
    
    # 4. Let the Tools Router decide and execute
    response = tools_router.print_response(context, stream=False)
    
    # 5. Logger la réponse de l'agent
    if interaction_id:
        try:
            db_service.add_conversation_message(
                interaction_id=interaction_id,
                speaker="agent",
                message_text=str(response),
                turn_number=2
            )
        except Exception as db_error:
            print(f"Erreur logging réponse BDD: {db_error}")
    
    return {
        "response": response,
        "interaction_id": interaction_id
    }
