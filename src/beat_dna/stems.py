from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import librosa

from .hearing import FrameFeatures, GridCell, aggregate_to_musical_grid, extract_frame_features

StemKind = Literal["drums", "bass", "vocals", "instruments", "other"]


@dataclass(frozen=True)
class StemInput:
    kind: StemKind
    path: Path


@dataclass(frozen=True)
class StemAnalysis:
    kind: StemKind
    source_file: str
    sample_rate: int
    duration_seconds: float
    frame_features: list[FrameFeatures]
    grid: list[GridCell]


def analyze_stem(
    stem: StemInput,
    *,
    bpm: float,
    bars: int,
    beats_per_bar: int = 4,
    steps_per_beat: int = 4,
) -> StemAnalysis:
    """Analyze a pre-separated stem on a shared musical grid."""
    audio, sample_rate = librosa.load(stem.path, sr=None, mono=True)
    frames = extract_frame_features(audio, sample_rate)
    onset_frames = librosa.onset.onset_detect(y=audio, sr=sample_rate, units="frames")
    onset_times = librosa.frames_to_time(onset_frames, sr=sample_rate).tolist()
    grid = aggregate_to_musical_grid(
        frames,
        onset_times,
        bpm=bpm,
        bars=bars,
        beats_per_bar=beats_per_bar,
        steps_per_beat=steps_per_beat,
    )
    return StemAnalysis(
        kind=stem.kind,
        source_file=str(stem.path),
        sample_rate=sample_rate,
        duration_seconds=float(librosa.get_duration(y=audio, sr=sample_rate)),
        frame_features=frames,
        grid=grid,
    )
