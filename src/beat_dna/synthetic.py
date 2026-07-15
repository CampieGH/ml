from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf


@dataclass(frozen=True)
class SyntheticBeatSpec:
    bpm: float = 140.0
    bars: int = 16
    beats_per_bar: int = 4
    sample_rate: int = 22050

    @property
    def beat_seconds(self) -> float:
        return 60.0 / self.bpm

    @property
    def duration_seconds(self) -> float:
        return self.bars * self.beats_per_bar * self.beat_seconds


def _add_click(audio: np.ndarray, start: int, amplitude: float, length: int = 256) -> None:
    end = min(start + length, audio.size)
    if end <= start:
        return
    window = np.hanning(end - start)
    audio[start:end] += amplitude * window


def generate_synthetic_beat(path: Path, spec: SyntheticBeatSpec = SyntheticBeatSpec()) -> Path:
    """Generate a deterministic beat with clearly contrasting four-bar sections.

    Sparse sections use quieter quarter-note pulses. Dense sections use louder
    quarter-note pulses plus eighth-note hats. The contrast is intentionally
    exaggerated so tests validate segmentation rather than psychoacoustics.
    """
    total_samples = int(round(spec.duration_seconds * spec.sample_rate))
    audio = np.zeros(total_samples, dtype=np.float32)

    for bar in range(spec.bars):
        dense_section = (bar // 4) % 2 == 1
        main_gain = 1.0 if dense_section else 0.28

        for beat in range(spec.beats_per_bar):
            beat_time = (bar * spec.beats_per_bar + beat) * spec.beat_seconds
            sample = int(round(beat_time * spec.sample_rate))

            if beat in (0, 2):
                _add_click(audio, sample, amplitude=main_gain, length=420)
            if beat in (1, 3):
                _add_click(audio, sample, amplitude=main_gain * 0.72, length=240)

            if dense_section:
                half_beat = sample + int(round(spec.beat_seconds * spec.sample_rate / 2))
                _add_click(audio, half_beat, amplitude=0.42, length=120)

    peak = float(np.max(np.abs(audio)))
    if peak > 0:
        audio = 0.9 * audio / peak

    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, audio, spec.sample_rate)
    return path
