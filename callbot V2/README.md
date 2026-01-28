# 🤖 Callbot Julie V2 - CNP Assurances

<div align="center">

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![RAG](https://img.shields.io/badge/RAG-FAISS-orange.svg)
![TTS](https://img.shields.io/badge/TTS-Coqui-purple.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Callbot IA avec RAG, Smart Routing et TTS pour gérer les appels liés aux sinistres "accidents de la vie" chez CNP Assurances**

</div>

---

## 📋 Table des Matières

- [À Propos](#-à-propos)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Composants](#-composants)
- [Tests](#-tests)
- [Documentation API](#-documentation-api)
- [Développement](#-développement)

---

## 🎯 À Propos

### Contexte Métier

CNP Assurances recevait un volume très élevé d'appels liés aux sinistres "accidents de la vie". Une grande partie de ces appels étaient répétitifs (questions simples, demandes d'information), saturant les conseillers et réduisant leur disponibilité pour les dossiers complexes.

### Solution

Mise en place d'un **callbot basé sur l'IA conversationnelle** avec :
- 🔍 **RAG (Retrieval-Augmented Generation)** : Recherche sémantique dans la base de connaissances
- 🔀 **Smart Router** : Routage intelligent basé sur la confiance et les mots-clés
- 📝 **Response Builder** : Génération de réponses adaptées au contexte/émotion
- 🔊 **TTS (Text-to-Speech)** : Synthèse vocale avec Coqui TTS
- 🤝 **Human Handoff** : Escalade vers conseillers pour cas complexes

### Résultats Visés

- ✅ **90% du flux d'appels répétitifs** absorbés par l'IA
- ✅ **Temps de réponse < 2 secondes** (RAG ~100ms, Response ~800ms, TTS ~500ms)
- ✅ **100% offline** après téléchargement initial des modèles
- ✅ **Amélioration de la satisfaction client** grâce à une prise en charge immédiate

---

## 🏗️ Architecture

### Vue d'Ensemble V2

```
┌─────────────────────────────────────────────────────────────────┐
│                    📞 SYSTÈME TÉLÉPHONIQUE (AMI)                │
│         Speech-to-Text → Texte + Émotion → [CALLBOT V2]        │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    🎯 ORCHESTRATOR (Main Pipeline)               │
│                      src/services/orchestrator.py               │
│  1. Reçoit requête (texte + émotion + session)                  │
│  2. Route via Smart Router                                       │
│  3. Génère réponse via Response Builder                         │
│  4. Convertit en audio via TTS                                  │
│  5. Retourne réponse complète                                   │
└────────────────────────────────┬────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
┌───────────────┐      ┌─────────────────┐      ┌───────────────┐
│ 🔀 SMART      │      │ 📝 RESPONSE     │      │ 🔊 TTS        │
│    ROUTER     │      │    BUILDER      │      │    SERVICE    │
│               │      │                 │      │               │
│ • Confidence  │      │ • Templates     │      │ • Coqui TTS   │
│ • Keywords    │      │ • LLM (option)  │      │ • Cache MP3   │
│ • Off-topic   │      │ • Emotion adapt │      │ • Base64 out  │
└───────┬───────┘      └────────┬────────┘      └───────────────┘
        │                       │
        ▼                       │
┌───────────────┐               │
│ 🔍 RAG        │◄──────────────┘
│ Knowledge Base│
│               │
│ • FAISS index │
│ • 471MB model │
│ • Embedding   │
│   cache       │
└───────────────┘
        │
        ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃              ROUTING DECISION                     ┃
┗━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┛
               │                 │
        ┌──────┴──────┐   ┌──────┴──────┐
        ▼             ▼   ▼             ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ rag_response  │ │ human_handoff │ │  crm_action   │
│               │ │               │ │               │
│ Score > 0.5   │ │ • Urgent      │ │ • Update info │
│ Question      │ │ • Complex     │ │ • Paiement    │
│ simple        │ │ • Off-topic   │ │ • Consultation│
└───────────────┘ └───────────────┘ └───────────────┘
```

### Flux de Données

```
📥 INPUT (from AMI):
{
  "text": "Comment faire un rachat sur mon contrat ?",
  "emotion": "neutral",
  "confidence": 0.82,
  "session_id": "call_12345"
}

📤 OUTPUT (to AMI):
{
  "action": "rag_response",
  "response_text": "Pour faire un rachat, connectez-vous...",
  "audio_base64": "UklGRi4AAABXQVZFZm10...",
  "confidence": 0.89,
  "next_step": "continue_conversation"
}
```

### Composants - 👤 IBRAHIM

#### 1️⃣ RAG Knowledge Base (`RAG/rag_api.py`)

**Rôle** : Recherche sémantique dans la base de connaissances assurance

**Caractéristiques** :
- 🔍 FAISS pour recherche vectorielle rapide
- 📦 Modèle HuggingFace multilingue (471MB, téléchargé une seule fois)
- 💾 Cache des embeddings pour réponses instantanées
- 🔒 100% local et sécurisé (pas d'API externe)

**Input** :
```python
rag.search("Comment faire un rachat ?", k=3)
```

**Output** :
```json
{
  "documents": [
    {"content": "Pour faire un rachat...", "relevance_score": 0.89}
  ],
  "query_time_ms": 45
}
```

#### 2️⃣ Smart Router (`RAG/smart_router.py`)

**Rôle** : Décide si la requête doit aller vers RAG, Human Handoff ou CRM

**Logique de Routage** :
| Condition | Action |
|-----------|--------|
| Mots-clés urgents (urgent, réclamation, litige) | `human_handoff` |
| Question off-topic (quantique, spatial) | `human_handoff` |
| Score RAG > 0.5 | `rag_response` |
| Score RAG < 0.3 | `human_handoff` |

**Input** :
```python
router.route_query("J'ai un problème urgent")
```

**Output** :
```json
{
  "action": "human_handoff",
  "reason": "urgent_keyword",
  "confidence": 0.0
}
```

#### 3️⃣ Response Builder (`src/services/response_builder.py`)

**Rôle** : Génère des réponses naturelles adaptées au contexte et à l'émotion

**Modes** :
- **Template** : Réponses pré-définies (rapide, pas d'API)
- **LLM** : Génération via OpenAI/Ollama (plus naturel)

**Adaptation émotionnelle** :
| Émotion | Ton |
|---------|-----|
| `stressed` | Empathique : "Je comprends que cette situation..." |
| `angry` | Apaisant : "Je comprends votre frustration..." |
| `neutral` | Professionnel : Direct et efficace |

#### 4️⃣ TTS Service (`src/services/tts_service.py`)

**Rôle** : Convertit le texte en audio pour le système téléphonique

**Caractéristiques** :
- 🔊 Coqui TTS (gratuit, local, privé)
- 🇫🇷 Voix française naturelle
- 💾 Cache MP3 pour éviter régénération
- 📤 Sortie Base64 pour transmission API

#### 5️⃣ Orchestrator (`src/services/orchestrator.py`)

**Rôle** : Coordonne tous les composants dans un pipeline unifié

**Pipeline** :
```
Request → Smart Router → RAG/Handoff → Response Builder → TTS → Response
```

**Performance** :
- RAG : ~100ms
- Response : ~800ms  
- TTS : ~500ms
- **Total : < 2 secondes**

#### 6️⃣ API FastAPI (`src/api.py`)

**Endpoints** :
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/process` | Pipeline complet (texte → audio) |
| POST | `/api/rag/query` | Recherche RAG directe |
| POST | `/api/tts/generate` | Génération TTS directe |
| GET | `/health` | Health check |
| GET | `/api/stats` | Statistiques système |

---

## 🚀 Installation

### Prérequis

- Python 3.12 ou supérieur
- ~2GB d'espace disque (modèles ML)
- PowerShell (Windows)

### Installation Automatique

```powershell
# Cloner et accéder au projet
cd "c:\Users\IBRAHIM NASSIH\Documents\VSCode\callbot V2"

# Exécuter le script de setup
.\setup.ps1
```

### Installation Manuelle

```powershell
# Installer les dépendances principales
pip install -r requirements.txt

# Installer les dépendances RAG
pip install -r RAG/requirement.txt

# Installer torch (IMPORTANT - ~113MB)
pip install torch --timeout 600

# Installer sentence-transformers
pip install sentence-transformers

# (Optionnel) Installer Coqui TTS pour synthèse vocale
pip install coqui-tts
```

### Premier Lancement (Téléchargement Modèles)

```powershell
# Le premier lancement télécharge le modèle HuggingFace (471MB)
# Après cela, tout fonctionne offline !
python -c "from RAG.rag_api import RAGKnowledgeBase; RAGKnowledgeBase()"
```

---

## 💻 Utilisation

### 1. Test Rapide de l'Orchestrator

```powershell
# Test complet sans TTS (rapide)
python -c "from src.services.orchestrator import test_orchestrator; test_orchestrator()"
```

**Résultat attendu** :
```
✅ Action: rag_response
� Response: "Pour accéder à votre espace client..."
📊 Confidence: 0.85
⏱️  Total time: 150ms
```

### 2. Test du RAG seul

```powershell
python -c "from RAG.rag_api import RAGKnowledgeBase; rag = RAGKnowledgeBase(); print(rag.search('rachat'))"
```

### 3. Test du Smart Router

```powershell
python RAG/smart_router.py
```

### 4. API REST

Démarrez le serveur :

```powershell
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Accédez à la documentation :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### 5. Appel API Exemple

```bash
curl -X POST "http://localhost:8000/api/process" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Comment faire un rachat ?",
    "emotion": "neutral",
    "session_id": "call_001"
  }'
```

**Réponse** :
```json
{
  "action": "rag_response",
  "response_text": "Pour faire un rachat sur votre contrat...",
  "audio_base64": "UklGRi4AAABXQVZFZm10...",
  "confidence": 0.89,
  "next_step": "continue_conversation"
}
```

---

## 🔧 Composants Détaillés

### RAG Knowledge Base

**Fichiers** :
- `RAG/rag_api.py` : API principale
- `RAG/data/kb.jsonl` : Base de connaissances (Q&A)
- `RAG/faiss_index/` : Index vectoriel
- `RAG/embedding_cache/` : Cache des embeddings

**Méthodes** :
```python
rag = RAGKnowledgeBase()
rag.search(query, k=3)           # Recherche simple
rag.search_with_metadata(query)  # Avec scores et metadata
rag.get_stats()                  # Statistiques
```

### Smart Router

**Fichiers** :
- `RAG/smart_router.py` : Logique de routage

**Mots-clés de handoff** :
- Urgents : `urgent`, `immédiat`, `critique`
- Complexes : `réclamation`, `litige`, `plainte`, `avocat`
- Off-topic : `quantique`, `spatial`, `pizza`

### Response Builder

**Fichiers** :
- `src/services/response_builder.py` : Générateur de réponses

**Templates par action** :
- `rag_response` : Réponse basée sur documents
- `human_handoff` : Message de transfert
- `crm_action` : Confirmation d'action

### TTS Service

**Fichiers** :
- `src/services/tts_service.py` : Service TTS
- `cache/tts_cache/` : Cache audio

**Configuration** :
- Voix : Française
- Format : MP3/WAV 16kHz
- Vitesse : 0.9x (clarté téléphonique)

### Orchestrator

**Fichiers** :
- `src/services/orchestrator.py` : Pipeline principal

**Options** :
```python
orchestrator = CallbotOrchestrator(
    enable_tts=True,      # Activer TTS
    enable_llm=False,     # Utiliser templates (pas de LLM)
    llm_provider="ollama" # ou "openai"
)
```

---

## 🧪 Tests

### Exécuter tous les tests

```powershell
pytest tests/ -v
```

### Tests par composant

```powershell
# RAG Knowledge Base
python RAG/test.py

# Smart Router
python RAG/smart_router.py

# Orchestrator complet
python -c "from src.services.orchestrator import test_orchestrator; test_orchestrator()"

# Avec TTS (si installé)
python -c "from src.services.orchestrator import demo_with_tts; demo_with_tts()"
```

### Scénarios de Test

| Scénario | Query | Émotion | Résultat Attendu |
|----------|-------|---------|------------------|
| Simple | "Comment accéder à mon espace ?" | neutral | `rag_response` |
| Urgent | "Problème urgent avec mon contrat" | angry | `human_handoff` |
| Off-topic | "Comment créer un portail quantique ?" | neutral | `human_handoff` |
| Stressé | "Déclarer un accident" | stressed | `rag_response` + ton empathique |

---

## 📡 Documentation API

### POST /api/process

**Pipeline complet** : texte → routing → response → TTS → audio

**Request** :
```json
{
  "text": "Comment faire un rachat sur mon contrat ?",
  "emotion": "neutral",
  "session_id": "call_12345",
  "conversation_history": []
}
```

**Response** :
```json
{
  "action": "rag_response",
  "response_text": "Pour faire un rachat, connectez-vous à votre espace...",
  "audio_base64": "UklGRi4AAABXQVZFZm10...",
  "confidence": 0.89,
  "next_step": "continue_conversation",
  "documents_used": ["Q: Comment faire un rachat..."],
  "metadata": {
    "tone": "professional",
    "total_response_time_ms": 1250.5,
    "tts_cached": false
  }
}
```

### POST /api/rag/query

**Recherche RAG directe** (sans génération de réponse)

**Request** :
```json
{
  "query": "espace client",
  "k": 3
}
```

**Response** :
```json
{
  "documents": [
    {"content": "Pour accéder...", "relevance_score": 0.92}
  ],
  "query_time_ms": 45
}
```

### POST /api/tts/generate

**Génération TTS directe**

**Request** :
```json
{
  "text": "Bonjour, je suis Julie",
  "emotion": "neutral"
}
```

**Response** :
```json
{
  "audio_base64": "UklGRi4AAABXQVZFZm10...",
  "generation_time_ms": 450,
  "cached": false
}
```

### GET /health

**Health check**

**Response** :
```json
{
  "status": "healthy",
  "components": {
    "rag": true,
    "router": true,
    "tts": true
  }
}
```

### GET /api/stats

**Statistiques système**

**Response** :
```json
{
  "total_requests": 150,
  "rag_responses": 120,
  "human_handoffs": 25,
  "crm_actions": 5,
  "avg_response_time_ms": 1100.5
}
```

---

## 👨‍💻 Développement

### Structure du Projet V2

```
callbot V2/
├── 📁 RAG/                           # Système RAG
│   ├── rag_api.py                   # Knowledge Base API
│   ├── smart_router.py              # Smart Query Router
│   ├── build_index.py               # Construction index FAISS
│   ├── data/
│   │   └── kb.jsonl                 # Base de connaissances
│   ├── faiss_index/                 # Index vectoriel
│   ├── embedding_cache/             # Cache embeddings
│   └── model_cache/                 # Cache modèle HuggingFace
│
├── 📁 src/                           # Code source principal
│   ├── api.py                       # FastAPI REST API
│   ├── main.py                      # Point d'entrée
│   ├── schemas.py                   # Modèles Pydantic
│   │
│   ├── 📁 services/                  # Services métier
│   │   ├── orchestrator.py          # 🎯 Pipeline principal
│   │   ├── response_builder.py      # Génération réponses
│   │   └── tts_service.py           # Synthèse vocale
│   │
│   ├── 📁 agents/                    # Agents spécialisés
│   │   ├── crm_agent.py             # Agent CRM
│   │   └── human_handoff_agent.py   # Agent escalade
│   │
│   └── 📁 routers/                   # Routeurs FastAPI
│       └── tools_router.py
│
├── 📁 cache/                         # Caches
│   └── tts_cache/                   # Cache audio TTS
│
├── 📁 tests/                         # Tests unitaires
│   ├── test_integration.py
│   ├── test_response_builder.py
│   └── test_tools_router.py
│
├── requirements.txt                  # Dépendances Python
├── setup.ps1                        # Script installation
├── README.md                        # Ce fichier
└── QUICKSTART.md                    # Guide démarrage rapide
```

### Technologies

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **RAG** | FAISS + HuggingFace | Recherche sémantique |
| **Embeddings** | sentence-transformers | Vectorisation texte |
| **Modèle** | paraphrase-multilingual-MiniLM-L12-v2 | Embedding multilingue |
| **TTS** | Coqui TTS | Synthèse vocale locale |
| **API** | FastAPI | REST API |
| **Validation** | Pydantic | Schémas de données |
| **Tests** | Pytest | Tests unitaires |

### Dépendances Principales

```
torch>=2.0.0           # Deep learning
sentence-transformers  # Embeddings
faiss-cpu             # Vector search
langchain-huggingface # LangChain integration
fastapi               # REST API
coqui-tts             # Text-to-Speech (optionnel)
```

### Points d'Intégration avec AMI

**Système Téléphonique (AMI)** :
```
Téléphone → Speech-to-Text → [AMI: Analyse émotion] → 
            ↓
      {text, emotion, session_id}
            ↓
      [CALLBOT V2: Orchestrator]
            ↓
      {response_text, audio_base64, action}
            ↓
      [AMI: Play audio] → Téléphone
```

**Responsabilités** :
- **AMI** : STT, analyse émotion, lecture audio, gestion appel
- **Callbot V2** : RAG, routing, génération réponse, TTS

---

## ⚠️ Troubleshooting

### Erreur "sentence-transformers not found"

```powershell
pip install sentence-transformers
pip install torch --timeout 600  # Peut prendre du temps (~113MB)
```

### Téléchargement modèle lent

Le modèle HuggingFace (471MB) est téléchargé au premier lancement. Après cela, tout fonctionne offline grâce au cache :
- Windows : `C:\Users\<USER>\.cache\huggingface\hub\`

### TTS ne fonctionne pas

Coqui TTS nécessite torch. Si l'installation échoue :
1. Désactivez TTS : `enable_tts=False`
2. Le système fonctionne en mode texte seul

### Performance lente

1. Vérifiez que les caches sont utilisés :
   - `RAG/embedding_cache/` pour les embeddings
   - `cache/tts_cache/` pour l'audio
2. Le premier appel est toujours plus lent (chargement modèle)

---

## 📄 License

MIT License - Voir LICENSE pour plus de détails

---

## 👥 Équipe

**Développé par** : IBRAHIM NASSIH  
**Projet** : Callbot Julie V2 - CNP Assurances  
**Date** : Janvier 2026  
**Version** : 2.0.0

---

<div align="center">

**📚 Documentation complémentaire**

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Guide démarrage rapide |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architecture détaillée |
| [DATABASE_README.md](DATABASE_README.md) | Documentation base de données |

</div>
