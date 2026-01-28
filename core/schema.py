# Strict schema validation for the Figma JSON output.
# Stdlib only to keep it light + portable.

from typing import Dict, Any
from .static import ALLOWED_URGENCY, ALLOWED_ACTION

REQUIRED_KEYS = ("intent", "urgency", "action", "confidence")

def validate_decision_schema(obj: Dict[str, Any]) -> None:
    if not isinstance(obj, dict):
        raise ValueError("Decision must be a dict.")

    keys = tuple(obj.keys())
    if set(keys) != set(REQUIRED_KEYS) or len(keys) != 4:
        raise ValueError(f"Decision must have EXACT keys {REQUIRED_KEYS}, got {keys}")

    if not isinstance(obj["intent"], str) or not obj["intent"]:
        raise ValueError("intent must be a non-empty string.")

    if obj["urgency"] not in ALLOWED_URGENCY:
        raise ValueError(f"urgency must be one of {ALLOWED_URGENCY}.")

    if obj["action"] not in ALLOWED_ACTION:
        raise ValueError(f"action must be one of {ALLOWED_ACTION}.")

    conf = obj["confidence"]
    if not isinstance(conf, (int, float)):
        raise ValueError("confidence must be a number.")
    conf = float(conf)
    if conf < 0.0 or conf > 1.0:
        raise ValueError("confidence must be in [0.0, 1.0].")
