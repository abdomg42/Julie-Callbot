from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class CoreState:
    full_text: str
    emotion_bert: Dict[str, Any]
    emotion_wav2vec: Dict[str, Any]
    audio_summary: Dict[str, Any]
    decision: Optional[Dict[str, Any]] = None                     # strict schema decision JSON
    debug: Dict[str, Any] = field(default_factory=dict)           # traces for tests/demo
