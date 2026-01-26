import torch
from transformers import Wav2Vec2Processor, Wav2Vec2ForSequenceClassification

class Wav2VecSentiment:
    def __init__(self, model_id="Lajavaness/wav2vec2-lg-xlsr-fr-speech-emotion-recognition"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = Wav2Vec2Processor.from_pretrained(model_id)
        self.model = Wav2Vec2ForSequenceClassification.from_pretrained(model_id)
        self.model.to(self.device)

    def analyze(self, audio, sr=16000):
        inputs = self.processor(
            audio,
            sampling_rate=sr,
            return_tensors="pt",
            padding=True
        ).to(self.device)

        with torch.no_grad():
            logits = self.model(**inputs).logits

        predicted = torch.argmax(logits, dim=-1).item()
        return {"audio_sentiment_class": predicted}
