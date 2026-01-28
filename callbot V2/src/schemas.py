"""
Data models and schemas for the Callbot system
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class IntentType(str, Enum):
    """Types of customer intents"""
    DECLARE_CLAIM = "declare_claim"
    CHECK_STATUS = "check_status"
    UPDATE_INFO = "update_info"
    GENERAL_INFO = "general_info"
    COMPLAINT = "complaint"
    PAYMENT_INFO = "payment_info"
    CANCEL_POLICY = "cancel_policy"


class UrgencyLevel(str, Enum):
    """Urgency levels for requests"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EmotionType(str, Enum):
    """Customer emotions"""
    NEUTRAL = "neutral"
    SATISFIED = "satisfied"
    STRESSED = "stressed"
    ANGRY = "angry"
    FRUSTRATED = "frustrated"


class ActionType(str, Enum):
    """Possible actions to take"""
    AUTOMATED_RESPONSE = "automated_response"
    CRM_ACTION = "crm_action"
    HUMAN_HANDOFF = "human_handoff"
    ESCALATE = "escalate"


# ===== INPUT SCHEMAS =====

class IntentData(BaseModel):
    """Data received from AI Core (Redouane's component)"""
    intent: IntentType
    urgency: UrgencyLevel
    confidence: float = Field(ge=0.0, le=1.0)
    emotion: EmotionType
    text: str
    conversation_context: List[Dict] = Field(default_factory=list)
    customer_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "intent": "declare_claim",
                "urgency": "high",
                "confidence": 0.91,
                "emotion": "stressed",
                "text": "Je veux déclarer un accident domestique",
                "conversation_context": [],
                "customer_id": "C12345"
            }
        }


class KnowledgeData(BaseModel):
    """Data received from Knowledge Base (Hatim's component)"""
    documents: List[Dict]
    query: str
    total_results: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "title": "Procédure sinistre accident de la vie",
                        "content": "Pour déclarer un sinistre...",
                        "relevance_score": 0.95
                    }
                ],
                "query": "declare accident domestique",
                "total_results": 3
            }
        }


# ===== OUTPUT SCHEMAS =====

class RoutingDecision(BaseModel):
    """Output from Tool Router"""
    action: ActionType
    reason: str
    priority: str
    metadata: Dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "human_handoff",
                "reason": "high_urgency_claim",
                "priority": "urgent",
                "metadata": {
                    "intent": "declare_claim",
                    "emotion": "stressed"
                },
                "timestamp": "2026-01-23T10:30:00"
            }
        }


class Response(BaseModel):
    """Output from Response Builder"""
    response_text: str
    tone: str
    language: str = "fr-FR"
    confidence: float = Field(ge=0.0, le=1.0)
    requires_followup: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "response_text": "Je comprends votre situation. Je vais vous aider à déclarer votre sinistre...",
                "tone": "empathetic",
                "language": "fr-FR",
                "confidence": 0.89,
                "requires_followup": False
            }
        }


# ===== CRM SCHEMAS =====

class CRMRequest(BaseModel):
    """Request to CRM system"""
    customer_id: str
    action: str  # "update_address", "check_policy", etc.
    data: Dict = Field(default_factory=dict)


class CRMResponse(BaseModel):
    """Response from CRM system"""
    success: bool
    data: Dict = Field(default_factory=dict)
    message: str


# ===== HUMAN HANDOFF SCHEMAS =====

class HandoffRequest(BaseModel):
    """Request for human agent escalation"""
    customer_id: Optional[str]
    intent: IntentType
    urgency: UrgencyLevel
    emotion: EmotionType
    context: str
    conversation_history: List[Dict] = Field(default_factory=list)
    priority: str = "medium"
    reason: str


class HandoffResponse(BaseModel):
    """Response from handoff system"""
    ticket_id: str
    agent_assigned: Optional[str] = None
    estimated_wait_time: Optional[int] = None  # in seconds
    status: str = "queued"
