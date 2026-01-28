import torch
from transformers import pipeline

# on peut utiliser un autre modèle (tblard/tf-allocine)
class BertSentiment:
    def __init__(self, model_id="cmarkea/distilcamembert-base-sentiment"): 
        device = 0 if torch.cuda.is_available() else -1
        self.pipe = pipeline("sentiment-analysis", model=model_id, device=device)
    
    def analyze(self, text):
        result = self.pipe(text)[0]

        label = result["label"]      # e.g. "4 stars"
        score = result["score"]

        stars = int(label[0])        # "4 stars" -> 4

        if stars <= 2:
            sentiment = "NEGATIVE"
        elif stars == 3:
            sentiment = "NEUTRAL"
        else:
            sentiment = "POSITIVE"

        return {
            "sentiment": sentiment,
            "score": score
        }