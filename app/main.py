if __name__ == "__main__":
    from core.entrypoint import run_ai_core
    from Callbot_julie_inputs.entrypoint.run import run_inputs
## part of MG

    inputs = run_inputs()  
    text = inputs["full_text"]
    emotion_bert = inputs["emotion_bert"]
    emotion_wav2vec = inputs["emotion_wav2vec"]
    audio_summary = inputs["audio_summary"]  


## Part of  RED

    decision = run_ai_core(text, audio_summary, emotion_bert, emotion_wav2vec)
    print("Decision:", decision)


## Other Parts