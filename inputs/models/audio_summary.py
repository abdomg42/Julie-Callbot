import numpy as np

def compute_audio_summary(audio_np: np.ndarray, sr: int = 16000, zones: int = 4,
                                  frame_ms: int = 25, hop_ms: int = 10,
                                  spike_z: float = 2.5, silence_rms: float = 0.01) -> dict:
    if audio_np is None or audio_np.size == 0:
        return {
            "sample_rate_hz": sr,
            "duration_ms": 0,
            "num_zones": zones,
            "global_peak_zone": 0,
            "global_peak_zscore": 0.0,
            "peak_zscore_by_zone": [0.0] * zones,
            "spike_count_by_zone": [0] * zones,
            "silence_ratio": 1.0,
            "clipping_ratio": 0.0,
        }

    # normalize waveform [-1,1]
    x = audio_np.astype(np.float32) / 32768.0
    duration_ms = int(round(1000.0 * len(x) / sr))

    # clipping ratio (saturation)
    clipping_ratio = float(np.mean(np.abs(audio_np) >= 32760))

    # RMS envelope
    frame = max(1, int(sr * frame_ms / 1000))
    hop = max(1, int(sr * hop_ms / 1000))

    if len(x) < frame:
        rms = np.array([float(np.sqrt(np.mean(x * x) + 1e-12))], dtype=np.float32)
    else:
        n_frames = 1 + (len(x) - frame) // hop
        rms = np.empty(n_frames, dtype=np.float32)
        for i in range(n_frames):
            w = x[i * hop : i * hop + frame]
            rms[i] = float(np.sqrt(np.mean(w * w) + 1e-12))

    silence_ratio = float(np.mean(rms < silence_rms))

    # z-score energy (spikes)
    mu = float(rms.mean())
    sd = float(rms.std() + 1e-8)
    z = (rms - mu) / sd

    # per-zone
    n = len(z)
    peak_zscore_by_zone = []
    spike_count_by_zone = []

    for zi in range(zones):
        a = int(zi * n / zones)
        b = int((zi + 1) * n / zones)
        seg = z[a:b] if b > a else z[a:a+1]

        peak_zscore_by_zone.append(round(float(seg.max()), 2))
        spike_count_by_zone.append(int(np.sum(seg > spike_z)))

    # global peak
    peak_idx = int(np.argmax(z))
    global_peak_zone = min(zones - 1, int(peak_idx * zones / max(1, n)))
    global_peak_zscore = round(float(z[peak_idx]), 2)

    return {
        "sample_rate_hz": sr,
        "duration_ms": duration_ms,
        "num_zones": zones,
        "global_peak_zone": global_peak_zone,
        "global_peak_zscore": global_peak_zscore,
        "peak_zscore_by_zone": peak_zscore_by_zone,
        "spike_count_by_zone": spike_count_by_zone,
        "silence_ratio": round(silence_ratio, 3),
        "clipping_ratio": round(clipping_ratio, 3),
    }
