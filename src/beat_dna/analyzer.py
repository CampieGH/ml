from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np

from .models import TrackAnalysis

SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}


def analyze_track(path: Path) -> TrackAnalysis:
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported audio format: {path.suffix}")

    audio, sample_rate = librosa.load(path, sr=None, mono=True)
    if audio.size == 0:
        raise ValueError(f"Audio file is empty: {path}")

    duration = float(librosa.get_duration(y=audio, sr=sample_rate))

    onset_envelope = librosa.onset.onset_strength(y=audio, sr=sample_rate)
    tempo, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_envelope,
        sr=sample_rate,
    )
    bpm = float(np.asarray(tempo).reshape(-1)[0]) if np.size(tempo) else 0.0
    beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate)

    onset_frames = librosa.onset.onset_detect(
        onset_envelope=onset_envelope,
        sr=sample_rate,
        units="frames",
        backtrack=False,
    )
    onset_times = librosa.frames_to_time(onset_frames, sr=sample_rate)

    rms = librosa.feature.rms(y=audio)[0]
    rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=sample_rate)

    return TrackAnalysis(
        source_file=str(path),
        duration_seconds=duration,
        sample_rate=int(sample_rate),
        estimated_bpm=bpm,
        beat_times_seconds=[float(value) for value in beat_times],
        onset_times_seconds=[float(value) for value in onset_times],
        rms_times_seconds=[float(value) for value in rms_times],
        rms_values=[float(value) for value in rms],
    )


def find_audio_files(directory: Path) -> list[Path]:
    if not directory.exists():
        raise FileNotFoundError(directory)
    if not directory.is_dir():
        raise NotADirectoryError(directory)

    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
