import sounddevice as sd
import webrtcvad
import numpy as np
import queue
import time

class AudioRecorder:
    def __init__(self, sample_rate=16000, frame_ms=30, silence_limit=0.9, vad_aggressiveness=2):
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.frame_size = int(sample_rate * frame_ms / 1000)
        self.silence_limit = silence_limit
        self.vad = webrtcvad.Vad(vad_aggressiveness)
        self.audio_queue = queue.Queue()

    def audio_callback(self, indata, frames, time_info, status):
        self.audio_queue.put(bytes(indata))

    def is_speech(self, frame):
        return self.vad.is_speech(frame, self.sample_rate)

    def record_until_silence(self):
        frames = []
        silence_start = None
        # Message optimisé - système audio prêt immédiatement
        print("🎤 Écoute active - Je vous écoute")

        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.frame_size,
            dtype="int16",
            channels=1,
            callback=self.audio_callback
        ):
            while True:
                frame = self.audio_queue.get()
                frames.append(frame)

                if self.is_speech(frame):
                    silence_start = None
                else:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > self.silence_limit:
                        print("🛑 Silence detected")
                        break

        audio_bytes = b"".join(frames)
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
        audio_float32 = audio_np.astype(np.float32) / 32768.0
        return audio_float32
