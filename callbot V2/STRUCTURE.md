# 📂 Structure du Projet Callbot V1

**Dernière mise à jour:** 24 janvier 2026  
**Version:** 1.0 avec PostgreSQL unifié

---

## 📋 Vue d'ensemble

Projet Callbot multi-agents avec base de données PostgreSQL unifiée (table unique).

```
callbot V1/
├── src/                           # Code source principal
│   ├── __init__.py
│   ├── api.py                     # API FastAPI (optionnel)
│   ├── main.py                    # Point d'entrée principal
│   ├── schemas.py                 # Schémas Pydantic
│   ├── agents/                    # Agents intelligents
│   │   ├── __init__.py
│   │   ├── crm_agent.py          # Agent CRM (4 outils)
│   │   └── human_handoff_agent.py # Agent escalade humaine
│   ├── database/                  # Couche base de données
│   │   ├── __init__.py
│   │   └── db_service.py         # Service PostgreSQL unifié
│   ├── routers/                   # Routeurs de requêtes
│   │   ├── __init__.py
│   │   └── tools_router.py       # Routeur CRM/Handoff
│   └── teams/                     # Équipes d'agents
│       ├── __init__.py
│       └── response_builder.py   # Générateur de réponses
│
├── tests/                         # Tests unitaires
│   ├── __init__.py
│   ├── test_integration.py
│   ├── test_response_builder.py
│   └── test_tools_router.py
│
├── .env                           # Variables d'environnement
├── .gitignore                     # Fichiers à ignorer
├── requirements.txt               # Dépendances Python
├── pyproject.toml                 # Configuration projet Python
├── setup.ps1                      # Script d'installation PowerShell
│
├── database_schema_simple.sql     # ⭐ Schéma PostgreSQL (table unique)
├── test_db_connection.py          # ⭐ Test connexion BDD (7 tests)
├── demo_database_only.py          # ⭐ Démo sans OpenAI
├── demo_with_database.py          # ⭐ Démo complète avec agents
├── view_database.py               # ⭐ Visualisation données BDD
│
├── README.md                      # Documentation principale
├── QUICKSTART.md                  # Guide démarrage rapide
├── ARCHITECTURE.md                # Architecture technique
├── IBRAHIM_GUIDE.md               # Guide personnalisé
├── DATABASE_README.md             # Documentation base de données
└── DATABASE_QUICKSTART.md         # Guide rapide BDD
```

---

## 🎯 Fichiers clés (⭐ à connaître)

### **Scripts de démonstration**
| Fichier | Description | Dépendances |
|---------|-------------|-------------|
| `demo_database_only.py` | Test BDD sans OpenAI | PostgreSQL uniquement |
| `demo_with_database.py` | Démo complète avec agents | OpenAI + PostgreSQL |
| `view_database.py` | Visualisation données | PostgreSQL uniquement |
| `test_db_connection.py` | Test CRUD complet (7 tests) | PostgreSQL uniquement |

### **Base de données**
| Fichier | Description |
|---------|-------------|
| `database_schema_simple.sql` | Schéma PostgreSQL avec 1 table unifiée (36 colonnes) |
| `src/database/db_service.py` | Service Python pour toutes les opérations CRUD |

### **Agents intelligents**
| Fichier | Description |
|---------|-------------|
| `src/agents/crm_agent.py` | Agent CRM avec 4 outils (update_address, check_policy, get_customer_info, update_payment_method) |
| `src/agents/human_handoff_agent.py` | Agent d'escalade vers humain (2 outils) |
| `src/routers/tools_router.py` | Routeur qui distribue les requêtes aux agents |
| `src/teams/response_builder.py` | Générateur de réponses finales |

---

## 🗄️ Architecture base de données

### **PostgreSQL 18.1**
- **Base:** `callbot_db`
- **Port:** 5432
- **User:** `callbot_user`
- **Password:** 212002

### **Table unique: `callbot_interactions`**
- **36 colonnes** regroupant toutes les données
- **Colonnes JSONB:** `conversation_history`, `action_result`, `crm_action_details`, `metadata`
- **Auto-génération:** `interaction_id`, `created_at`, `updated_at`
- **Format ID:** `INT-YYYY-XXXXXXXX`

### **3 vues SQL:**
- `v_active_interactions` - Interactions en cours
- `v_pending_handoffs` - Escalades en attente
- `v_daily_stats` - Statistiques quotidiennes

---

## 🚀 Commandes essentielles

### **Installation**
```powershell
# Installation complète
.\setup.ps1

# Ou manuel
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### **Configuration**
```powershell
# Créer .env avec:
DATABASE_URL=postgresql://callbot_user:212002@localhost:5432/callbot_db
OPENAI_API_KEY=votre_clé_ici
USE_MOCK_DB=false
```

### **Initialisation base de données**
```powershell
# Dans pgAdmin ou psql, exécuter:
psql -U postgres -d callbot_db -f database_schema_simple.sql
```

### **Tests et démonstrations**
```powershell
# Test connexion BDD (7 tests CRUD)
python test_db_connection.py

# Démo sans OpenAI (gratuit)
python demo_database_only.py

# Visualisation données
python view_database.py

# Démo complète avec agents (nécessite crédits OpenAI)
python demo_with_database.py
```

---

## 📊 Statistiques projet

- **Lignes de code:** ~2500 lignes Python
- **Agents:** 2 (CRM + Handoff)
- **Outils disponibles:** 6 (4 CRM + 2 Handoff)
- **Tables BDD:** 1 table unifiée + 3 vues
- **Scripts de test:** 4 fichiers
- **Documentation:** 6 fichiers Markdown

---

## 🧹 Fichiers supprimés (nettoyage)

### **Dossier `data/` (obsolète avec PostgreSQL)**
- ❌ `conversations.json`
- ❌ `crm_actions.json`
- ❌ `handoff_tickets.json`
- ❌ `interactions.json`
- ❌ `responses.json`

### **Documentation redondante**
- ❌ `CHANGES_SUMMARY.md`
- ❌ `CHEATSHEET.md`
- ❌ `VISUAL_SUMMARY.txt`
- ❌ `PROJECT_SUMMARY.md`

### **Ancien démo**
- ❌ `demo.py` (remplacé par `demo_with_database.py`)

---

## 🔧 Technologies utilisées

| Technologie | Version | Usage |
|-------------|---------|-------|
| Python | 3.12.0 | Langage principal |
| PostgreSQL | 18.1 | Base de données |
| psycopg2-binary | 2.9.9+ | Driver PostgreSQL |
| Agno Framework | latest | Framework multi-agents |
| OpenAI | gpt-4o-mini | Modèle LLM |
| FastAPI | latest | API REST (optionnel) |

---

## 📝 Notes importantes

1. **Architecture simplifiée:** Passage de 8 tables à 1 table unifiée pour faciliter la maintenance
2. **Agents Agno:** Format modèle `openai:gpt-4o-mini` (pas `gpt-4o-mini`)
3. **Paramètre obsolète:** `show_tool_calls` retiré de tous les agents
4. **Session ID auto-généré:** Format `SESSION-YYYYMMDD-XXXXXXXX`
5. **Tests sans OpenAI:** Utiliser `demo_database_only.py` pour tester gratuitement

---

## 📚 Documentation

- **Démarrage rapide:** `QUICKSTART.md`
- **Architecture:** `ARCHITECTURE.md`
- **Guide personnalisé:** `IBRAHIM_GUIDE.md`
- **Base de données:** `DATABASE_README.md`
- **Schéma BDD:** `DATABASE_QUICKSTART.md`

---

**Projet nettoyé et optimisé le 24 janvier 2026** ✅
