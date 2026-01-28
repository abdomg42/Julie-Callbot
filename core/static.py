# Static variables & base knowledge for AI Core.
# Keep this file "dumb": constants, regex lists, intent catalog.

ALLOWED_URGENCY = ("low", "med", "high")
ALLOWED_ACTION = ("rag_query", "escalate")

# Add/adjust intents here (10+ is fine).
# Keep IDs stable: frontend/backend will key off these strings.
INTENTS = (
    "declaration_sinistre",    # Déclaration sinistre (FNOL - 60% des appels)
    "suivi_dossier",           # Suivi dossier (25% des appels)
    "documents_medicaux",      # Pièces justificatives
    "indemnisation",           # Règlement/virement
    "infos_contrat",           # Contrat/garanties
    "reclamation",             # Litige
    "transfert_humain",        # Escalade conseiller
    "inconnu",                 # Fallback
)

# Keywords français naturels (ASR + typos)
INTENT_KEYWORDS = {
    "declaration_sinistre": [
        r"\b(déclar|declar|signaler)\w*\s+(sinistre|accident|dommage|probl[eè]me)",
        r"\b(j'ai eu un|j'ai fait un|j'ai eu)\s+(accident|chute|brûlure|coupure)",
        r"\b(ouvrir|créer|enregistrer)\s+dossier",
        r"\b(déclarer|déclaration)\s+(sinistre|accident)",
        r"\b(je viens pour|je téléphone pour)\s+(sinistre|accident)",
    ],
    "suivi_dossier": [
        r"\b(suivi|statut|état|avancement|o[ùu] en est)\s+(mon dossier|le dossier)",
        r"\b(numéro|num)\s+(dossier|réf|référence)",
        r"\b(quand|combien de temps|délai)\s+(r[ée]glement|indemnisation)",
        r"\b(o[ùu]r|où en est|quel est l'état)",
    ],
    "documents_medicaux": [
        r"\b(certificat|feuille|arrêt)\s+(médical|médecin|travail)",
        r"\b(facture|rapport|compte rendu)\s+m[ée]dical",
        r"\b(quels|quelle)\s+(pi[èe]ce|document|papier)",
        r"\b(j'ai envoy[éeé]|je dois envoyer)",
    ],
    "indemnisation": [
        r"\b(indemnisation|r[ée]glement|virement|argent|paiement)",
        r"\b(quand|combien|date)\s+(je vais recevoir|versement)",
        r"\b(rib|iban|récupérer|mon argent)",
    ],
    "infos_contrat": [
        r"\b(garantie|contrat|couverture|assurance|police)",
        r"\b(qu'est-ce qui est|est-ce que ça couvre)",
        r"\b(b[énée]ficiaire|qui est couvert)",
    ],
    "reclamation": [
        r"\b(réclamation|mécontent|pas d'accord|refus[éeé])",
        r"\b(ça fait longtemps|pas reçu|pas normal)",
        r"\b(recours|contester|litige)",
    ],
    "transfert_humain": [
        r"\b(conseiller|humain|opérateur|personne)",
        r"\b(j'veux parler à|transférer)",
    ],
    "inconnu": [],
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
DEFAULT_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"  # 768-dim
DEFAULT_OLLAMA_MODEL = "llama3.2:1b-instruct"
