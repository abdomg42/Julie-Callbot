"""
Response Builder - Main team for generating customer responses
Delegates to Tools Router when needed for CRM or human escalation
"""
from agno.team import Team
from src.routers.tools_router import tools_router
from tool_router.src.database.db_service import db_service
import os
import time
from typing import Optional, List, Dict


# ===== RESPONSE BUILDER TEAM =====

response_builder = Team(
    name="Response Builder",
    role="Agent principal de génération de réponses client",
    model="openai:gpt-4o-mini",
    members=[tools_router],
    instructions=[
        "Tu es Julie, l'assistante virtuelle de CNP Assurances.",
        "Tu aides les clients avec leurs questions sur les sinistres 'accidents de la vie'.",
        "",
        "RÈGLES DE GÉNÉRATION DE RÉPONSE:",
        "",
        "1. ADAPTATION ÉMOTIONNELLE:",
        "   - Si émotion = stressed, angry, frustrated:",
        "     • Commence par reconnaître l'émotion",
        "     • Utilise un ton empathique et rassurant",
        "     • Exemple: 'Je comprends votre préoccupation...'",
        "   - Si émotion = neutral, satisfied:",
        "     • Ton professionnel et courtois",
        "     • Direct et efficace",
        "",
        "2. LONGUEUR DES RÉPONSES:",
        "   - Maximum 3 phrases pour rester concis",
        "   - Vocal-friendly (sera converti en audio)",
        "   - Évite le jargon technique",
        "",
        "3. DÉLÉGATION:",
        "   - Si besoin d'action CRM ou escalade → Délègue au Tools Router",
        "   - Exemples: mise à jour données, création ticket escalade",
        "   - Ne tente PAS de faire l'action toi-même",
        "",
        "4. STRUCTURE TYPE:",
        "   - Empathie/Reconnaissance (si émotion négative)",
        "   - Réponse principale / Action",
        "   - Prochaine étape claire",
        "",
        "5. UTILISE LA KNOWLEDGE BASE:",
        "   - Réfère-toi aux documents fournis pour la précision",
        "   - Cite les procédures CNP Assurances",
        "",
        "EXEMPLES:",
        "",
        "Cas 1 - Client stressé avec sinistre urgent:",
        "\"Je comprends que c'est une situation difficile. Je vais immédiatement vous mettre en relation avec un conseiller spécialisé qui pourra traiter votre déclaration de sinistre. Vous serez pris en charge dans quelques instants.\"",
        "",
        "Cas 2 - Question simple sur horaires:",
        "\"Nos conseillers sont disponibles du lundi au vendredi de 9h à 18h. Vous pouvez également nous contacter par email 24h/24. Puis-je vous aider avec autre chose ?\"",
        "",
        "Cas 3 - Mise à jour d'adresse:",
        "\"Bien sûr, je peux mettre à jour votre adresse. [Délègue au Tools Router pour action CRM]. Votre nouvelle adresse a été enregistrée dans notre système.\""
    ],
    markdown=True,
    debug_mode=False
)


def generate_response(
    intent: str,
    urgency: str,
    emotion: str,
    confidence: float,
    text: str,
    documents: Optional[List[Dict]] = None,
    customer_id: Optional[str] = None,
    interaction_id: Optional[str] = None
) -> Dict:
    """
    Generate a response for the customer
    
    Args:
        intent: Customer intent
        urgency: Urgency level
        emotion: Customer emotion
        confidence: Intent confidence
        text: Customer's original request
        documents: Knowledge base documents (from Hatim's component)
        customer_id: Customer ID if available
        interaction_id: Interaction ID for logging
    
    Returns:
        Dict with generated response and metrics
    """
    start_time = time.time()
    
    # Build context with all information
    context_parts = [
        f"Intent détecté: {intent}",
        f"Urgence: {urgency}",
        f"Émotion du client: {emotion}",
        f"Confiance de détection: {confidence}",
        f"Demande du client: \"{text}\""
    ]
    
    if customer_id:
        context_parts.append(f"ID Client: {customer_id}")
    
    if documents:
        context_parts.append("\nDocuments pertinents de la base de connaissances:")
        for i, doc in enumerate(documents[:3], 1):
            title = doc.get("title", "Document")
            content = doc.get("content", "")[:200]
            context_parts.append(f"{i}. {title}: {content}")
    
    context = "\n".join(context_parts)
    context += "\n\nGénère une réponse appropriée pour ce client:"
    
    # Generate response using Response Builder team
    response_text = response_builder.print_response(context, stream=False)
    
    # Calculer métriques
    execution_time = int((time.time() - start_time) * 1000)
    tone = _detect_tone(emotion)
    
    # Logger dans la BDD unifiée
    if interaction_id:
        try:
            db_service.log_response(
                interaction_id=interaction_id,
                response_text=str(response_text),
                tone=tone,
                language="fr",
                confidence=confidence,
                generation_method="team",
                generation_time_ms=execution_time
            )
        except Exception as db_error:
            print(f"Erreur logging response BDD: {db_error}")
    
    return {
        "response": response_text,
        "tone": tone,
        "confidence": confidence,
        "execution_time_ms": execution_time,
        "interaction_id": interaction_id
    }


def _detect_tone(emotion: str) -> str:
    """Détermine le ton de la réponse basé sur l'émotion"""
    tone_mapping = {
        "angry": "empathetic",
        "frustrated": "empathetic",
        "stressed": "reassuring",
        "neutral": "professional",
        "satisfied": "friendly",
        "happy": "friendly"
    }
    return tone_mapping.get(emotion, "professional")
