"""Callbot Orchestrator - Main processing pipeline."""

import os
import sys
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR.parent.parent / "RAG"))

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


@dataclass
class CallbotRequest:
    """Request format for the callbot."""
    text: str
    emotion: str = "neutral"
    confidence: float = 0.0
    session_id: str = ""
    conversation_history: List[Dict] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class CallbotResponse:
    """Response format for the callbot."""
    action: str
    response_text: str
    audio_base64: str = ""
    confidence: float = 0.0
    next_step: str = "continue_conversation"  # or "end_call", "transfer"
    documents_used: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.documents_used is None:
            self.documents_used = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CallbotOrchestrator:
    """Main orchestrator for the callbot system."""
    
    def __init__(
        self,
        enable_tts: bool = True,
        enable_llm: bool = False,
        llm_provider: str = "ollama"
    ):
        """
        Initialize the Callbot Orchestrator.
        
        Args:
            enable_tts: Enable text-to-speech conversion
            enable_llm: Use LLM for response generation
            llm_provider: "openai", "anthropic", or "ollama"
        """
        print("\n" + "="*60)
        print("🤖 CALLBOT JULIE - ORCHESTRATOR INITIALIZATION")
        print("="*60)
        
        self.start_time = time.time()
        self.enable_tts = enable_tts
        self.enable_llm = enable_llm
        
        self.router = None
        self.rag = None
        self.response_builder = None
        self.tts = None
        
        self._init_smart_router()
        self._init_response_builder(enable_llm, llm_provider)
        self._init_tts(enable_tts)
        
        self.stats = {
            "total_requests": 0,
            "rag_responses": 0,
            "crm_actions": 0,
            "human_handoffs": 0,
            "avg_response_time_ms": 0,
            "total_response_time_ms": 0
        }
    
    def _init_smart_router(self):
        """Initialize Smart Router."""
        try:
            rag_path = Path(__file__).parent.parent.parent.parent / "RAG"
            sys.path.insert(0, str(rag_path))
            from smart_router import SmartQueryRouter
            self.router = SmartQueryRouter()
        except Exception:
            try:
                rag_path = Path(__file__).parent.parent.parent.parent / "RAG"
                sys.path.insert(0, str(rag_path))
                from rag_api import RAGKnowledgeBase
                self.rag = RAGKnowledgeBase()
                self.router = None
            except Exception:
                self.router = None
                self.rag = None
    
    def _init_response_builder(self, enable_llm: bool, llm_provider: str):
        """Initialize Response Builder."""
        try:
            from src.services.response_builder import ResponseBuilder
            self.response_builder = ResponseBuilder(
                use_llm=enable_llm,
                llm_provider=llm_provider
            )
        except ImportError:
            from response_builder import ResponseBuilder
            self.response_builder = ResponseBuilder(
                use_llm=enable_llm,
                llm_provider=llm_provider
            )
    
    def _init_tts(self, enable_tts: bool):
        """Initialize TTS Service."""
        if not enable_tts:
            self.tts = None
            return
        
        try:
            from .optimized_tts_service import OptimizedTTSService
            self.tts = OptimizedTTSService()
            self.tts.preload_common_phrases()
        except ImportError:
            try:
                from .simple_tts_service import SimpleTTSService
                self.tts = SimpleTTSService()
            except Exception:
                self.tts = None
    
    def process(self, request: CallbotRequest) -> CallbotResponse:
        """Process a callbot request and return response."""
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        routing_result = self._route_query(request.text)
        action = routing_result.get("action", "rag_response")
        
        if action == "human_handoff":
            response = self._handle_handoff(request, routing_result)
        elif action == "crm_action":
            response = self._handle_crm(request, routing_result)
        else:
            response = self._handle_rag(request, routing_result)
        
        if self.enable_tts and self.tts:
            audio_result = self.tts.generate_speech(
                text=response.response_text,
                emotion=request.emotion
            )
            response.audio_base64 = audio_result.get("audio_base64", "")
            response.metadata["tts_generation_ms"] = audio_result.get("generation_time", 0) * 1000
            response.metadata["tts_cached"] = audio_result.get("cached", False)
        
        total_time_ms = (time.time() - start_time) * 1000
        response.metadata["total_response_time_ms"] = round(total_time_ms, 2)
        
        self.stats["total_response_time_ms"] += total_time_ms
        self.stats["avg_response_time_ms"] = (
            self.stats["total_response_time_ms"] / self.stats["total_requests"]
        )
        
        print(f"   ✅ Response generated in {total_time_ms:.0f}ms")
        
        return response
    
    def _route_query(self, text: str) -> Dict[str, Any]:
        """Route query using Smart Router."""
        if self.router:
            return self.router.route_query(text)
        elif hasattr(self, 'rag') and self.rag:
            # Direct RAG search (no routing logic)
            result = self.rag.search_with_metadata(text, k=3)
            return {
                "action": "rag_response",
                "documents": result.get("documents", []),
                "confidence": result["documents"][0]["relevance_score"] if result.get("documents") else 0
            }
        else:
            return {
                "action": "human_handoff",
                "reason": "No RAG system available"
            }
    
    def _handle_rag(self, request: CallbotRequest, routing_result: Dict) -> CallbotResponse:
        """Handle RAG response."""
        self.stats["rag_responses"] += 1
        
        # Extract documents
        documents = []
        if "documents" in routing_result:
            for doc in routing_result["documents"]:
                if isinstance(doc, dict):
                    documents.append(doc.get("content", str(doc)))
                else:
                    documents.append(str(doc))
        
        # Generate response
        response_result = self.response_builder.generate_response(
            query=request.text,
            documents=documents,
            emotion=request.emotion,
            conversation_history=request.conversation_history,
            action_type="rag_response"
        )
        
        return CallbotResponse(
            action="rag_response",
            response_text=response_result["response_text"],
            confidence=routing_result.get("confidence", 0),
            next_step="continue_conversation",
            documents_used=[d[:100] for d in documents[:2]],
            metadata={
                "tone": response_result.get("tone", "professional"),
                "generation_method": response_result.get("generation_method", "template")
            }
        )
    
    def _handle_handoff(self, request: CallbotRequest, routing_result: Dict) -> CallbotResponse:
        """Handle human handoff."""
        self.stats["human_handoffs"] += 1
        
        # Generate handoff response
        response_result = self.response_builder.generate_response(
            query=request.text,
            documents=[],
            emotion=request.emotion,
            action_type="human_handoff"
        )
        
        return CallbotResponse(
            action="human_handoff",
            response_text=response_result["response_text"],
            confidence=0.0,
            next_step="transfer",
            metadata={
                "handoff_reason": routing_result.get("reason", "Complex query"),
                "session_id": request.session_id,
                "emotion": request.emotion,
                "original_query": request.text
            }
        )
    
    def _handle_crm(self, request: CallbotRequest, routing_result: Dict) -> CallbotResponse:
        """Handle CRM action."""
        self.stats["crm_actions"] += 1
        
        # For now, generate a confirmation response
        # TODO: Integrate with actual CRM agent
        response_result = self.response_builder.generate_response(
            query="Votre demande a été enregistrée.",
            documents=[],
            emotion=request.emotion,
            action_type="crm_action"
        )
        
        return CallbotResponse(
            action="crm_action",
            response_text=response_result["response_text"],
            confidence=1.0,
            next_step="continue_conversation",
            metadata={
                "crm_action": routing_result.get("crm_action", "unknown"),
                "success": True
            }
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            **self.stats,
            "tts_enabled": self.enable_tts,
            "llm_enabled": self.enable_llm,
            "router_available": self.router is not None
        }


# ============================================================================
# 🧪 TEST
# ============================================================================

def test_orchestrator():
    """Test the orchestrator pipeline."""
    orchestrator = CallbotOrchestrator(enable_tts=False, enable_llm=False)
    
    test_scenarios = [
        CallbotRequest(text="Comment accéder à mon espace client ?", emotion="neutral", session_id="test_001"),
        CallbotRequest(text="Je veux déclarer un accident de la vie", emotion="stressed", session_id="test_002"),
        CallbotRequest(text="J'ai un problème urgent avec mon contrat", emotion="angry", session_id="test_003"),
    ]
    
    for request in test_scenarios:
        response = orchestrator.process(request)
        print(f"Query: {request.text[:50]}... -> Action: {response.action}")


if __name__ == "__main__":
    test_orchestrator()
