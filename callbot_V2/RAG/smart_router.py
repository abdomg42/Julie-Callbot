"""
🤖 SMART QUERY ROUTER
========================================

Routes queries intelligently:
- Simple questions → RAG (instant response)
- Complex/unknown questions → Human agent

📥 INPUT:
{
  "query": "comment accéder à mon espace client"
}

📤 OUTPUT:
{
  "action": "rag_response",  # or "human_handoff"
  "response": "...",
  "confidence": 0.85,
  "documents": [...]
}
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from rag_api import RAGKnowledgeBase
from typing import Dict, Any
import json


class SmartQueryRouter:
    """
    🧠 Smart Router: Decides RAG vs Human Handoff
    
    Rules:
    1. High confidence (>0.7) → Use RAG
    2. Low confidence (<0.7) → Transfer to agent
    3. Complex queries → Transfer to agent
    """
    
    # Keywords indicating complex queries requiring human assistance
    COMPLEX_KEYWORDS = [
        "urgent", "réclamation", "litige", "problème", "erreur",
        "contentieux", "avocat", "juridique", "plainte", "insatisfait",
        "mécontent", "scandale", "arnaque", "escroquerie"
    ]
    
    # Strategy: Use RELATIVE scoring instead of absolute threshold
    # Since absolute scores are low (0.15-0.20), we check:
    # 1. Is there at least 1 document returned?
    # 2. Is the best match significantly better than random?
    MIN_DOCUMENTS = 1  # Must find at least 1 document
    MIN_RELATIVE_CONFIDENCE = 0.10  # Minimum score to consider (filters out pure noise)
    
    def __init__(self, rag_system: RAGKnowledgeBase = None):
        """Initialize router with RAG system"""
        self.rag = rag_system or RAGKnowledgeBase()
        print("✅ Smart Router initialized")
    
    def route_query(self, query: str, k: int = 3) -> Dict[str, Any]:
        """
        🎯 MAIN ROUTING METHOD
        
        Strategy: 
        - Complex keywords → Human
        - No results or very low score → Human
        - At least 1 document with reasonable score → RAG
        
        INPUT:
        {
          "query": "comment accéder à mon espace client"
        }
        
        OUTPUT:
        {
          "action": "rag_response",  # or "human_handoff"
          "response": "Document content...",
          "confidence": 0.19,
          "reason": "Document found in knowledge base",
          "documents": [...],
          "response_time_ms": 45
        }
        """
        
        # Step 1: Check if query contains complex keywords
        if self._is_complex_query(query):
            return self._create_handoff_response(
                query=query,
                reason="Query contains keywords requiring human assistance"
            )
        
        # Step 2: Get RAG results with confidence scores
        rag_result = self.rag.search_with_metadata(query, k=k)
        
        # Step 3: Check if we have any results
        if not rag_result['documents']:
            return self._create_handoff_response(
                query=query,
                reason="No matching documents found in knowledge base"
            )
        
        best_relevance = rag_result['documents'][0]['relevance_score']
        
        # Step 4: Check for topic relevance
        # If query is about insurance/banking and we found insurance/banking docs, use RAG
        # If query seems completely off-topic, transfer to human
        if self._is_completely_off_topic(query, rag_result['documents'][0]):
            return self._create_handoff_response(
                query=query,
                reason="Query appears to be outside insurance/banking domain",
                attempted_docs=rag_result['documents'][:2]
            )
        
        # Step 5: Decide action based on confidence
        # Use relative scoring: if we found something above minimum threshold, use RAG
        if best_relevance >= self.MIN_RELATIVE_CONFIDENCE:
            # Found a document → Use RAG
            return self._create_rag_response(query, rag_result, best_relevance)
        else:
            # Score too low (pure noise) → Transfer to human
            return self._create_handoff_response(
                query=query,
                reason=f"Very low confidence ({best_relevance:.2f} < {self.MIN_RELATIVE_CONFIDENCE})",
                attempted_docs=rag_result['documents'][:2]
            )
    
    def _is_complex_query(self, query: str) -> bool:
        """Check if query contains complex keywords"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.COMPLEX_KEYWORDS)
    
    def _is_completely_off_topic(self, query: str, best_doc: dict) -> bool:
        """
        Check if query is completely unrelated to insurance/banking domain.
        Uses simple keyword matching to detect off-topic queries.
        """
        query_lower = query.lower()
        
        # Common insurance/banking terms (should be in valid queries)
        domain_keywords = [
            'assurance', 'contrat', 'client', 'compte', 'espace', 'rachat',
            'versement', 'épargne', 'banque', 'cnp', 'coordonnées', 'sinistre',
            'prévoyance', 'bénéficiaire', 'capital', 'rente', 'fiscalité',
            'impôt', 'relevé', 'document', 'réclamation', 'modification'
        ]
        
        # Off-topic indicators (science fiction, technology, etc.)
        off_topic_keywords = [
            'quantique', 'spatial', 'alien', 'robot', 'ordinateur', 'jeu',
            'voyage temps', 'extraterrestre', 'fusée', 'astronomie'
        ]
        
        # If query contains off-topic keywords and no domain keywords → off-topic
        has_domain_keyword = any(keyword in query_lower for keyword in domain_keywords)
        has_off_topic_keyword = any(keyword in query_lower for keyword in off_topic_keywords)
        
        # Also check if best match has very low relevance (<0.16 = very weak)
        very_low_relevance = best_doc['relevance_score'] < 0.16
        
        return has_off_topic_keyword or (not has_domain_keyword and very_low_relevance)
    
    def _create_rag_response(self, query: str, rag_result: Dict, confidence: float) -> Dict[str, Any]:
        """Create response using RAG"""
        return {
            "action": "rag_response",
            "response": rag_result['documents'][0]['content'],
            "confidence": confidence,
            "reason": "Document found in knowledge base",
            "documents": rag_result['documents'],
            "response_time_ms": rag_result['response_time_ms'],
            "cost": 0.00,
            "source": "RAG"
        }
    
    def _create_handoff_response(self, query: str, reason: str, attempted_docs: list = None) -> Dict[str, Any]:
        """Create human handoff response"""
        return {
            "action": "human_handoff",
            "response": "Je transfère votre demande à un conseiller pour une réponse personnalisée.",
            "confidence": 0.0,
            "reason": reason,
            "query": query,
            "attempted_documents": attempted_docs or [],
            "handoff_message": f"Client query: {query}\nReason for handoff: {reason}",
            "source": "Human Agent Required"
        }


# ============================================================================
# 🧪 DEMO & TEST
# ============================================================================

def demo_router():
    """Demonstrate smart routing with different query types"""
    
    print("\n" + "="*80)
    print("🤖 SMART QUERY ROUTER DEMO")
    print("="*80)
    
    # Initialize router
    router = SmartQueryRouter()
    
    # Test cases
    test_queries = [
        {
            "query": "comment accéder à mon espace client",
            "expected": "rag_response",
            "description": "Simple question in knowledge base"
        },
        {
            "query": "faire un rachat",
            "expected": "rag_response",
            "description": "Standard procedure question"
        },
        {
            "query": "J'ai un problème urgent avec mon contrat",
            "expected": "human_handoff",
            "description": "Contains 'urgent' keyword"
        },
        {
            "query": "comment créer un portail quantique pour voyager dans le temps",
            "expected": "human_handoff",
            "description": "Completely out of scope (low confidence)"
        },
        {
            "query": "Je veux faire une réclamation",
            "expected": "human_handoff",
            "description": "Contains 'réclamation' keyword"
        }
    ]
    
    # Test each query
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'─'*80}")
        print(f"🧪 Test {i}: {test['description']}")
        print(f"📝 Query: \"{test['query']}\"")
        print(f"🎯 Expected: {test['expected']}")
        print('─'*80)
        
        # Route the query
        result = router.route_query(test['query'], k=3)
        
        # Display results
        print(f"\n✅ Action: {result['action']}")
        print(f"📊 Confidence: {result['confidence']:.2f}")
        print(f"💡 Reason: {result['reason']}")
        
        if result['action'] == "rag_response":
            print(f"\n📄 Response preview:")
            print(result['response'][:200] + "...")
            print(f"\n⏱️  Response time: {result['response_time_ms']}ms")
        else:
            print(f"\n🤝 Handoff message:")
            print(result['response'])
        
        # Verify expectation
        status = "✅ PASS" if result['action'] == test['expected'] else "❌ FAIL"
        print(f"\n{status}")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE")
    print("="*80)


def integration_example():
    """Show how to integrate with the callbot system"""
    
    print("\n" + "="*80)
    print("🔗 INTEGRATION EXAMPLE")
    print("="*80)
    
    router = SmartQueryRouter()
    
    # Example: User asks a question
    user_query = "comment modifier mes coordonnées"
    
    print(f"\n📞 User: \"{user_query}\"")
    print("\n🤖 Processing...")
    
    # Route the query
    result = router.route_query(user_query)
    
    # Handle the result
    if result['action'] == "rag_response":
        print("\n✅ Response from RAG:")
        print(f"   {result['response'][:150]}...")
        print(f"\n   ⚡ Response time: {result['response_time_ms']}ms")
        print(f"   💰 Cost: ${result['cost']}")
    
    elif result['action'] == "human_handoff":
        print("\n🤝 Transferring to human agent...")
        print(f"   Reason: {result['reason']}")
        print(f"   Message to agent: {result['handoff_message']}")
    
    print("\n" + "="*80)


# ============================================================================
# API ENDPOINT EXAMPLE
# ============================================================================

def api_endpoint_example():
    """Example of how to use in FastAPI"""
    
    example_code = '''
# In your main FastAPI app (src/api.py):

from RAG.smart_router import SmartQueryRouter

# Initialize once at startup
router = SmartQueryRouter()

@app.post("/query")
async def handle_query(query: str):
    """Handle user query with smart routing"""
    
    # Route the query
    result = router.route_query(query)
    
    if result['action'] == "rag_response":
        # Return RAG response directly
        return {
            "type": "text",
            "content": result['response'],
            "metadata": {
                "source": "knowledge_base",
                "confidence": result['confidence'],
                "response_time_ms": result['response_time_ms']
            }
        }
    
    elif result['action'] == "human_handoff":
        # Trigger human handoff
        # Call your CRM/handoff system here
        return {
            "type": "handoff",
            "content": result['response'],
            "metadata": {
                "reason": result['reason'],
                "query": result['query']
            }
        }
'''
    
    print("\n" + "="*80)
    print("💻 API INTEGRATION EXAMPLE")
    print("="*80)
    print(example_code)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Run demo
    demo_router()
    
    # Show integration example
    integration_example()
    
    # Show API example
    api_endpoint_example()
