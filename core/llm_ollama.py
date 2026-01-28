# Ollama client for decision JSON generation.
# Uses short prompts, strict JSON parsing, and one repair attempt.

from typing import Dict, Any, Optional
import json
import requests
from .schema import validate_decision_schema

class OllamaDecisionLLM:
    def __init__(self, model: str, base_url: str = "http://localhost:11434", timeout_s: float = 5):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s

    def _generate(self, prompt: str, max_tokens: int = 120) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.1,  # stable JSON
                "top_p": 0.9,
            }
        }
        r = requests.post(url, json=payload, timeout=self.timeout_s)
        r.raise_for_status()
        return r.json().get("response", "")

    def decide_json(self, prompt: str) -> Dict[str, Any]:
        # Attempt 1
        txt = self._generate(prompt)
        obj = self._try_parse(txt)
        if obj is not None:
            validate_decision_schema(obj)
            return obj

        # Repair attempt (keep it short)
        repair_prompt = (
            "Corrige la sortie suivante pour qu'elle soit UNIQUEMENT un JSON valide "
            "avec EXACTEMENT les clés intent, urgency, action, confidence, et rien d'autre.\n"
            f"SORTIE À CORRIGER:\n{txt}\nJSON:"
        )
        txt2 = self._generate(repair_prompt, max_tokens=140)
        obj2 = self._try_parse(txt2)
        if obj2 is None:
            raise ValueError("LLM output is not parseable JSON after repair.")
        validate_decision_schema(obj2)
        return obj2

    @staticmethod
    def _try_parse(text: str) -> Optional[Dict[str, Any]]:
        # Strip common wrappers
        t = text.strip()
        # If model printed extra text, try to extract the first {...} block.
        if not (t.startswith("{") and t.endswith("}")):
            start = t.find("{")
            end = t.rfind("}")
            if start != -1 and end != -1 and end > start:
                t = t[start:end+1]
        try:
            return json.loads(t)
        except Exception:
            return None
