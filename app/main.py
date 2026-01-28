
from core.entrypoint import run_ai_core
from Callbot_julie_inputs.entrypoint.run import run_inputs
from callbot_V2.entrypoint.entrypoint import callbot_global_response



if __name__ == "__main__":
  # part of MG
  inputs = run_inputs()
  text = inputs["full_text"]
  emotion_bert = inputs["emotion_bert"]
  emotion_wav2vec = inputs["emotion_wav2vec"]
  audio_summary = inputs["audio_summary"]

  # Part of RED
  decision = run_ai_core(text, audio_summary, emotion_bert, emotion_wav2vec)

  """
  decision = {
    "intent": "<un des intents>",
    "urgency": "<low|med|high>",
    "action": "<rag_query|escalate>",
    "confidence": <float entre 0.0 et 1.0>,
  }
  """

  # Conversation history management
  conversation_history = []

  # Example: append the first user message
  conversation_history.append({"role": "user", "text": text})

  # Call the callbot and get the response

  #############  what is an orchestrator? #############
  orchestrator = None  # Optionally reuse or pass an orchestrator

  response = callbot_global_response(
    text=text,
    ######   here i dont kow how can i pass all the args ######
    emotion="emotion" + emotion_bert + 
            " emotion 2" + emotion_wav2vec + 
            " urgent " + decision["urgency"] +
            " action " + decision["action"] + 
            " intention " + decision["intent"],
    #### plz check the fuction if we need to change more ######
    confidence=decision.get("confidence", 0.0),
    session_id="session_123",
    conversation_history=conversation_history,
    orchestrator=orchestrator
  )

  # Append the bot's response to the conversation history
  if hasattr(response, 'response_text'):
    conversation_history.append({"role": "bot", "text": response.response_text})
  elif isinstance(response, dict) and "response_text" in response:
    conversation_history.append({"role": "bot", "text": response["response_text"]})
 
 ######################## WE NEED TO DO SOMETHING WITH THE RESPONSE ########################
########################## WE NEED TO LOOP THIS FOR A FULL CONVERSATION ##########################