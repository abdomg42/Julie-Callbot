"""
FastAPI application for Callbot REST API

🎯 ENDPOINTS PRINCIPAUX:
- POST /api/process      → Pipeline complet (AMI Phone System)
- POST /api/rag/query    → Recherche RAG directe
- POST /api/tts/generate → Génération TTS directe
- GET  /health           → Health check

📥 INPUT FORMAT (from AMI):
{
  "text": "Je veux déclarer un accident",
  "emotion": "stressed",
  "session_id": "call_123"
}

📤 OUTPUT FORMAT (to AMI):
{
  "action": "rag_response",
  "response_text": "Je comprends...",
  "audio_base64": "UklGRi4...",
  "confidence": 0.89
}
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add paths for imports
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "RAG"))

from src.teams.response_builder import generate_response
from src.schemas import (
    IntentData, 
    KnowledgeData, 
    Response as ResponseSchema,
    RoutingDecision
)

# Load environment
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Callbot Julie - API",
    description="API pour le système de callbot CNP Assurances",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== REQUEST MODELS =====

class CallbotRequest(BaseModel):
    """Complete request with intent and knowledge data"""
    intent_data: IntentData
    knowledge_data: Optional[KnowledgeData] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    components: List[str]
    version: str


# ===== NEW: CALLBOT PROCESS MODELS (for AMI integration) =====

class ProcessRequest(BaseModel):
    """
    🎯 Request format from AMI (Phone System)
    This is the main input format for the callbot pipeline.
    """
    text: str = Field(..., description="Transcribed user speech")
    emotion: str = Field(default="neutral", description="Detected emotion: stressed, angry, neutral, happy")
    confidence: float = Field(default=0.0, description="Emotion detection confidence")
    session_id: str = Field(default="", description="Call session identifier")
    conversation_history: List[Dict[str, str]] = Field(default=[], description="Previous conversation exchanges")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Je veux déclarer un accident domestique",
                "emotion": "stressed",
                "confidence": 0.82,
                "session_id": "call_12345",
                "conversation_history": [
                    {"role": "assistant", "text": "Bonjour, je suis Julie..."},
                    {"role": "user", "text": "Bonjour"}
                ]
            }
        }


class ProcessResponse(BaseModel):
    """
    🎯 Response format to AMI (Phone System)
    This is what the Phone System receives back.
    """
    action: str = Field(..., description="rag_response, crm_action, or human_handoff")
    response_text: str = Field(..., description="Generated response text")
    audio_base64: str = Field(default="", description="TTS audio in base64 format")
    confidence: float = Field(default=0.0, description="Response confidence score")
    next_step: str = Field(default="continue_conversation", description="continue_conversation, end_call, or transfer")
    documents_used: List[str] = Field(default=[], description="RAG documents used")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "action": "rag_response",
                "response_text": "Je comprends que cette situation peut être stressante. Pour déclarer un sinistre...",
                "audio_base64": "UklGRi4...",
                "confidence": 0.89,
                "next_step": "continue_conversation",
                "documents_used": ["Q12: Procédure sinistre..."],
                "metadata": {"tone": "empathetic", "tts_cached": False}
            }
        }


class RAGQueryRequest(BaseModel):
    """Request for direct RAG query"""
    query: str
    k: int = Field(default=3, description="Number of documents to return")


class TTSRequest(BaseModel):
    """Request for direct TTS generation"""
    text: str
    emotion: str = Field(default="neutral")


# ===== GLOBAL: Initialize Orchestrator =====

# Lazy initialization (will be done on first request or startup)
_orchestrator = None


def get_orchestrator():
    """Get or initialize the orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        try:
            from src.services.orchestrator import CallbotOrchestrator, CallbotRequest
            _orchestrator = CallbotOrchestrator(
                enable_tts=True,
                enable_llm=False  # Use templates by default
            )
        except Exception as e:
            print(f"⚠️  Orchestrator init error: {e}")
            _orchestrator = None
    return _orchestrator


# ===== ENDPOINTS =====

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "components": ["response_builder", "tools_router", "crm_agent", "human_handoff_agent"],
        "version": "1.0.0"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": ["response_builder", "tools_router", "crm_agent", "human_handoff_agent"],
        "version": "1.0.0"
    }


@app.post("/api/generate-response", response_model=ResponseSchema)
async def create_response(request: CallbotRequest):
    """
    Generate a response based on intent and knowledge data
    
    This is the main endpoint that:
    1. Receives intent from AI Core (Redouane's component)
    2. Receives knowledge from Knowledge Base (Hatim's component)
    3. Generates appropriate response using Response Builder
    4. Routes to CRM or Human Handoff if needed (via Tools Router)
    """
    try:
        intent_data = request.intent_data
        knowledge_data = request.knowledge_data
        
        # Extract documents if available
        documents = None
        if knowledge_data:
            documents = knowledge_data.documents
        
        # Generate response
        response_text = generate_response(
            intent=intent_data.intent.value,
            urgency=intent_data.urgency.value,
            emotion=intent_data.emotion.value,
            confidence=intent_data.confidence,
            text=intent_data.text,
            documents=documents,
            customer_id=intent_data.customer_id
        )
        
        # Determine tone based on emotion
        tone = "empathetic" if intent_data.emotion.value in ["stressed", "angry", "frustrated"] else "professional"
        
        return ResponseSchema(
            response_text=response_text,
            tone=tone,
            language="fr-FR",
            confidence=intent_data.confidence,
            requires_followup=False
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération de réponse: {str(e)}"
        )


@app.post("/api/test-routing")
async def test_routing(intent_data: IntentData):
    """
    Test endpoint to see routing decision without generating full response
    """
    try:
        # Determine which component would handle this
        if intent_data.urgency.value == "high" or intent_data.intent.value in ["declare_claim", "complaint"]:
            action = "human_handoff"
            reason = "high_urgency_or_complex_intent"
        elif intent_data.intent.value in ["update_info", "check_status", "payment_info"]:
            action = "crm_action"
            reason = "crm_data_operation"
        else:
            action = "automated_response"
            reason = "simple_query"
        
        return {
            "action": action,
            "reason": reason,
            "intent": intent_data.intent.value,
            "urgency": intent_data.urgency.value,
            "emotion": intent_data.emotion.value
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du test de routage: {str(e)}"
        )


# ===== NEW: MAIN CALLBOT ENDPOINTS (for AMI integration) =====

@app.post("/api/process", response_model=ProcessResponse)
async def process_callbot_request(request: ProcessRequest):
    """
    🎯 MAIN ENDPOINT - Complete Callbot Pipeline
    
    This is the primary endpoint that your AMI (Phone System) will call.
    
    Flow:
    1. Receives text + emotion from Speech-to-Text
    2. Routes query (RAG, CRM, or Human Handoff)
    3. Generates natural response
    4. Converts to audio (TTS)
    5. Returns complete response
    
    Input: ProcessRequest (text, emotion, session_id, ...)
    Output: ProcessResponse (response_text, audio_base64, action, ...)
    """
    try:
        orchestrator = get_orchestrator()
        
        if orchestrator is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Orchestrator not available. Please try again."
            )
        
        # Convert to internal format
        from src.services.orchestrator import CallbotRequest as InternalRequest
        
        internal_request = InternalRequest(
            text=request.text,
            emotion=request.emotion,
            confidence=request.confidence,
            session_id=request.session_id,
            conversation_history=request.conversation_history
        )
        
        # Process through orchestrator
        response = orchestrator.process(internal_request)
        
        return ProcessResponse(
            action=response.action,
            response_text=response.response_text,
            audio_base64=response.audio_base64,
            confidence=response.confidence,
            next_step=response.next_step,
            documents_used=response.documents_used,
            metadata=response.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement: {str(e)}"
        )


@app.post("/api/rag/query")
async def query_rag(request: RAGQueryRequest):
    """
    🔍 Direct RAG Query
    
    Query the knowledge base directly without full pipeline.
    Useful for testing or specific document retrieval.
    """
    try:
        from RAG.smart_router import SmartQueryRouter
        
        router = SmartQueryRouter()
        result = router.route_query(request.query, k=request.k)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG query error: {str(e)}"
        )


@app.post("/api/tts/generate")
async def generate_tts(request: TTSRequest):
    """
    🔊 Direct TTS Generation
    
    Generate audio from text directly without full pipeline.
    Useful for testing or pre-generating common phrases.
    """
    try:
        from src.services.tts_service import TTSService
        
        tts = TTSService()
        result = tts.generate_audio(
            text=request.text,
            emotion=request.emotion
        )
        
        return {
            "audio_base64": result.get("audio_base64", ""),
            "duration_ms": result.get("duration_ms", 0),
            "cached": result.get("cached", False),
            "generation_time_ms": result.get("generation_time_ms", 0)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS generation error: {str(e)}"
        )


@app.get("/api/stats")
async def get_stats():
    """
    📊 Get System Statistics
    
    Returns statistics about the callbot system.
    """
    orchestrator = get_orchestrator()
    
    if orchestrator:
        return {
            "status": "operational",
            "stats": orchestrator.get_stats()
        }
    else:
        return {
            "status": "initializing",
            "stats": {}
        }


# ===== STARTUP EVENT =====

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("\n" + "="*60)
    print("🚀 CALLBOT JULIE API - STARTING")
    print("="*60)
    print(f"📚 Documentation: http://localhost:8000/docs")
    print(f"📚 ReDoc: http://localhost:8000/redoc")
    print("\n🔧 Endpoints disponibles:")
    print("   POST /api/process      → Pipeline complet (AMI)")
    print("   POST /api/rag/query    → Recherche RAG directe")
    print("   POST /api/tts/generate → Génération TTS directe")
    print("   GET  /api/stats        → Statistiques système")
    print("   GET  /health           → Health check")
    
    # Pre-initialize orchestrator
    print("\n⏳ Initializing orchestrator...")
    orchestrator = get_orchestrator()
    if orchestrator:
        print("✅ Orchestrator ready!")
    else:
        print("⚠️  Orchestrator will initialize on first request")
    
    print("\n" + "="*60)
    print("✅ CALLBOT JULIE API READY!")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("👋 Callbot Julie API arrêtée")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
