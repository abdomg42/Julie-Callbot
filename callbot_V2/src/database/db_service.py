"""
Unified Database Service for Callbot Julie
Handles ALL interactions (simple CRM AND complex handoff cases)
"""
import psycopg2
from psycopg2.extras import RealDictCursor, Json
import os
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import json

from src.schemas import (
    IntentType,
    UrgencyLevel,
    EmotionType,
    ActionType
)


class DatabaseService:
    """Service unifié pour gérer toutes les interactions avec la BDD"""
    
    def __init__(self):
        # En développement: utiliser des fichiers JSON comme "base de données"
        # En production: utiliser PostgreSQL
        self.use_mock = os.getenv("USE_MOCK_DB", "true").lower() == "true"
        self.connection_string = os.getenv(
            "DATABASE_URL",
            "postgresql://user:password@localhost:5432/callbot_db"
        )
        
        # Mock storage (fichiers JSON)
        self.mock_data_dir = "data"
        self._init_mock_storage()
    
    def _init_mock_storage(self):
        """Initialise le stockage mock (fichiers JSON)"""
        if self.use_mock:
            os.makedirs(self.mock_data_dir, exist_ok=True)
            
            # Fichiers de données
            self.interactions_file = os.path.join(self.mock_data_dir, "interactions.json")
            self.conversations_file = os.path.join(self.mock_data_dir, "conversations.json")
            self.crm_actions_file = os.path.join(self.mock_data_dir, "crm_actions.json")
            self.handoff_tickets_file = os.path.join(self.mock_data_dir, "handoff_tickets.json")
            self.responses_file = os.path.join(self.mock_data_dir, "responses.json")
            
            # Créer les fichiers s'ils n'existent pas
            for file in [self.interactions_file, self.conversations_file, 
                        self.crm_actions_file, self.handoff_tickets_file, 
                        self.responses_file]:
                if not os.path.exists(file):
                    with open(file, 'w') as f:
                        json.dump([], f)
    
    def _load_json(self, filepath: str) -> List[Dict]:
        """Charge un fichier JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_json(self, filepath: str, data: List[Dict]):
        """Sauvegarde dans un fichier JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def _get_connection(self):
        """Crée une connexion à la base de données PostgreSQL"""
        if self.use_mock:
            return None
        return psycopg2.connect(self.connection_string)
    
    # =====================
    # INTERACTIONS
    # =====================
    
    def create_interaction(
        self,
        customer_id: str,
        session_id: str,
        intent: str,
        urgency: str,
        emotion: str,
        confidence: float,
        action_taken: str,
        priority: str,
        reason: str,
        metadata: Dict = None
    ) -> str:
        """
        Crée une nouvelle interaction (CAS SIMPLE OU COMPLEXE)
        
        Returns:
            interaction_id généré
        """
        interaction_id = f"INT-{datetime.now().year}-{uuid.uuid4().hex[:8].upper()}"
        
        interaction = {
            "interaction_id": interaction_id,
            "customer_id": customer_id,
            "session_id": session_id,
            "intent": intent,
            "urgency": urgency,
            "emotion": emotion,
            "confidence": confidence,
            "action_taken": action_taken,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resolved_at": None,
            "resolution_time_seconds": None,
            "customer_satisfaction": None,
            "metadata": metadata or {}
        }
        
        if self.use_mock:
            # Mode mock (fichier JSON)
            interactions = self._load_json(self.interactions_file)
            interactions.append(interaction)
            self._save_json(self.interactions_file, interactions)
        else:
            # Mode PostgreSQL - TABLE UNIQUE callbot_interactions
            conn = self._get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO callbot_interactions (
                        interaction_id, customer_id, session_id,
                        intent, urgency, emotion, confidence,
                        action_taken, priority, status, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    interaction_id, customer_id, session_id,
                    intent, urgency, emotion, confidence,
                    action_taken, priority, "pending",
                    Json(metadata or {})
                ))
                
                conn.commit()
            finally:
                cursor.close()
                conn.close()
        
        return interaction_id
    
    def update_interaction_status(
        self,
        interaction_id: str,
        status: str,
        resolved_by: Optional[str] = None
    ) -> bool:
        """Met à jour le statut d'une interaction"""
        
        if self.use_mock:
            interactions = self._load_json(self.interactions_file)
            
            for interaction in interactions:
                if interaction["interaction_id"] == interaction_id:
                    interaction["status"] = status
                    interaction["updated_at"] = datetime.now().isoformat()
                    
                    if status in ["completed", "failed"]:
                        interaction["resolved_at"] = datetime.now().isoformat()
                        
                        # Calculer temps de résolution
                        created = datetime.fromisoformat(interaction["created_at"])
                        resolved = datetime.now()
                        interaction["resolution_time_seconds"] = int((resolved - created).total_seconds())
                    
                    break
            
            self._save_json(self.interactions_file, interactions)
            return True
        else:
            # Mode PostgreSQL - TABLE UNIQUE callbot_interactions
            conn = self._get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    UPDATE callbot_interactions
                    SET status = %s,
                        updated_at = NOW(),
                        resolved_at = CASE WHEN %s IN ('completed', 'failed') THEN NOW() ELSE resolved_at END,
                        resolution_time_seconds = CASE 
                            WHEN %s IN ('completed', 'failed') 
                            THEN EXTRACT(EPOCH FROM (NOW() - created_at))::INTEGER
                            ELSE NULL 
                        END
                    WHERE interaction_id = %s
                """, (status, status, status, interaction_id))
                
                conn.commit()
                return True
            finally:
                cursor.close()
                conn.close()
    
    def get_interaction(self, interaction_id: str) -> Optional[Dict]:
        """Récupère une interaction par son ID"""
        
        if self.use_mock:
            interactions = self._load_json(self.interactions_file)
            for interaction in interactions:
                if interaction["interaction_id"] == interaction_id:
                    return interaction
            return None
        else:
            # Mode PostgreSQL - TABLE UNIQUE callbot_interactions
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            try:
                cursor.execute("""
                    SELECT * FROM callbot_interactions
                    WHERE interaction_id = %s
                """, (interaction_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
            finally:
                cursor.close()
                conn.close()
    
    # =====================
    # CONVERSATION MESSAGES
    # =====================
    
    def add_conversation_message(
        self,
        interaction_id: str,
        speaker: str,
        message_text: str,
        turn_number: int,
        detected_intent: Optional[str] = None,
        detected_emotion: Optional[str] = None,
        confidence: Optional[float] = None,
        metadata: Dict = None
    ) -> str:
        """Ajoute un message à la conversation - stocke dans conversation_history JSONB"""
        
        message_id = f"MSG-{uuid.uuid4().hex[:8].upper()}"
        
        message = {
            "message_id": message_id,
            "speaker": speaker,
            "message_text": message_text,
            "turn_number": turn_number,
            "detected_intent": detected_intent,
            "detected_emotion": detected_emotion,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        if self.use_mock:
            conversations = self._load_json(self.conversations_file)
            message["interaction_id"] = interaction_id
            conversations.append(message)
            self._save_json(self.conversations_file, conversations)
        else:
            # Mode PostgreSQL - Append au JSONB conversation_history
            conn = self._get_connection()
            cursor = conn.cursor()
            
            try:
                # Mettre à jour les champs directs aussi
                if speaker == "customer":
                    cursor.execute("""
                        UPDATE callbot_interactions
                        SET customer_message = %s,
                            conversation_history = conversation_history || %s::jsonb
                        WHERE interaction_id = %s
                    """, (message_text, Json([message]), interaction_id))
                else:
                    cursor.execute("""
                        UPDATE callbot_interactions
                        SET bot_response = %s,
                            conversation_history = conversation_history || %s::jsonb
                        WHERE interaction_id = %s
                    """, (message_text, Json([message]), interaction_id))
                
                conn.commit()
            finally:
                cursor.close()
                conn.close()
        
        return message_id
    
    def get_conversation_history(self, interaction_id: str) -> List[Dict]:
        """Récupère l'historique de conversation depuis conversation_history JSONB"""
        
        if self.use_mock:
            conversations = self._load_json(self.conversations_file)
            return [
                msg for msg in conversations 
                if msg["interaction_id"] == interaction_id
            ]
        else:
            # Mode PostgreSQL - Lire le JSONB conversation_history
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            try:
                cursor.execute("""
                    SELECT conversation_history
                    FROM callbot_interactions
                    WHERE interaction_id = %s
                """, (interaction_id,))
                
                row = cursor.fetchone()
                if row and row['conversation_history']:
                    return row['conversation_history']
                return []
            finally:
                cursor.close()
                conn.close()
    
    # =====================
    # CRM ACTIONS (CAS SIMPLES)
    # =====================
    
    def log_crm_action(
        self,
        interaction_id: str,
        customer_id: str,
        action_type: str,
        input_data: Dict,
        output_data: Dict,
        success: bool,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[int] = None
    ) -> str:
        """Enregistre une action CRM dans la table unique"""
        
        crm_action_id = f"CRM-{uuid.uuid4().hex[:8].upper()}"
        
        crm_action = {
            "crm_action_id": crm_action_id,
            "interaction_id": interaction_id,
            "customer_id": customer_id,
            "action_type": action_type,
            "input_data": input_data,
            "output_data": output_data,
            "success": success,
            "error_message": error_message,
            "executed_at": datetime.now().isoformat(),
            "execution_time_ms": execution_time_ms
        }
        
        if self.use_mock:
            crm_actions = self._load_json(self.crm_actions_file)
            crm_actions.append(crm_action)
            self._save_json(self.crm_actions_file, crm_actions)
        else:
            # Mode PostgreSQL - Mettre à jour la ligne d'interaction
            conn = self._get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    UPDATE callbot_interactions
                    SET action_type = %s,
                        action_result = %s,
                        success = %s,
                        crm_action_details = %s,
                        execution_time_ms = %s,
                        updated_at = NOW()
                    WHERE interaction_id = %s
                """, (
                    action_type,
                    Json(output_data),
                    success,
                    Json({"input": input_data, "error": error_message}),
                    execution_time_ms,
                    interaction_id
                ))
                
                conn.commit()
            finally:
                cursor.close()
                conn.close()
        
        return crm_action_id
    
    # =====================
    # HANDOFF TICKETS (CAS COMPLEXES)
    # =====================
    
    def create_handoff_ticket(
        self,
        interaction_id: str,
        customer_id: str,
        queue_type: str,
        department: str,
        estimated_wait_time_seconds: int,
        context_summary: str,
        key_information: Dict,
        skills_required: List[str] = None
    ) -> str:
        """Crée un ticket handoff - Met à jour l'interaction existante"""
        
        ticket_id = f"TKT-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"
        
        ticket = {
            "ticket_id": ticket_id,
            "interaction_id": interaction_id,
            "customer_id": customer_id,
            "queue_type": queue_type,
            "queue_position": None,
            "estimated_wait_time_seconds": estimated_wait_time_seconds,
            "agent_id": None,
            "agent_name": None,
            "department": department,
            "skills_required": skills_required or [],
            "ticket_status": "queued",
            "created_at": datetime.now().isoformat(),
            "assigned_at": None,
            "started_at": None,
            "resolved_at": None,
            "resolution_notes": None,
            "resolution_category": None,
            "context_summary": context_summary,
            "key_information": key_information
        }
        
        if self.use_mock:
            tickets = self._load_json(self.handoff_tickets_file)
            tickets.append(ticket)
            self._save_json(self.handoff_tickets_file, tickets)
        else:
            # Mode PostgreSQL - Mettre à jour l'interaction avec infos handoff
            conn = self._get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    UPDATE callbot_interactions
                    SET is_handoff = TRUE,
                        handoff_reason = %s,
                        handoff_queue = %s,
                        handoff_department = %s,
                        ticket_status = 'queued',
                        estimated_wait_seconds = %s,
                        metadata = metadata || %s,
                        updated_at = NOW()
                    WHERE interaction_id = %s
                """, (
                    context_summary,
                    queue_type,
                    department,
                    estimated_wait_time_seconds,
                    Json({"ticket_id": ticket_id, "skills_required": skills_required or [], "key_information": key_information}),
                    interaction_id
                ))
                
                conn.commit()
            finally:
                cursor.close()
                conn.close()
        
        return ticket_id
    
    def assign_ticket_to_agent(
        self,
        ticket_id: str,
        agent_id: str,
        agent_name: str
    ) -> bool:
        """Assigne un ticket à un agent"""
        
        if self.use_mock:
            tickets = self._load_json(self.handoff_tickets_file)
            
            for ticket in tickets:
                if ticket["ticket_id"] == ticket_id:
                    ticket["agent_id"] = agent_id
                    ticket["agent_name"] = agent_name
                    ticket["ticket_status"] = "assigned"
                    ticket["assigned_at"] = datetime.now().isoformat()
                    break
            
            self._save_json(self.handoff_tickets_file, tickets)
            return True
        else:
            # Mode PostgreSQL - Mettre à jour l'interaction
            conn = self._get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    UPDATE callbot_interactions
                    SET assigned_agent = %s,
                        ticket_status = 'assigned',
                        updated_at = NOW()
                    WHERE metadata->>'ticket_id' = %s
                """, (f"{agent_name} ({agent_id})", ticket_id))
                
                conn.commit()
                return True
            finally:
                cursor.close()
                conn.close()
    
    def resolve_ticket(
        self,
        ticket_id: str,
        resolution_notes: str,
        resolution_category: str
    ) -> bool:
        """Résout un ticket"""
        
        if self.use_mock:
            tickets = self._load_json(self.handoff_tickets_file)
            
            for ticket in tickets:
                if ticket["ticket_id"] == ticket_id:
                    ticket["ticket_status"] = "resolved"
                    ticket["resolved_at"] = datetime.now().isoformat()
                    ticket["resolution_notes"] = resolution_notes
                    ticket["resolution_category"] = resolution_category
                    break
            
            self._save_json(self.handoff_tickets_file, tickets)
            return True
        else:
            # Mode PostgreSQL - Mettre à jour l'interaction et son statut
            conn = self._get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    UPDATE callbot_interactions
                    SET ticket_status = 'resolved',
                        status = 'completed',
                        resolved_at = NOW(),
                        metadata = metadata || %s,
                        updated_at = NOW()
                    WHERE metadata->>'ticket_id' = %s
                """, (
                    Json({"resolution_notes": resolution_notes, "resolution_category": resolution_category}),
                    ticket_id
                ))
                
                conn.commit()
                return True
            finally:
                cursor.close()
                conn.close()
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """Récupère un ticket par son ID"""
        
        if self.use_mock:
            tickets = self._load_json(self.handoff_tickets_file)
            for ticket in tickets:
                if ticket["ticket_id"] == ticket_id:
                    return ticket
            return None
        else:
            # Mode PostgreSQL - Lire depuis l'interaction
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            try:
                cursor.execute("""
                    SELECT *
                    FROM callbot_interactions
                    WHERE metadata->>'ticket_id' = %s
                """, (ticket_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
            finally:
                cursor.close()
                conn.close()
    
    # =====================
    # RESPONSE LOGS - Plus utilisé avec table unique
    # =====================
    
    def log_response(
        self,
        interaction_id: str,
        response_text: str,
        tone: str,
        language: str,
        confidence: float,
        generation_method: str,
        generation_time_ms: int
    ) -> str:
        """Enregistre une réponse générée - Stocke dans bot_response"""
        
        response_id = f"RSP-{uuid.uuid4().hex[:8].upper()}"
        
        response = {
            "response_id": response_id,
            "interaction_id": interaction_id,
            "response_text": response_text,
            "tone": tone,
            "language": language,
            "confidence": confidence,
            "generation_method": generation_method,
            "generated_at": datetime.now().isoformat(),
            "generation_time_ms": generation_time_ms,
            "used": True,
            "edited": False,
            "edited_text": None
        }
        
        if self.use_mock:
            responses = self._load_json(self.responses_file)
            responses.append(response)
            self._save_json(self.responses_file, responses)
        else:
            # Mode PostgreSQL - Mettre à jour bot_response dans l'interaction
            conn = self._get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    UPDATE callbot_interactions
                    SET bot_response = %s,
                        metadata = metadata || %s,
                        updated_at = NOW()
                    WHERE interaction_id = %s
                """, (
                    response_text,
                    Json({"tone": tone, "language": language, "generation_method": generation_method, "generation_time_ms": generation_time_ms}),
                    interaction_id
                ))
                
                conn.commit()
            finally:
                cursor.close()
                conn.close()
        
        return response_id
    
    # =====================
    # ANALYTICS
    # =====================
    
    def get_daily_stats(self, date: Optional[str] = None) -> Dict:
        """Récupère les statistiques d'une journée depuis la table unique"""
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        if self.use_mock:
            interactions = self._load_json(self.interactions_file)
            
            # Filtrer par date
            daily_interactions = [
                i for i in interactions
                if i["created_at"].startswith(date)
            ]
            
            if not daily_interactions:
                return {
                    "date": date,
                    "total_interactions": 0,
                    "automated_responses": 0,
                    "crm_actions": 0,
                    "handoffs": 0
                }
            
            return {
                "date": date,
                "total_interactions": len(daily_interactions),
                "automated_responses": sum(1 for i in daily_interactions if i["action_taken"] == "automated_response"),
                "crm_actions": sum(1 for i in daily_interactions if i["action_taken"] == "crm_action"),
                "handoffs": sum(1 for i in daily_interactions if i["action_taken"] == "human_handoff"),
                "avg_confidence": sum(i["confidence"] for i in daily_interactions) / len(daily_interactions),
                "avg_resolution_time": sum(
                    i["resolution_time_seconds"] or 0 
                    for i in daily_interactions
                ) / len(daily_interactions)
            }
        else:
            # Mode PostgreSQL - Utiliser la vue v_daily_stats ou table unique
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            try:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_interactions,
                        SUM(CASE WHEN action_taken = 'automated_response' THEN 1 ELSE 0 END) as automated_responses,
                        SUM(CASE WHEN action_taken = 'crm_action' THEN 1 ELSE 0 END) as crm_actions,
                        SUM(CASE WHEN is_handoff = TRUE THEN 1 ELSE 0 END) as handoffs,
                        AVG(confidence) as avg_confidence,
                        AVG(resolution_time_seconds) as avg_resolution_time,
                        AVG(customer_satisfaction) as avg_satisfaction
                    FROM callbot_interactions
                    WHERE DATE(created_at) = %s
                """, (date,))
                
                return dict(cursor.fetchone())
            finally:
                cursor.close()
                conn.close()


# Instance globale
db_service = DatabaseService()
