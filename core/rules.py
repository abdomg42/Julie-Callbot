# Cheap rules that improve latency and stability.
# These rules act as a fallback + signal for the LLM (or can be used alone).

from typing import Tuple, List, Dict, Any
import re
from .static import INTENT_KEYWORDS, URG_HIGH, URG_MED

def score_urgency(text: str) -> str:
    t = text.lower()
    if any(re.search(p, t) for p in URG_HIGH):
        return "high"
    if any(re.search(p, t) for p in URG_MED):
        return "med"
    return "low"

def keyword_intent_prior(text: str, debug: bool = False) -> Tuple[str, float]:
    """Return (intent, strength 0..1) based on keyword hits."""
    t = text.lower().strip()
    best_intent, best_hits = "unknown", 0
    
    for intent, kws in INTENT_KEYWORDS.items():
        hits = 0
        for kw in kws:
            if re.search(kw, t):
                hits += 1
                if debug:
                    print(f"   🔍 [DEBUG] Match: '{intent}' pattern '{kw}'")
        
        if hits > best_hits:
            best_intent, best_hits = intent, hits
            
    strength = min(1.0, best_hits / 3.0) if best_hits > 0 else 0.0
    
    if debug:
        print(f"   🔍 [DEBUG] Result: intent='{best_intent}', strength={strength:.2f}")
    
    return best_intent, strength
