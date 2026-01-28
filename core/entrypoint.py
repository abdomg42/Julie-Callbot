from typing import Dict, Any
from core.graph import build_app
from core.state import CoreState

_APP = build_app(use_llm=True)

def run_ai_core(full_text: str, emotion_bert: dict, emotion_wav2vec: dict, audio_summary: dict) -> Dict[str, Any]:
    if hasattr(vector_embedding, "tolist"):
        vector_embedding = vector_embedding.tolist()

    state = CoreState(
        full_text=full_text,
        emotion_bert=emotion_bert,
        emotion_wav2vec=emotion_wav2vec,
        audio_summary=audio_summary
    )
    out = _APP.invoke(state)      
    return out["decision"]


