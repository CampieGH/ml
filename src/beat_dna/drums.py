from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import librosa
import numpy as np

DrumLabel = Literal["bass", "kick", "snare", "hat", "unknown"]


@dataclass(frozen=True)
class DrumEvent:
    time_seconds: float
    label: DrumLabel
    confidence: float
    low_ratio: float
    mid_ratio: float
    high_ratio: float
    spectral_centroid_hz: float


def _band_ratio(power: np.ndarray, frequencies: np.ndarray, low: float, high: float) -> float:
    mask = (frequencies >= low) & (frequencies < high)
    total = float(np.sum(power)) + 1e-12
    return float(np.sum(power[mask]) / total)


def classify_transient(segment: np.ndarray, sample_rate: int) -> DrumEvent:
    """Classify one short transient using spectral heuristics.

    This is deliberately a baseline classifier, not a trained neural model.
    It separates low-frequency bass/kick energy from noisy mid/high-frequency
    snare and hat energy well enough to bootstrap labelled data later.
    """
    if segment.size == 0 or np.max(np.abs(segment)) < 1e-8:
        return DrumEvent(0.0, "unknown", 0.0, 0.0, 0.0, 0.0, 0.0)

    windowed = segment.astype(float) * np.hanning(segment.size)
    spectrum = np.fft.rfft(windowed)
    power = np.abs(spectrum) ** 2
    frequencies = np.fft.rfftfreq(segment.size, d=1.0 / sample_rate)

    low_ratio = _band_ratio(power, frequencies, 20.0, 180.0)
    mid_ratio = _band_ratio(power, frequencies, 180.0, 2500.0)
    high_ratio = _band_ratio(power, frequencies, 2500.0, sample_rate / 2)
    centroid = float(librosa.feature.spectral_centroid(y=segment, sr=sample_rate)[0, 0])

    if low_ratio >= 0.72 and centroid < 220:
        label: DrumLabel = "bass"
        confidence = min(1.0, low_ratio)
    elif low_ratio >= 0.48 and centroid < 900:
        label = "kick"
        confidence = min(1.0, 0.55 + low_ratio / 2)
    elif high_ratio >= 0.52 and centroid >= 4500:
        label = "hat"
        confidence = min(1.0, high_ratio)
    elif mid_ratio + high_ratio >= 0.62 and centroid >= 1200:
        label = "snare"
        confidence = min(1.0, 0.45 + (mid_ratio + high_ratio) / 2)
    else:
        label = "unknown"
        confidence = 0.25

    return DrumEvent(
        time_seconds=0.0,
        label=label,
        confidence=float(confidence),
        low_ratio=low_ratio,
        mid_ratio=mid_ratio,
        high_ratio=high_ratio,
        spectral_centroid_hz=centroid,
    )


def extract_drum_events(
    audio: np.ndarray,
    sample_rate: int,
    onset_times: list[float],
    window_seconds: float = 0.12,
) -> list[DrumEvent]:
    window_samples = max(128, int(round(window_seconds * sample_rate)))
    events: list[DrumEvent] = []

    for onset_time in onset_times:
        start = max(0, int(round(onset_time * sample_rate)))
        end = min(audio.size, start + window_samples)
        result = classify_transient(audio[start:end], sample_rate)
        events.append(
            DrumEvent(
                time_seconds=float(onset_time),
                label=result.label,
                confidence=result.confidence,
                low_ratio=result.low_ratio,
                mid_ratio=result.mid_ratio,
                high_ratio=result.high_ratio,
                spectral_centroid_hz=result.spectral_centroid_hz,
            )
        )

    return events
