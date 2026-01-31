"""AI Core entrypoint."""

from typing import Dict, Any
import os
from core.graph import build_app
from core.state import CoreState

USE_LLM = os.environ.get("CALLBOT_USE_LLM", "false").lower() == "true"
_APP = build_app(use_llm=USE_LLM)


def run_ai_core(full_text: str, emotion_bert: dict, audio_summary: dict) -> Dict[str, Any]:
    """Run AI decision engine."""
    state = CoreState(
        full_text=full_text,
        emotion_bert=emotion_bert,
        audio_summary=audio_summary
    )
    out = _APP.invoke(state)
    return out["decision"]


