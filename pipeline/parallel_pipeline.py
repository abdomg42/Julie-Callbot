import threading

class ParallelPipeline:
    def __init__(self, whisper, bert, wav2vec):
        self.whisper = whisper
        self.bert = bert
        self.wav2vec = wav2vec

    def process(self, audio):
        results = {}

        def text_path():
            text = self.whisper.transcribe(audio)
            results["text"] = text
            results["bert_sentiment"] = self.bert.analyze(text)

        def audio_path():
            results["wav2vec_sentiment"] = self.wav2vec.analyze(audio)

        t1 = threading.Thread(target=text_path)
        t2 = threading.Thread(target=audio_path)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        return results