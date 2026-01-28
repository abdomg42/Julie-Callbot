from audio.recorder import AudioRecorder
from models.whisper import Whisper
from models.bert_sentiment import BertSentiment
from models.wav2vec_sentiment import Wav2VecSentiment
from pipeline.parallel_pipeline import ParallelPipeline

# Initialize
recorder = AudioRecorder()
whisper = Whisper()
bert = BertSentiment()
wav2vec = Wav2VecSentiment()
pipeline = ParallelPipeline(whisper, bert, wav2vec)

# Record until silence
audio = recorder.record_until_silence()

# Process in parallel
results = pipeline.process(audio)
print(results)
import torch 
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)
# print("TEXT:", results["text"])
# print("BERT SENTIMENT:", results["bert_sentiment"])
# print("WAV2VEC SENTIMENT:", results["wav2vec"]["audio_sentiment"])
# print("WAV2VEC AUDIO SIGNAL SHAPE:", results["wav2vec"]["audio_signal"].shape)

