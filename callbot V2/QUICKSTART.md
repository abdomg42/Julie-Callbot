# 🚀 Guide de Démarrage Rapide - Callbot Julie

## 📋 Prérequis

- Python 3.9 ou supérieur
- Clé API OpenAI
- PowerShell (Windows)

---

## ⚡ Installation Rapide

### 1. Cloner/Ouvrir le Projet

```powershell
cd "c:\Users\IBRAHIM NASSIH\Documents\VSCode\callbot V1"
```

### 2. Créer l'Environnement Virtuel

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Si vous avez une erreur d'exécution de script, exécutez :
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Installer les Dépendances

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurer l'Environnement

Créez un fichier `.env` à la racine du projet :

```powershell
Copy-Item .env.example .env
```

Éditez `.env` et ajoutez votre clé API OpenAI :
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

---

## 🎯 Utilisation

### Option 1 : Script de Démonstration

Exécutez le script principal avec des cas de test :

```powershell
python src/main.py
```

Cela va tester :
- ✅ Sinistre urgent → Human Handoff
- ✅ Question simple → Réponse automatique
- ✅ Mise à jour CRM → CRM Agent
- ✅ Client mécontent → Ton empathique + Escalade

### Option 2 : API REST

Démarrez le serveur FastAPI :

```powershell
python src/api.py
```

Ou avec uvicorn :

```powershell
uvicorn src.api:app --reload --port 8000
```

Accédez à la documentation interactive :
- 🌐 **Swagger UI** : http://localhost:8000/docs
- 🌐 **ReDoc** : http://localhost:8000/redoc

### Option 3 : Tests Unitaires

Exécutez la suite de tests :

```powershell
pytest tests/ -v
```

Pour les tests avec couverture :

```powershell
pytest tests/ --cov=src --cov-report=html
```

---

## 📡 Exemple d'Appel API

### Génération de Réponse

**Endpoint** : `POST /api/generate-response`

```json
{
  "intent_data": {
    "intent": "declare_claim",
    "urgency": "high",
    "confidence": 0.91,
    "emotion": "stressed",
    "text": "J'ai eu un accident domestique grave",
    "conversation_context": [],
    "customer_id": "C12345"
  },
  "knowledge_data": {
    "documents": [
      {
        "title": "Procédure sinistre",
        "content": "Pour déclarer un sinistre...",
        "relevance_score": 0.95
      }
    ],
    "query": "accident domestique",
    "total_results": 1
  }
}
```

**Réponse attendue** :

```json
{
  "response_text": "Je comprends votre situation. Je vais immédiatement vous mettre en relation avec un conseiller...",
  "tone": "empathetic",
  "language": "fr-FR",
  "confidence": 0.91,
  "requires_followup": false
}
```

### Test de Routage

**Endpoint** : `POST /api/test-routing`

```json
{
  "intent": "update_info",
  "urgency": "medium",
  "confidence": 0.88,
  "emotion": "neutral",
  "text": "Je veux changer mon adresse",
  "customer_id": "C67890"
}
```

**Réponse** :

```json
{
  "action": "crm_action",
  "reason": "crm_data_operation",
  "intent": "update_info",
  "urgency": "medium",
  "emotion": "neutral"
}
```

---

## 🏗️ Architecture des Composants

```
Response Builder (équipe principale)
    │
    ├── Tools Router (sous-équipe)
    │       ├── CRM Agent
    │       │     ├── update_customer_address
    │       │     ├── check_policy_status
    │       │     ├── get_customer_info
    │       │     └── update_payment_method
    │       │
    │       └── Human Handoff Agent
    │             ├── create_escalation_ticket
    │             ├── estimate_wait_time
    │             ├── transfer_to_agent
    │             └── log_escalation_reason
```

---

## 🔧 Structure du Projet

```
callbot V1/
├── src/
│   ├── agents/
│   │   ├── crm_agent.py              # Agent CRM
│   │   └── human_handoff_agent.py    # Agent escalade
│   ├── routers/
│   │   └── tools_router.py           # Routeur vers agents
│   ├── teams/
│   │   └── response_builder.py       # Générateur de réponses
│   ├── schemas.py                     # Modèles de données
│   ├── api.py                        # API FastAPI
│   └── main.py                       # Script de démo
├── tests/
│   ├── test_tools_router.py
│   ├── test_response_builder.py
│   └── test_integration.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📊 Métriques Clés

Le système vise à atteindre :

- ✅ **90% d'automatisation** des appels répétitifs
- ✅ **Réponse immédiate** aux questions simples
- ✅ **Escalade intelligente** des cas complexes
- ✅ **Ton empathique** pour clients stressés

---

## 🐛 Dépannage

### Erreur : "Module 'agno' not found"

```powershell
pip install agno
```

### Erreur : "OpenAI API key not found"

Vérifiez que votre fichier `.env` contient :
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

### Erreur : Script execution policy

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📞 Points d'Intégration

Vos composants (Tool Router & Response Builder) s'intègrent avec :

### 🔼 En Amont (Input)
- **AI Core** (Redouane) : Fournit intent, emotion, urgency
- **Knowledge Base** (Hatim) : Fournit documents pertinents

### 🔽 En Aval (Output)
- **Text-to-Speech** : Reçoit response_text pour synthèse vocale
- **CRM System** : Reçoit les demandes de mise à jour
- **Human Queue** : Reçoit les tickets d'escalade

---

## ✅ Checklist de Validation

- [ ] Installation complète sans erreur
- [ ] Variables d'environnement configurées
- [ ] Script de démo fonctionne
- [ ] API démarre sans erreur
- [ ] Tests passent (pytest)
- [ ] Documentation accessible (Swagger)

---

## 🎓 Prochaines Étapes

1. **Phase 1** : Tester avec des cas réels
2. **Phase 2** : Intégrer avec les composants upstream (Redouane, Hatim)
3. **Phase 3** : Connecter au vrai CRM
4. **Phase 4** : Déploiement et monitoring

**Bon développement ! 🚀**
