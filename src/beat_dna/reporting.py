from __future__ import annotations

import json
from pathlib import Path

import librosa
import matplotlib.pyplot as plt
import numpy as np

from .models import TrackAnalysis


def save_json_report(analysis: TrackAnalysis, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{analysis.stem}.json"
    destination.write_text(
        json.dumps(analysis.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return destination


def save_plot(
    analysis: TrackAnalysis,
    audio: np.ndarray,
    sample_rate: int,
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{analysis.stem}.png"

    times = librosa.times_like(audio, sr=sample_rate)
    figure, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    axes[0].plot(times, audio, linewidth=0.6)
    axes[0].set_title(f"Waveform: {analysis.stem}")
    axes[0].set_ylabel("Amplitude")

    axes[1].plot(analysis.rms_times_seconds, analysis.rms_values, linewidth=1.0)
    for beat_time in analysis.beat_times_seconds:
        axes[1].axvline(beat_time, linewidth=0.5, alpha=0.35)
    for onset_time in analysis.onset_times_seconds:
        axes[1].axvline(onset_time, linewidth=0.4, alpha=0.15)

    axes[1].set_title(f"RMS / Beats / Onsets | Estimated BPM: {analysis.estimated_bpm:.2f}")
    axes[1].set_xlabel("Time, seconds")
    axes[1].set_ylabel("RMS")

    figure.tight_layout()
    figure.savefig(destination, dpi=160)
    plt.close(figure)
    return destination
