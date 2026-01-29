# 🏗️ Architecture Complète du Callbot Julie

## Vue d'Ensemble du Système

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CALLBOT JULIE - CNP ASSURANCES                      │
│                    Architecture Multi-Agents (Framework Agno)                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1 : ACQUISITION & PRÉTRAITEMENT                                      │
│  👤 Responsable: ABDELLAH                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                    📞 Appel Client (Audio Stream)
                                   │
                                   ▼
         ┌─────────────────────────────────────────────┐
         │   🎤 Speech-to-Text (Whisper + BERT)       │
         │   • Transcription vocale                    │
         │   • Nettoyage du texte                      │
         └──────────────┬──────────────────────────────┘
                        │
                        ├──► Text: "Je veux déclarer un accident"
                        │
         ┌──────────────▼──────────────────────────────┐
         │   • Détection d'émotion                     │
         │   • Score de confiance                      │
         └──────────────┬──────────────────────────────┘
                        │
                        └──► Emotion: "stressed", Confidence: 0.82
                        │
                        │
┌───────────────────────▼─────────────────────────────────────────────────────┐
│  LAYER 2 : INTELLIGENCE ARTIFICIELLE (CORE)                                 │
│  👤 Responsable: REDOUANE                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                        │
         ┌──────────────▼──────────────────────────────┐
         │   🧠 AI Core & Decision Maker              │
         │   • Compréhension de l'intention            │
         │   • Gestion du contexte dialogue            │
         │   • Analyse de l'urgence                    │
         └──────────────┬──────────────────────────────┘
                        │
                        └──► Intent: "declare_claim"
                             Urgency: "high"
                             Confidence: 0.91
                        │
                        │
┌───────────────────────▼─────────────────────────────────────────────────────┐
│  LAYER 3 : KNOWLEDGE & ACTIONS                                              │
│  👤 Responsables: HATIM + IBRAHIM                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                        │
         ┌──────────────┴──────────────┐
         │                             │
         ▼                             ▼
┌────────────────────┐      ┌────────────────────────┐
│  📚 Knowledge Base │      │  🔀 TOOL ROUTER        │
│  (RAG + FAISS)     │      │  (IBRAHIM)             │
│  👤 HATIM          │      │                        │
│                    │      │  Pattern: Router       │
│  • Recherche       │      │  respond_directly=True │
│    sémantique      │      │                        │
│  • Embeddings      │      │  Décision:             │
│  • Documents       │      │  • CRM Action          │
│    pertinents      │      │  • Human Handoff       │
└──────┬─────────────┘      │  • Auto Response       │
       │                    └──────┬──────┬──────────┘
       │                           │      │
       │                    ┌──────┘      └──────┐
       │                    ▼                     ▼
       │          ┌─────────────────┐   ┌──────────────────┐
       │          │  💼 CRM AGENT   │   │  🤝 HUMAN        │
       │          │  (IBRAHIM)      │   │  HANDOFF AGENT   │
       │          │                 │   │  (IBRAHIM)       │
       │          │  Tools:         │   │                  │
       │          │  • update_addr  │   │  Tools:          │
       │          │  • check_policy │   │  • create_ticket │
       │          │  • get_customer │   │  • estimate_wait │
       │          │  • update_pay   │   │  • transfer_agent│
       │          └─────────┬───────┘   └──────┬───────────┘
       │                    │                   │
       │                    └──────┬────────────┘
       │                           │
       │                           │
┌──────▼───────────────────────────▼───────────────────────────────────────────┐
│  LAYER 4 : RESPONSE GENERATION                                               │
│  👤 Responsable: IBRAHIM                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
         ┌─────────────────────────▼─────────────────────┐
         │   💬 RESPONSE BUILDER (Équipe Principale)     │
         │   Model: gpt-4o-min                               │
         │                                                │
         │   Membres: [Tools Router]                     │
         │                                                │
         │   • Génération de réponse contextuelle         │
         │   • Adaptation ton émotionnel                  │
         │   • Utilisation documents (RAG)                │
         │   • Délégation si nécessaire                   │
         │                                                │
         │   If emotion in [stressed, angry]:             │
         │     Tone = "empathetic" 💙                     │
         │   Else:                                        │
         │     Tone = "professional" 💼                   │
         └──────────────┬─────────────────────────────────┘
                        │
                        └──► Response Text (Fr-FR)
                             "Je comprends votre situation..."
                        │
                        │
┌───────────────────────▼─────────────────────────────────────────────────────┐
│  LAYER 5 : OUTPUT                                                            │
│  👤 Responsable: Audio Engineer                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                        │
         ┌──────────────▼──────────────────────────────┐
         │   🔊 Text-to-Speech (TTS)                  │
         │   • Synthèse vocale                         │
         │   • Voix naturelle                          │
         └──────────────┬──────────────────────────────┘
                        │
                        ▼
                  📞 Client (Audio)
                        │
                        │
┌───────────────────────▼─────────────────────────────────────────────────────┐
│  LAYER 6 : EXTERNAL SYSTEMS                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                        │
         ┌──────────────┴──────────────┐
         │                             │
         ▼                             ▼
┌────────────────────┐      ┌────────────────────────┐
│  🏢 CRM SYSTEM     │      │  👥 HUMAN QUEUE        │
│                    │      │                        │
│  • Customer DB     │      │  • Ticket System       │
│  • Policies        │      │  • Agent Assignment    │
│  • Claims          │      │  • Priority Queue      │
│  • Payments        │      │  • Escalation Rules    │
└────────────────────┘      └────────────────────────┘
```

---

## 📊 Flux de Données Détaillé

### Cas 1 : Appel Simple (Question Horaires)

```
Client: "Quels sont vos horaires ?"
   │
   ▼
[Speech-to-Text]
   │ text: "Quels sont vos horaires"
   ▼
[Emotion Analysis]
   │ emotion: "neutral", confidence: 0.95
   ▼
[AI Core]
   │ intent: "general_info", urgency: "low"
   ▼
[Knowledge Base] ─────► Documents: ["Horaires: 9h-18h"]
   │
   ▼
[Tool Router]
   │ decision: "automated_response"
   ▼
[Response Builder]
   │ tone: "professional"
   │ text: "Nos conseillers sont disponibles..."
   ▼
[TTS]
   │ audio: "Nos conseillers sont disponibles..."
   ▼
Client ✅
```

### Cas 2 : Sinistre Urgent (Escalade Humaine)

```
Client: "Accident grave, besoin d'aide immédiatement!"
   │
   ▼
[Speech-to-Text]
   │ text: "Accident grave, besoin d'aide"
   ▼
[Emotion Analysis]
   │ emotion: "stressed", confidence: 0.89
   ▼
[AI Core]
   │ intent: "declare_claim", urgency: "high"
   ▼
[Tool Router]
   │ decision: "human_handoff" ⚠️
   ▼
[Human Handoff Agent]
   │ action: create_escalation_ticket()
   │ ticket_id: "TICKET-ABC123"
   │ priority: "urgent"
   ▼
[Response Builder]
   │ tone: "empathetic" 💙
   │ text: "Je comprends votre situation. Je vous mets"
   │       "en relation avec un conseiller..."
   ▼
[TTS]
   │ audio: "Je comprends votre situation..."
   ▼
[Human Queue] ─────► Agent Assigned: "Marie Dubois"
   │
   ▼
Client ─────► Transfer to Human Agent ✅
```

### Cas 3 : Mise à Jour CRM

```
Client: "Je veux changer mon adresse"
   │
   ▼
[Speech-to-Text]
   │ text: "Je veux changer mon adresse"
   ▼
[Emotion Analysis]
   │ emotion: "neutral", confidence: 0.92
   ▼
[AI Core]
   │ intent: "update_info", urgency: "medium"
   ▼
[Tool Router]
   │ decision: "crm_action" 💼
   ▼
[CRM Agent]
   │ action: update_customer_address()
   │ customer_id: "C12345"
   │ success: true
   ▼
[Response Builder]
   │ tone: "professional"
   │ text: "Votre adresse a été mise à jour."
   ▼
[CRM System] ─────► Database Updated ✅
   │
   ▼
[TTS]
   │ audio: "Votre adresse a été mise à jour."
   ▼
Client ✅
```

---

## 🔗 Interfaces entre Composants

### Interface 1 : AI Core → Tool Router

```json
{
  "intent": "declare_claim",
  "urgency": "high",
  "confidence": 0.91,
  "emotion": "stressed",
  "text": "J'ai eu un accident",
  "conversation_context": [...],
  "customer_id": "C12345"
}
```

### Interface 2 : Knowledge Base → Response Builder

```json
{
  "documents": [
    {
      "title": "Procédure sinistre",
      "content": "Pour déclarer un sinistre...",
      "relevance_score": 0.95
    }
  ],
  "query": "declare accident",
  "total_results": 3
}
```

### Interface 3 : Tool Router → CRM Agent

```python
# Tool call automatique via Agno
update_customer_address(
    customer_id="C12345",
    new_address={
        "street": "123 Rue Example",
        "city": "Paris",
        "postal_code": "75001"
    }
)
```

### Interface 4 : Tool Router → Human Handoff

```python
# Tool call automatique via Agno
create_escalation_ticket(
    customer_id="C12345",
    intent="declare_claim",
    urgency="high",
    emotion="stressed",
    context="Client a eu un accident domestique grave",
    reason="high_urgency_claim"
)
```

### Interface 5 : Response Builder → TTS

```json
{
  "response_text": "Je comprends votre situation...",
  "tone": "empathetic",
  "language": "fr-FR",
  "confidence": 0.91
}
```

---

## 🎯 Responsabilités par Composant (IBRAHIM)

### Tool Router (src/routers/tools_router.py)

**Input** :
- Intent data from AI Core
- Emotion, urgency, confidence

**Processing** :
```python
if urgency == "high" or intent in ["declare_claim", "complaint"]:
    → Human Handoff Agent

elif intent in ["update_info", "check_status", "payment_info"]:
    → CRM Agent

else:
    → Automated Response
```

**Output** :
- Routing decision
- Delegated execution

### Response Builder (src/teams/response_builder.py)

**Input** :
- Intent data
- Knowledge documents
- Emotion

**Processing** :
```python
if emotion in ["stressed", "angry", "frustrated"]:
    tone = "empathetic"
    prefix = "Je comprends votre préoccupation..."
else:
    tone = "professional"
    prefix = ""

response = LLM.generate(context + documents)
```

**Output** :
- Response text (fr-FR)
- Tone indicator
- Confidence score

---

## 📈 Métriques de Performance

```
┌─────────────────────────────────────────────────────────┐
│  KPIs CIBLES                                            │
├─────────────────────────────────────────────────────────┤
│  • Automatisation:           90% des appels             │
│  • Temps de réponse:         < 3 secondes               │
│  • Précision routage:        > 95%                      │
│  • Satisfaction client:      > 4.5/5                    │
│  • Escalade appropriée:      < 10%                      │
│  • Disponibilité:            99.9%                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technologies

```
┌─────────────────────┬──────────────────────────────────┐
│  Composant          │  Technologies                    │
├─────────────────────┼──────────────────────────────────┤
│  Speech-to-Text     │  Whisper, BERT                   │
│  AI Core            │  Custom NLP                      │
│  Knowledge Base     │  FAISS, RAG, Embeddings          │
│  Tool Router        │  Agno Framework, Python          │
│  Response Builder   │  Agno Framework, gpt-4o-min          │
│  Agents             │  Agno Agents, Python Tools       │
│  API                │  FastAPI, Pydantic               │
│  TTS                │  Custom TTS Engine               │
└─────────────────────┴──────────────────────────────────┘
```

---

**Cette architecture garantit :**
- ✅ Modularité et évolutivité
- ✅ Séparation des responsabilités
- ✅ Résilience et monitoring
- ✅ Facilité de maintenance
