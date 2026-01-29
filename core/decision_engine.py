from typing import Dict, Any
from .rules import score_urgency, keyword_intent_prior
from .schema import validate_decision_schema

def decide_rules_only(full_text: str,
                      emotion_bert: Dict[str, Any] = None,
                      audio_summary: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Rules-only fallback router (no retrieval).
    Uses full_text as the primary signal.
    Optionally uses emotion/audio_summary as light overrides for urgency/confidence.
    """
    full_text = (full_text or "").strip()
    emotion_bert = emotion_bert or {}
    audio_summary = audio_summary or {}

    # 1) Urgency from text
    urgency = score_urgency(full_text)

    # 2) Intent prior from text
    intent, strength = keyword_intent_prior(full_text)
    if not intent:
        intent = "unknown"

    # 3) Confidence heuristic (fallback only)
    conf = 0.60 + 0.35 * float(strength)
    
    # Special handling for greetings and common intents
    if intent == "greeting":
        conf = max(0.85, conf)  # High confidence for greetings
    elif intent == "unknown":
        conf -= 0.25  # Penalty for unknown

    # 4) Cheap audio quality penalty (if audio is bad, lower confidence)
    # (These keys come from your audio_summary)
    silence_ratio = float(audio_summary.get("silence_ratio", 0.0) or 0.0)
    clipping_ratio = float(audio_summary.get("clipping_ratio", 0.0) or 0.0)
    if silence_ratio > 0.60:
        conf -= 0.15
    if clipping_ratio > 0.05:
        conf -= 0.10

    conf = max(0.0, min(1.0, conf))

    # 5) Action routing - more nuanced logic (less aggressive escalation)
    if urgency == "high":
        action = "escalate"  # Only true emergencies
    elif intent == "complaint" and conf < 0.30:  # Only very unclear complaints
        action = "escalate"
    elif intent == "unknown" and conf < 0.25:  # Only very unclear unknowns
        action = "escalate"
    elif intent in ("greeting", "general_info", "declare_claim", "check_status", "update_info", "payment_info"):
        action = "rag_query"  # Always try RAG for these
    elif conf < 0.20:  # Much lower threshold - only completely unclear text
        action = "escalate"
    else:
        action = "rag_query"  # Default to RAG, not escalation

    out = {"intent": intent, "urgency": urgency, "action": action, "confidence": round(conf, 3)}
    validate_decision_schema(out)
    return out
