"""
🧪 TEST YOUR RAG API
====================
Simple test to verify everything is working
"""

from rag_api import RAGKnowledgeBase
import json


def test_rag():
    print("="*80)
    print("🧪 TESTING RAG API")
    print("="*80)
    
    # Initialize
    print("\n1️⃣ Loading RAG system...")
    rag = RAGKnowledgeBase()
    print("✅ Loaded!")
    
    # Test queries
    test_queries = [
        "comment accéder à mon espace client",
        "faire un rachat",
        "qui est CNP Assurances"
    ]
    
    print(f"\n2️⃣ Testing {len(test_queries)} queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'─'*80}")
        print(f"Test {i}: {query}")
        print('─'*80)
        
        # Call API
        result = rag.search(query, k=3)
        
        # Display results
        print(f"✅ Found {len(result['documents'])} documents")
        print(f"\nFirst document preview:")
        print(result['documents'][0][:200] + "...")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80)
    print("\n🎯 Your RAG API is ready to use!")


if __name__ == "__main__":
    test_rag()
