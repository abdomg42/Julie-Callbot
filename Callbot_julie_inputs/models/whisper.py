import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

class Whisper:
    def __init__(self, model_id="openai/whisper-small"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id)
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model.to(self.device)

    def transcribe(self, audio, sr=16000):
        inputs = self.processor(
            audio,
            sampling_rate=sr,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            ids = self.model.generate(**inputs)

        return self.processor.batch_decode(ids, skip_special_tokens=True)[0]
