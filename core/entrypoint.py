from typing import Dict, Any
import os
from core.graph import build_app
from core.state import CoreState

# ⚡ PERFORMANCE OPTIMIZATION
# Use rules-only by default (instant, <5ms) unless LLM is explicitly requested
# LLM adds 500ms-2s latency and requires Ollama server
USE_LLM = os.environ.get("CALLBOT_USE_LLM", "false").lower() == "true"

_APP = build_app(use_llm=USE_LLM)

# Debug mode output
if USE_LLM:
    print("🧠 AI Core: LLM mode (requires Ollama)")
else:
    print("⚡ AI Core: Rules mode (instant, no LLM)")


def run_ai_core(full_text: str, emotion_bert: dict, audio_summary: dict) -> Dict[str, Any]:
    """
    Run AI decision engine.
    
    Performance:
    - Rules mode: <5ms (default, recommended for production)
    - LLM mode: 500ms-2s (better accuracy, requires Ollama)
    """
    state = CoreState(
        full_text=full_text,
        emotion_bert=emotion_bert,
        audio_summary=audio_summary
    )
    out = _APP.invoke(state)
    return out["decision"]


