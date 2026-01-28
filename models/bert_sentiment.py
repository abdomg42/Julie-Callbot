from transformers import pipeline
class BertSentiment:
    def __init__(self, model_id="cmarkea/distilcamembert-base-sentiment"): 
        self.pipe = pipeline("sentiment-analysis", model=model_id)
    
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
            "raw_label": label,
            "raw_score": score,
            "sentiment": sentiment
        }
