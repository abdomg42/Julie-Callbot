import threading
import webrtcvad
import sounddevice as sd
import numpy as np
from typing import Callable


class BargeInController:
    """Detect incoming speech and call a callback when detected."""
    def __init__(self, callback_on_speech: Callable, sample_rate: int = 16000, frame_ms: int = 30, aggressiveness: int = 2):
        self.cb = callback_on_speech
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.frame_size = int(sample_rate * frame_ms / 1000)
        self.vad = webrtcvad.Vad(aggressiveness)
        self._stop = threading.Event()
        self._thread = None

    def _read_loop(self):
        try:
            with sd.RawInputStream(samplerate=self.sample_rate, blocksize=self.frame_size, dtype='int16', channels=1) as stream:
                while not self._stop.is_set():
                    data = stream.read(self.frame_size)[0]
                    if data is None:
                        continue
                    pcm = data.tobytes()
                    if len(pcm) < 1:
                        continue
                    try:
                        if self.vad.is_speech(pcm, self.sample_rate):
                            # Detected speech — call callback and stop
                            try:
                                self.cb()
                            except Exception:
                                pass
                            return
                    except Exception:
                        # Ignore VAD errors and continue
                        continue
        except Exception:
            # Device errors should not crash caller
            return

    def start(self):
        self._stop.clear()
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)


class StoppablePlayer:
    """Play raw PCM (int16) numpy array and allow stopping."""
    def __init__(self, audio_np: np.ndarray, sample_rate: int = 16000):
        # audio_np expected int16 numpy 1D
        self.audio = audio_np
        self.sr = sample_rate
        self._pos = 0
        self._stop = threading.Event()
        self.stream = None

    def _callback(self, outdata, frames, time_info, status):
        if self._stop.is_set():
            raise sd.CallbackStop()
        start = self._pos
        end = start + frames
        chunk = self.audio[start:end]
        if len(chunk) < frames:
            chunk = np.pad(chunk, (0, frames - len(chunk)), mode='constant')
            self._stop.set()
        outdata[:] = chunk.reshape(-1, 1)
        self._pos = end

    def play(self):
        self._pos = 0
        self._stop.clear()
        self.stream = sd.OutputStream(samplerate=self.sr, channels=1, dtype='int16', callback=self._callback)
        self.stream.start()

    def stop(self):
        self._stop.set()
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
