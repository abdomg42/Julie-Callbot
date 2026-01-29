
from ..src.services.orchestrator import CallbotOrchestrator, CallbotRequest

def callbot_global_response(
	text,
	emotion_bert=None,
	intent="unknown",
	urgency="low",
	action="rag_query",
	confidence=0.0,
	session_id="",
	conversation_history=None,
	orchestrator=None,
	enable_tts=True,
	enable_llm=False
):
	"""
	Global function to process input through Callbot V2 pipeline.
	Args:
		text (str): User input text
		emotion_bert (dict): BERT emotion analysis result
		intent (str): Detected intent from AI Core
		urgency (str): Urgency level (low/med/high)
		action (str): Action to take (rag_query/escalate)
		confidence (float): Confidence score
		session_id (str): Session identifier
		conversation_history (list): List of previous conversation turns
		orchestrator (CallbotOrchestrator): Optional, pass an orchestrator instance
		enable_tts (bool): Enable text-to-speech
		enable_llm (bool): Enable LLM for response generation
	Returns:
		CallbotResponse: Structured response with text, audio, action, etc.
	"""
	if orchestrator is None:
		orchestrator = CallbotOrchestrator(enable_tts=enable_tts, enable_llm=enable_llm)
	
	# Extract emotion label from emotion_bert for backward compatibility
	emotion = "neutral"
	if emotion_bert:
		emotion = emotion_bert.get("sentiment", "neutral").lower()

	req = CallbotRequest(
		text=text,
		emotion=emotion,
		confidence=confidence,
		session_id=session_id,
		conversation_history=conversation_history or []
	)
	return orchestrator.process(req)


def get_orchestrator(enable_tts=True, enable_llm=False):
	"""
	Create and return a reusable orchestrator instance.
	Args:
		enable_tts (bool): Enable text-to-speech
		enable_llm (bool): Enable LLM for response generation
	Returns:
		CallbotOrchestrator: Initialized orchestrator
	"""
	return CallbotOrchestrator(enable_tts=enable_tts, enable_llm=enable_llm)


def play_audio_response(response, blocking: bool = True):
	"""
	Play audio response with optimized non-blocking option.
	
	Args:
		response: CallbotResponse object with audio_base64 field
		blocking: If False, plays in background thread (default: True for compatibility)
	"""
	import base64
	import tempfile
	import os
	import threading
	
	if not response.audio_base64:
		print("⚠️  Pas d'audio à jouer")
		return
	
	def _play_audio():
		try:
			import pygame
			
			# Initialize pygame mixer only once
			if not pygame.mixer.get_init():
				pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
			
			# Decode and save to temp file
			audio_bytes = base64.b64decode(response.audio_base64)
			with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
				tmp_file.write(audio_bytes)
				tmp_path = tmp_file.name
			
			# Load and play
			pygame.mixer.music.load(tmp_path)
			pygame.mixer.music.play()
			
			# Wait for playback only if blocking
			if blocking:
				while pygame.mixer.music.get_busy():
					pygame.time.Clock().tick(10)
				# Clean up after playback
				try:
					os.remove(tmp_path)
				except:
					pass
			else:
				# Schedule cleanup after estimated duration
				def cleanup():
					import time
					time.sleep(5)  # Wait for audio to finish
					try:
						os.remove(tmp_path)
					except:
						pass
				threading.Thread(target=cleanup, daemon=True).start()
				
		except ImportError:
			print("🔊 Audio généré - pygame non installé")
		except Exception as e:
			print(f"⚠️  Erreur lecture audio: {e}")
	
	if blocking:
		_play_audio()
	else:
		# Non-blocking: play in background thread
		thread = threading.Thread(target=_play_audio, daemon=True)
		thread.start()
