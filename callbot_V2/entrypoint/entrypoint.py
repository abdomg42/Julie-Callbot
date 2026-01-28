
from src.services.orchestrator import CallbotOrchestrator, CallbotRequest

def callbot_global_response(
	text,
	emotion="neutral",
	confidence=0.0,
	session_id="",
	conversation_history=None,
	orchestrator=None
):
	"""
	Global function to process input through Callbot V2 pipeline.
	Args:
		text (str): User input text
		emotion (str): Detected emotion (default: neutral)
		confidence (float): Confidence score (default: 0.0)
		session_id (str): Session identifier (default: empty)
		conversation_history (list): List of previous conversation turns (default: empty)
		orchestrator (CallbotOrchestrator): Optional, pass an orchestrator instance
	Returns:
		CallbotResponse: Structured response with text, audio, action, etc.
	"""
	if orchestrator is None:
		orchestrator = CallbotOrchestrator(enable_tts=True, enable_llm=False)
	req = CallbotRequest(
		text=text,
		emotion=emotion,
		confidence=confidence,
		session_id=session_id,
		conversation_history=conversation_history or []
	)
	return orchestrator.process(req)
