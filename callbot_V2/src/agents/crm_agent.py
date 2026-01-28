"""
CRM Agent - Handles customer relationship management operations
"""
from agno.agent import Agent
from agno.tools import tool
from typing import Dict, Optional
import httpx
import os
import time
from src.schemas import CRMRequest, CRMResponse
from src.database.db_service import db_service


# ===== CRM TOOLS =====

@tool
def update_customer_address(customer_id: str, new_address: Dict, interaction_id: Optional[str] = None) -> Dict:
    """
    Update customer address in CRM system
    
    Args:
        customer_id: The customer's unique identifier
        new_address: Dictionary containing street, city, postal_code, country
        interaction_id: ID de l'interaction (pour tracking en BDD)
    
    Returns:
        Dictionary with success status and confirmation message
    """
    crm_api_url = os.getenv("CRM_API_URL", "http://localhost:8003/api")
    start_time = time.time()
    
    try:
        # Simulate CRM API call
        payload = {
            "customer_id": customer_id,
            "action": "update_address",
            "data": new_address
        }
        
        # In production, this would be an actual API call:
        # response = httpx.post(f"{crm_api_url}/customers/update", json=payload)
        
        # Mock response for development
        success = True
        output_data = {**new_address, "updated_at": time.time()}
        error_message = None
        
        result = {
            "success": True,
            "message": f"Adresse mise à jour pour le client {customer_id}",
            "data": output_data
        }
        
    except Exception as e:
        success = False
        output_data = {}
        error_message = str(e)
        
        result = {
            "success": False,
            "message": f"Erreur lors de la mise à jour: {str(e)}",
            "data": {}
        }
    
    finally:
        execution_time = int((time.time() - start_time) * 1000)
        
        # Logger dans la BDD unifiée
        if interaction_id:
            try:
                db_service.log_crm_action(
                    interaction_id=interaction_id,
                    customer_id=customer_id,
                    action_type="update_address",
                    input_data={"new_address": new_address},
                    output_data=output_data,
                    success=success,
                    error_message=error_message,
                    execution_time_ms=execution_time
                )
                
                # Mettre à jour statut interaction
                if success:
                    db_service.update_interaction_status(
                        interaction_id, "completed", "crm_agent"
                    )
                else:
                    db_service.update_interaction_status(
                        interaction_id, "failed"
                    )
            except Exception as db_error:
                print(f"Erreur logging BDD: {db_error}")
    
    return result


@tool
def check_policy_status(customer_id: str, policy_number: Optional[str] = None, interaction_id: Optional[str] = None) -> Dict:
    """
    Check the status of a customer's insurance policy
    
    Args:
        customer_id: The customer's unique identifier
        policy_number: Optional specific policy number
        interaction_id: ID de l'interaction (pour tracking en BDD)
    
    Returns:
        Dictionary with policy status information
    """
    crm_api_url = os.getenv("CRM_API_URL", "http://localhost:8003/api")
    start_time = time.time()
    
    try:
        # Mock policy data
        success = True
        policy_data = {
            "customer_id": customer_id,
            "policy_number": policy_number or "POL-2026-001",
            "status": "active",
            "coverage": "Accidents de la vie",
            "expiry_date": "2027-12-31",
            "premium": "25.99€/mois"
        }
        error_message = None
        
        result = {
            "success": True,
            "message": "Informations de police récupérées",
            "data": policy_data
        }
    except Exception as e:
        success = False
        policy_data = {}
        error_message = str(e)
        
        result = {
            "success": False,
            "message": f"Erreur lors de la récupération: {str(e)}",
            "data": {}
        }
    
    finally:
        execution_time = int((time.time() - start_time) * 1000)
        
        if interaction_id:
            try:
                db_service.log_crm_action(
                    interaction_id=interaction_id,
                    customer_id=customer_id,
                    action_type="check_policy_status",
                    input_data={"customer_id": customer_id, "policy_number": policy_number},
                    output_data=policy_data,
                    success=success,
                    error_message=error_message,
                    execution_time_ms=execution_time
                )
                
                if success:
                    db_service.update_interaction_status(interaction_id, "completed", "crm_agent")
                else:
                    db_service.update_interaction_status(interaction_id, "failed")
            except Exception as db_error:
                print(f"Erreur logging BDD: {db_error}")
    
    return result


@tool
def get_customer_info(customer_id: str, interaction_id: Optional[str] = None) -> Dict:
    """
    Retrieve customer information from CRM
    
    Args:
        customer_id: The customer's unique identifier
        interaction_id: ID de l'interaction (pour tracking en BDD)
    
    Returns:
        Dictionary with customer details
    """
    start_time = time.time()
    
    try:
        # Mock customer data
        success = True
        customer_data = {
            "customer_id": customer_id,
            "name": "Jean Dupont",
            "email": "jean.dupont@example.com",
            "phone": "+33 1 23 45 67 89",
            "policies": ["POL-2026-001"],
            "status": "active",
            "member_since": "2020-05-15"
        }
        error_message = None
        
        result = {
            "success": True,
            "message": "Informations client récupérées",
            "data": customer_data
        }
    except Exception as e:
        success = False
        customer_data = {}
        error_message = str(e)
        
        result = {
            "success": False,
            "message": f"Erreur lors de la récupération: {str(e)}",
            "data": {}
        }
    
    finally:
        execution_time = int((time.time() - start_time) * 1000)
        
        if interaction_id:
            try:
                db_service.log_crm_action(
                    interaction_id=interaction_id,
                    customer_id=customer_id,
                    action_type="get_customer_info",
                    input_data={"customer_id": customer_id},
                    output_data=customer_data,
                    success=success,
                    error_message=error_message,
                    execution_time_ms=execution_time
                )
                
                if success:
                    db_service.update_interaction_status(interaction_id, "completed", "crm_agent")
                else:
                    db_service.update_interaction_status(interaction_id, "failed")
            except Exception as db_error:
                print(f"Erreur logging BDD: {db_error}")
    
    return result


@tool
def update_payment_method(customer_id: str, payment_info: Dict, interaction_id: Optional[str] = None) -> Dict:
    """
    Update customer payment method
    
    Args:
        customer_id: The customer's unique identifier
        payment_info: Dictionary containing payment method details
        interaction_id: ID de l'interaction (pour tracking en BDD)
    
    Returns:
        Dictionary with success status
    """
    start_time = time.time()
    
    try:
        success = True
        output_data = {
            "payment_method": payment_info.get("method", "card"),
            "last_four": payment_info.get("last_four", "****")
        }
        error_message = None
        
        result = {
            "success": True,
            "message": f"Méthode de paiement mise à jour pour {customer_id}",
            "data": output_data
        }
    except Exception as e:
        success = False
        output_data = {}
        error_message = str(e)
        
        result = {
            "success": False,
            "message": f"Erreur lors de la mise à jour: {str(e)}",
            "data": {}
        }
    
    finally:
        execution_time = int((time.time() - start_time) * 1000)
        
        if interaction_id:
            try:
                db_service.log_crm_action(
                    interaction_id=interaction_id,
                    customer_id=customer_id,
                    action_type="update_payment_method",
                    input_data=payment_info,
                    output_data=output_data,
                    success=success,
                    error_message=error_message,
                    execution_time_ms=execution_time
                )
                
                if success:
                    db_service.update_interaction_status(interaction_id, "completed", "crm_agent")
                else:
                    db_service.update_interaction_status(interaction_id, "failed")
            except Exception as db_error:
                print(f"Erreur logging BDD: {db_error}")
    
    return result


# ===== CRM AGENT =====

crm_agent = Agent(
    name="CRM Agent",
    role="Gestionnaire des opérations CRM et données client",
    model="openai:gpt-4o-mini",
    tools=[
        update_customer_address,
        check_policy_status,
        get_customer_info,
        update_payment_method
    ],
    instructions=[
        "Tu es un agent spécialisé dans la gestion des données clients chez CNP Assurances.",
        "Tu peux mettre à jour les informations client, consulter les polices d'assurance, et gérer les paiements.",
        "Sois précis et confirme toujours les actions effectuées.",
        "Si une information est manquante, demande-la de manière claire.",
        "Respecte la confidentialité des données clients."
    ],
    markdown=True,
    debug_mode=False
)
