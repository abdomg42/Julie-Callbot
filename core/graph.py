# LangGraph orchestration of the AI Core.
# Nodes: preprocess -> decide -> (optional feedback stub)

from typing import Any, Dict
from requests.exceptions import RequestException
from langgraph.graph import StateGraph, END

from .state import CoreState
from .decision_engine import decide_rules_only
from .prompts import decision_prompt
from .llm_ollama import OllamaDecisionLLM
from .static import DEFAULT_OLLAMA_MODEL

def node_preprocess(state: CoreState) -> CoreState:
    # Keep debug small + useful
    state.debug["text_len"] = len(state.full_text or "")
    state.debug["has_audio_summary"] = bool(state.audio_summary)
    state.debug["has_emotion_bert"] = bool(state.emotion_bert)
    # wav2vec removed
    return state


def node_decide_rules(state: CoreState) -> CoreState:
    # Deterministic fallback (fast)
    decision = decide_rules_only(state.full_text or "",
                                 emotion_bert=state.emotion_bert,
                                 audio_summary=state.audio_summary)
    state.decision = decision
    state.debug["mode"] = "rules_only"
    return state


def node_decide_with_llm(state: CoreState, llm: OllamaDecisionLLM) -> CoreState:
    # LLM is the primary decider: it must output the strict schema JSON
    prompt = decision_prompt(
        full_text=state.full_text,
        emotion_bert=state.emotion_bert,
        audio_summary=state.audio_summary,
    )

    try:
        decision = llm.decide_json(prompt)
        state.debug["mode"] = "ollama_llm"
    except RequestException as e:
        # If Ollama isn't running, fall back
        decision = decide_rules_only(state.full_text)
        state.debug["mode"] = "rules_fallback"
        state.debug["ollama_error"] = str(e)

    state.decision = decision
    return state


def node_feedback_stub(state: CoreState) -> CoreState:
    # Placeholder: store after-call rating later (no runtime cost now).
    state.debug["feedback_placeholder"] = {
        "store": {
            "decision": state.decision,
            "advisor_rating": None
        }
    }
    return state


def build_app(use_llm: bool = True, ollama_model: str = DEFAULT_OLLAMA_MODEL) -> Any:
    g = StateGraph(CoreState)
    g.add_node("preprocess", node_preprocess)

    if use_llm:
        llm = OllamaDecisionLLM(model=ollama_model)
        g.add_node("decide", lambda s: node_decide_with_llm(s, llm))
    else:
        g.add_node("decide", node_decide_rules)

    g.add_node("feedback", node_feedback_stub)

    g.set_entry_point("preprocess")
    g.add_edge("preprocess", "decide")
    g.add_edge("decide", "feedback")
    g.add_edge("feedback", END)

    return g.compile()