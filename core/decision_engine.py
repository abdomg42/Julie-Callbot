\"\"\"Rules-based decision engine.\"\"\"

from typing import Dict, Any
from .rules import score_urgency, keyword_intent_prior
from .schema import validate_decision_schema


def decide_rules_only(full_text: str,
                      emotion_bert: Dict[str, Any] = None,
                      audio_summary: Dict[str, Any] = None) -> Dict[str, Any]:
    \"\"\"Rules-only fallback router.\"\"\"
    full_text = (full_text or "").strip()
    emotion_bert = emotion_bert or {}
    audio_summary = audio_summary or {}

    urgency = score_urgency(full_text)
    intent, strength = keyword_intent_prior(full_text)
    if not intent:
        intent = "unknown"

    conf = 0.60 + 0.35 * float(strength)
    
    if intent == "greeting":
        conf = max(0.85, conf)
    elif intent == "unknown":
        conf -= 0.25

    silence_ratio = float(audio_summary.get("silence_ratio", 0.0) or 0.0)
    clipping_ratio = float(audio_summary.get("clipping_ratio", 0.0) or 0.0)
    if silence_ratio > 0.60:
        conf -= 0.15
    if clipping_ratio > 0.05:
        conf -= 0.10

    conf = max(0.0, min(1.0, conf))

    if urgency == "high":
        action = "escalate"
    elif intent == "complaint" and conf < 0.30:
        action = "escalate"
    elif intent == "unknown" and conf < 0.25:
        action = "escalate"
    elif intent in ("greeting", "general_info", "declare_claim", "check_status", "update_info", "payment_info"):
        action = "rag_query"
    elif conf < 0.20:
        action = "escalate"
    else:
        action = "rag_query"

    out = {"intent": intent, "urgency": urgency, "action": action, "confidence": round(conf, 3)}
    validate_decision_schema(out)
    return out
