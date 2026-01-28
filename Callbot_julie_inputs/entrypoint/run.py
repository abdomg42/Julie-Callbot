from audio.recorder import AudioRecorder
from models.whisper import Whisper
from models.bert_sentiment import BertSentiment
from models.wav2vec_sentiment import Wav2VecSentiment
from pipeline.parallel_pipeline import ParallelPipeline



def run_inputs():

    recorder = AudioRecorder()
    whisper = Whisper()
    bert = BertSentiment()
    wav2vec = Wav2VecSentiment()
    pipeline = ParallelPipeline(whisper, bert, wav2vec)

    # Record until silence
    audio = recorder.record_until_silence()

    # Process in parallel
    results = pipeline.process(audio)
    return results
    