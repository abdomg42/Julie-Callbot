from transformers import pipeline

# on peut utiliser un autre modèle plus rapide (cmarkea/distilcamembert-base-sentiment)
class BertSentiment:
    def __init__(self, model_id="tblard/tf-allocine"): 
        self.pipe = pipeline("sentiment-analysis", model=model_id)

    def analyze(self, text):
        return self.pipe(text)[0]
