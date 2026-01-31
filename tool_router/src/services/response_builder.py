"""
📝 RESPONSE BUILDER - LLM-BASED RESPONSE GENERATION
====================================================

Génère des réponses naturelles pour le callbot Julie.
Utilise les documents RAG + contexte émotionnel pour créer
des réponses adaptées, empathiques et professionnelles.

✅ FONCTIONNALITÉS:
- Reformulation des documents RAG en langage naturel
- Adaptation au ton selon l'émotion du client
- Personnalité "Julie" cohérente
- Réponses courtes optimisées pour le vocal (2-3 phrases max)

📥 INPUT:
{
  "query": "Je veux déclarer un accident",
  "documents": ["Procédure sinistre...", ...],
  "emotion": "stressed",
  "conversation_history": [...]
}

📤 OUTPUT:
{
  "response_text": "Je comprends, c'est stressant. Pour déclarer...",
  "tone": "empathetic",
  "source_documents": ["doc1", "doc2"]
}
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

# Persona template for Julie
JULIE_PERSONA = """Tu es Julie, assistante virtuelle de CNP Assurances.

🎯 TON RÔLE:
- Aider les clients avec leurs questions sur l'assurance
- Être professionnelle mais chaleureuse
- Donner des réponses claires et concises

📏 RÈGLES DE RÉPONSE:
1. Maximum 2-3 phrases (c'est pour un callbot vocal)
2. Langage simple, pas de jargon
3. Toujours proposer de l'aide supplémentaire
4. Ne jamais inventer d'informations

😊 ADAPTATION ÉMOTIONNELLE:
- Si le client est stressé → Rassurer d'abord
- Si le client est en colère → Rester calme, montrer de l'empathie
- Si le client est neutre → Ton professionnel standard
"""

# Emotion-specific prefixes
EMOTION_PREFIXES = {
    "stressed": "Je comprends que cette situation peut être stressante. ",
    "angry": "Je comprends votre frustration et je suis là pour vous aider. ",
    "sad": "Je suis désolée pour cette situation difficile. ",
    "neutral": "",
    "happy": ""
}

# Emotion-specific tones
EMOTION_TONES = {
    "stressed": "empathetic",
    "angry": "calm_reassuring",
    "sad": "compassionate",
    "neutral": "professional",
    "happy": "friendly"
}


class ResponseBuilder:
    """
    🎯 Response Builder - Transforms RAG documents into natural responses
    
    Two modes:
    1. WITH LLM (OpenAI/Claude/Ollama) - Best quality
    2. WITHOUT LLM (Template-based) - Fallback, still good
    """
    
    def __init__(self, use_llm: bool = False, llm_provider: str = "ollama"):
        """
        Initialize Response Builder.
        
        Args:
            use_llm: Whether to use LLM for response generation
            llm_provider: "openai", "anthropic", or "ollama"
        """
        print("📝 Initializing Response Builder...")
        
        self.use_llm = use_llm
        self.llm_provider = llm_provider
        self.llm_client = None
        
        if use_llm:
            self._init_llm(llm_provider)
        else:
            print("💡 Using template-based responses (no LLM)")
            print("   To enable LLM, set use_llm=True")
        
        print("✅ Response Builder ready!")
    
    def _init_llm(self, provider: str):
        """Initialize LLM client based on provider."""
        try:
            if provider == "openai":
                import openai
                self.llm_client = openai.OpenAI()
                print("✅ OpenAI GPT initialized")
                
            elif provider == "anthropic":
                import anthropic
                self.llm_client = anthropic.Anthropic()
                print("✅ Anthropic Claude initialized")
                
            elif provider == "ollama":
                # Ollama runs locally, just need requests
                import requests
                self.llm_client = "ollama"
                print("✅ Ollama (local) initialized")
                print("   Make sure Ollama is running: ollama serve")
                
            else:
                print(f"⚠️  Unknown provider: {provider}")
                self.use_llm = False
                
        except ImportError as e:
            print(f"⚠️  LLM library not installed: {e}")
            print("   Falling back to template mode")
            self.use_llm = False
        except Exception as e:
            print(f"⚠️  Error initializing LLM: {e}")
            self.use_llm = False
    
    def generate_response(
        self,
        query: str,
        documents: List[str],
        emotion: str = "neutral",
        conversation_history: List[Dict] = None,
        action_type: str = "rag_response"
    ) -> Dict[str, Any]:
        """
        🎯 MAIN METHOD - Generate a natural response
        
        Args:
            query: User's question
            documents: Relevant documents from RAG
            emotion: Detected emotion (stressed, angry, neutral, etc.)
            conversation_history: Previous exchanges
            action_type: rag_response, crm_action, or human_handoff
            
        Returns:
            {
                "response_text": "...",
                "tone": "empathetic",
                "source_documents": [...],
                "generation_method": "template"  # or "llm"
            }
        """
        # Handle different action types
        if action_type == "human_handoff":
            return self._generate_handoff_response(emotion)
        
        if action_type == "crm_action":
            return self._generate_crm_response(query, emotion)
        
        # Special handling for greetings - don't use RAG documents
        if self._is_greeting(query):
            return self._generate_greeting_response(query, emotion)
        
        # Special handling for goodbyes - don't use RAG documents
        if self._is_goodbye(query):
            return self._generate_goodbye_response(query, emotion)
        
        # Standard RAG response
        if self.use_llm and self.llm_client:
            return self._generate_llm_response(
                query, documents, emotion, conversation_history
            )
        else:
            return self._generate_template_response(
                query, documents, emotion
            )
    
    def _generate_template_response(
        self,
        query: str,
        documents: List,
        emotion: str
    ) -> Dict[str, Any]:
        """
        Generate response using templates (no LLM needed).
        Optimized for voice: VERY SHORT responses (< 100 chars) for fast TTS (~1s).
        """
        # Get emotion prefix
        prefix = EMOTION_PREFIXES.get(emotion, "")
        tone = EMOTION_TONES.get(emotion, "professional")
        
        # Maximum response length for fast TTS
        # 180 chars ≈ 2-3s with gTTS + accélération 1.2x = ~2.5s final
        # Balance entre qualité d'information et rapidité
        MAX_VOICE_LENGTH = 180
        
        # Extract the most relevant part from documents
        if documents and len(documents) > 0:
            # Take the first document (most relevant)
            main_doc = documents[0]
            
            # Handle dict format from RAG (with 'content' key)
            if isinstance(main_doc, dict):
                main_doc_content = main_doc.get('content', str(main_doc))
            else:
                main_doc_content = str(main_doc)
            
            # Clean up the document
            # If it's in Q&A format, extract the answer
            if "Réponse:" in main_doc_content:
                parts = main_doc_content.split("Réponse:")
                if len(parts) > 1:
                    answer = parts[1].strip()
                else:
                    answer = main_doc_content
            else:
                answer = main_doc_content
            
            # Truncate for voice - find a natural break point (plus intelligent)
            if len(answer) > MAX_VOICE_LENGTH:
                # 1. Try to cut at sentence end (.)
                cut_point = answer[:MAX_VOICE_LENGTH].rfind('.')
                if cut_point > MAX_VOICE_LENGTH * 0.6:  # Au moins 60% de la limite
                    main_content = answer[:cut_point + 1]
                # 2. Try to cut after a complete instruction (like "1) ... 2) ...")
                elif ') ' in answer[:MAX_VOICE_LENGTH]:
                    instructions = answer[:MAX_VOICE_LENGTH].split(') ')
                    if len(instructions) > 1:
                        # Keep complete instructions
                        main_content = ') '.join(instructions[:-1]) + ')'
                    else:
                        cut_point = answer[:MAX_VOICE_LENGTH].rfind(' ')
                        main_content = answer[:cut_point] + "."
                # 3. Cut at word boundary
                else:
                    cut_point = answer[:MAX_VOICE_LENGTH].rfind(' ')
                    main_content = answer[:cut_point] + "."
            else:
                main_content = answer
            
            # Ajouter une indication si la réponse a été raccourcie
            if len(answer) > MAX_VOICE_LENGTH:
                print(f" -- Réponse raccourcie: {len(answer)} → {len(main_content)} chars")
            
            # Build response (keep it short!)
            response_text = f"{prefix}{main_content}"
            
        else:
            # No documents found - use fallback templates for common questions
            response_text = self._get_fallback_response(query, prefix)
        
        return {
            "response_text": response_text,
            "tone": tone,
            "source_documents": documents[:2] if documents else [],
            "generation_method": "template"
        }

    def _get_fallback_response(self, query: str, prefix: str) -> str:
        """Get SHORT fallback response for common questions (optimized for voice)."""
        query_lower = query.lower()
        
        # Greeting responses - SHORT for TTS
        if any(word in query_lower for word in ["bonjour", "bonsoir", "salut", "hello"]):
            return f"{prefix}Bonjour ! Je suis Julie de CNP Assurances. Comment puis-je vous aider ?"
        
        # Goodbye
        if any(word in query_lower for word in ["au revoir", "merci", "bye", "à bientôt"]):
            return f"{prefix}Merci pour votre appel. À bientôt !"
        
        # Common SHORT responses for insurance topics
        elif any(word in query_lower for word in ["modifier", "changer", "information"]):
            return f"{prefix}Pour modifier vos informations, connectez-vous à votre espace client ou appelez le 3477."
        
        elif any(word in query_lower for word in ["sinistre", "déclaration", "accident"]):
            return f"{prefix}Pour déclarer un sinistre, appelez le 3477 ou utilisez votre espace client en ligne."
        
        elif any(word in query_lower for word in ["contrat", "police", "garantie"]):
            return f"{prefix}Consultez vos contrats sur votre espace client ou appelez le 3477."
        
        elif any(word in query_lower for word in ["remboursement", "indemnisation", "paiement"]):
            return f"{prefix}Pour le suivi de vos remboursements, consultez votre espace client ou appelez le 3477."
        
        else:
            return f"{prefix}Je peux vous renseigner sur vos contrats et sinistres. Quelle est votre question ?"
    
    def _is_greeting(self, query: str) -> bool:
        """Check if query is a greeting."""
        query_lower = query.lower().strip()
        greeting_words = ["bonjour", "bonsoir", "salut", "hello", "hi", "allô", "allo"]
        return any(word in query_lower for word in greeting_words) and len(query_lower) < 30
    
    def _is_goodbye(self, query: str) -> bool:
        """Check if query is a goodbye."""
        query_lower = query.lower().strip()
        goodbye_words = ["au revoir", "aurevoir", "bye", "à bientôt", "a bientot", 
                        "adieu", "ciao", "bonne journée", "merci au revoir", "merci"]
        # Check for goodbye intent
        return any(word in query_lower for word in goodbye_words) and len(query_lower) < 40
    
    def _generate_goodbye_response(self, query: str, emotion: str) -> Dict[str, Any]:
        """Generate a SHORT goodbye response (optimized for voice TTS)."""
        prefix = EMOTION_PREFIXES.get(emotion, "")
        tone = EMOTION_TONES.get(emotion, "professional")
        
        # Short goodbye for fast TTS (< 1s)
        response_text = f"{prefix}Merci pour votre appel. À bientôt !"
        
        return {
            "response_text": response_text,
            "tone": tone,
            "source_documents": [],  # No documents for goodbyes!
            "generation_method": "goodbye_template",
            "is_final": True  # Signal to end conversation
        }
    
    def _generate_greeting_response(self, query: str, emotion: str) -> Dict[str, Any]:
        """Generate a SHORT greeting response (optimized for voice TTS)."""
        prefix = EMOTION_PREFIXES.get(emotion, "")
        tone = EMOTION_TONES.get(emotion, "professional")
        
        # Short greeting for fast TTS (< 1s)
        response_text = f"{prefix}Bonjour ! Je suis Julie de CNP Assurances. Comment puis-je vous aider ?"
        
        return {
            "response_text": response_text,
            "tone": tone,
            "source_documents": [],  # No documents for greetings!
            "generation_method": "greeting_template"
        }
    
    def _generate_llm_response(
        self,
        query: str,
        documents: List[str],
        emotion: str,
        conversation_history: List[Dict]
    ) -> Dict[str, Any]:
        """Generate response using LLM (OpenAI/Claude/Ollama)."""
        
        # Build context from documents
        docs_context = "\n".join([f"- {doc[:200]}" for doc in documents[:3]])
        
        # Build conversation context
        history_context = ""
        if conversation_history:
            last_exchanges = conversation_history[-4:]  # Last 2 exchanges
            history_context = "\n".join([
                f"{'Client' if ex.get('role') == 'user' else 'Julie'}: {ex.get('text', '')}"
                for ex in last_exchanges
            ])
        
        # Build prompt
        prompt = f"""{JULIE_PERSONA}

📋 CONTEXTE DE LA CONVERSATION:
{history_context if history_context else "Début de conversation"}

😊 ÉMOTION DÉTECTÉE DU CLIENT: {emotion}

📚 DOCUMENTS PERTINENTS:
{docs_context}

❓ QUESTION DU CLIENT:
{query}

📝 TA RÉPONSE (2-3 phrases max, adaptée à l'émotion):"""

        try:
            if self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.7
                )
                response_text = response.choices[0].message.content
                
            elif self.llm_provider == "anthropic":
                response = self.llm_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = response.content[0].text
                
            elif self.llm_provider == "ollama":
                import requests
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "mistral",  # or llama2, etc.
                        "prompt": prompt,
                        "stream": False,
                        "options": {"num_predict": 200}
                    },
                    timeout=30
                )
                response_text = response.json().get("response", "")
            
            return {
                "response_text": response_text.strip(),
                "tone": EMOTION_TONES.get(emotion, "professional"),
                "source_documents": documents[:2] if documents else [],
                "generation_method": f"llm_{self.llm_provider}"
            }
            
        except Exception as e:
            print(f"⚠️  LLM error: {e}")
            # Fallback to template
            return self._generate_template_response(query, documents, emotion)
    
    def _generate_handoff_response(self, emotion: str) -> Dict[str, Any]:
        """Generate response for human handoff."""
        prefix = EMOTION_PREFIXES.get(emotion, "")
        
        response_text = (
            f"{prefix}Je vais vous transférer à un conseiller qui pourra "
            "mieux vous aider. Merci de patienter un instant."
        )
        
        return {
            "response_text": response_text,
            "tone": EMOTION_TONES.get(emotion, "professional"),
            "source_documents": [],
            "generation_method": "template",
            "action": "human_handoff"
        }
    
    def _generate_crm_response(self, action_result: str, emotion: str) -> Dict[str, Any]:
        """Generate response for CRM actions."""
        prefix = EMOTION_PREFIXES.get(emotion, "")
        
        response_text = (
            f"{prefix}C'est fait ! {action_result} "
            "Y a-t-il autre chose que je puisse faire pour vous ?"
        )
        
        return {
            "response_text": response_text,
            "tone": EMOTION_TONES.get(emotion, "professional"),
            "source_documents": [],
            "generation_method": "template",
            "action": "crm_action"
        }


# ============================================================================
# 🧪 TEST
# ============================================================================

def test_response_builder():
    """Test the Response Builder."""
    print("\n" + "="*80)
    print("📝 RESPONSE BUILDER TEST")
    print("="*80)
    
    # Initialize (template mode, no LLM needed)
    builder = ResponseBuilder(use_llm=False)
    
    # Test cases
    test_cases = [
        {
            "query": "Comment accéder à mon espace client ?",
            "documents": [
                "Question: Comment modifier mes informations personnelles ?\n"
                "Réponse: La Banque Postale: Espace Client ou appel au 3639 "
                "ou rendez-vous en bureau de Poste (+ justificatif domicile)."
            ],
            "emotion": "neutral"
        },
        {
            "query": "J'ai eu un accident de la vie",
            "documents": [
                "Question: Comment déclarer un sinistre accident de la vie ?\n"
                "Réponse: Contactez le 3639 dans les 5 jours suivant l'accident. "
                "Documents nécessaires: certificat médical, déclaration sur l'honneur."
            ],
            "emotion": "stressed"
        },
        {
            "query": "Je veux parler à quelqu'un !",
            "documents": [],
            "emotion": "angry"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*60}")
        print(f"🧪 Test {i}")
        print(f"❓ Query: \"{test['query']}\"")
        print(f"😊 Emotion: {test['emotion']}")
        print(f"📚 Documents: {len(test['documents'])} found")
        print('─'*60)
        
        # Generate response
        result = builder.generate_response(
            query=test['query'],
            documents=test['documents'],
            emotion=test['emotion']
        )
        
        print(f"\n💬 Response:")
        print(f"   \"{result['response_text']}\"")
        print(f"\n🎭 Tone: {result['tone']}")
        print(f"⚙️  Method: {result['generation_method']}")
    
    # Test handoff
    print(f"\n{'─'*60}")
    print("🧪 Test Handoff")
    print('─'*60)
    
    handoff = builder.generate_response(
        query="",
        documents=[],
        emotion="angry",
        action_type="human_handoff"
    )
    print(f"💬 Response: \"{handoff['response_text']}\"")
    
    print("\n" + "="*80)
    print("✅ Tests complete!")


if __name__ == "__main__":
    test_response_builder()
