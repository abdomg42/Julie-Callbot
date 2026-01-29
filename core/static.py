# Static variables & base knowledge for AI Core.
# Keep this file "dumb": constants, regex lists, intent catalog.

ALLOWED_URGENCY = ("low", "med", "high")
ALLOWED_ACTION = ("rag_query", "escalate")

# Add/adjust intents here (10+ is fine).
# Keep IDs stable: frontend/backend will key off these strings.
INTENTS = (
    "greeting",
    "declare_claim",
    "check_status",
    "update_info",
    "complaint",
    "general_info",
    "payment_info",
    "cancel_policy",
    "unknown",
)

# Keywords français naturels (ASR + typos + speech recognition errors)
INTENT_KEYWORDS = {
    "greeting": [
        r"\b(bonjour|bonsoir|salut|hello|hi)\b",
        r"\b(je voudrais|j'aimerais|je souhaite)\s+(parler|discuter)",
        r"\b(allô|allo|oui)\s*$",
        r"^\s*(bonjour|bonsoir|salut|hello)\s*[.,!]*\s*$"
    ],
    "declare_claim": [
        r"\b(déclar|declar|signaler)\w*\s+(sinistre|accident|dommage|probl[eè]me)",
        r"\b(j'ai eu un|j'ai fait un|j'ai eu)\s+(accident|chute|brûlure|coupure)",
        r"\b(ouvrir|créer|enregistrer)\s+dossier",
        r"\b(déclarer|déclaration)\s+(sinistre|accident)",
        r"\b(je veux|je voudrais|j'aimerais)\s+(déclarer|signaler|annoncer)",
        r"\b(sinistre|accident|dommage)",
        r"\b(je viens pour|je téléphone pour)\s+(sinistre|accident)",
    ],
    "check_status": [
        r"\b(suivi|statut|état|avancement|o[ùu] en est)\s+(mon dossier|le dossier)",
        r"\b(numéro|num)\s+(dossier|réf|référence)",
        r"\b(quand|combien de temps|délai)\s+(r[ée]glement|indemnisation)",
        r"\b(o[ùu]r|où en est|quel est l'état)",
    ],
    "general_info": [
        r"\b(garantie|contrat|couverture|assurance|police)",
        r"\b(qu'est-ce qui est|est-ce que ça couvre)",
        r"\b(b[énée]ficiaire|qui est couvert)",
        r"\b(information|renseignement|question)",
        # Add fuzzy matching for CNP variations (speech recognition errors)
        r"\b(cnp|cmp|cmpa|cnpa|semp|cempe)\s+(assurance|séance|assistance)",
        r"\b(domaines?|activités?)\s+(de|du)\s+(cnp|cmp|cmpa|cnpa)",
        r"\b(quell?e?s?\s+sont\s+les?)\s+.*(cnp|cmp|cmpa|cnpa)",
        r"\b(informations?)\s+(sur|de)\s+(cnp|cmp|cmpa|cnpa)",
    ],
    "complaint": [
        r"\b(réclamation|mécontent|pas d'accord|refus[éeé])",
        r"\b(ça fait longtemps|pas reçu|pas normal)",
        r"\b(recours|contester|litige)",
        r"\b(en colère|furieux|énervé|scandalisé)",
        r"\b(service.*nul|mauvais service|horrible)",
        r"\b(ça ne va pas|pas acceptable|c'est inadmissible)",
    ],
    "unknown": [],
}
# Urgency rules (hybrid rule+ML design: rules are cheap and reliable).
URG_HIGH = [
    r"\burgent\b", r"\burgence\b", r"\bh[ôo]pital\b", r"\bambulance\b",
    r"\bperte de connaissance\b", r"\bsang\b", r"\bgrave\b", r"\bfracture\b",
    r"\bhospitalis[éeé]\b", r"\bchirurgie\b", r"\boperation\b",
    r"\bincapacité permanente\b", r"\bIPC\b", r"\bprothèse\b",
    r"\bamputation\b", r"\bsoins intensifs\b", r"\bcoma\b"
]

URG_MED = [
    r"\bdouleur\b", r"\bblessure\b", r"\bchute\b", r"\baccident\b",
    r"\barr[êe]t de travail\b", r"\btraumatisme\b",
    r"\bcoupure\b", r"\bbrûlure\b", r"\bcontusion\b",
    r"\belongation\b", r"\bentaillage\b", r"\bplaie\b",
    r"\bconsultation\b", r"\bmedecin\b", r"\bplatre\b"
]


# Default model names (override with env vars in prod)
# DEFAULT_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"  # 768-dim
DEFAULT_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_OLLAMA_MODEL = "llama3.2:1b-instruct"
