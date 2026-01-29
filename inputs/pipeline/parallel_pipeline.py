import threading

try:
    from ..models.audio_summary import compute_audio_summary
except ImportError:
    from models.audio_summary import compute_audio_summary

class ParallelPipeline:
    def __init__(self, whisper, bert, sample_rate_hz: int = 16000):
        self.whisper = whisper
        self.bert = bert
        self.sr = sample_rate_hz

    def process(self, audio):
        results = {}
        lock = threading.Lock()

        def text_path():
            text = self.whisper.transcribe(audio)
            bert_out = self.bert.analyze(text)
            with lock:
                results["full_text"] = text
                results["emotion_bert"] = bert_out


        def audio_summary_path():
            summary = compute_audio_summary(audio, sr=self.sr)
            with lock:
                results["audio_summary"] = summary

        t1 = threading.Thread(target=text_path)
        t2 = threading.Thread(target=audio_summary_path)

        t1.start(); t2.start()
        t1.join();  t2.join()

        return results
