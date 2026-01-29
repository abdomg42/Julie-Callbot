from audio.recorder import AudioRecorder
from models.whisper import Whisper
from models.bert_sentiment import BertSentiment
from models.wav2vec_sentiment import Wav2VecSentiment
from pipeline.parallel_pipeline import ParallelPipeline
import time


start_total = time.time()

# Initialize
start_init = time.time()
recorder = AudioRecorder()
whisper = Whisper()
bert = BertSentiment()
wav2vec = Wav2VecSentiment()
pipeline = ParallelPipeline(whisper, bert, wav2vec)
print(f"Init time: {time.time() - start_init:.2f}s")

# Record until silence
start_record = time.time()
audio = recorder.record_until_silence()
print(f"Record time: {time.time() - start_record:.2f}s")


# Process in parallel
start_process = time.time()
results = pipeline.process(audio)
print(f"Process time: {time.time() - start_process:.2f}s")
print(f"Total time: {time.time() - start_total:.2f}s")

print("=== RESULTS ===")
print(results)
# print("TEXT:", results["full_text"])
# print("BERT SENTIMENT:", results["bert_sentiment"])
# print("WAV2VEC SENTIMENT:", results["wav2vec"]["audio_sentiment"])
# print("WAV2VEC AUDIO SIGNAL SHAPE:", results["wav2vec"]["audio_signal"].shape)

