from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import librosa
import numpy as np


@dataclass(frozen=True)
class FrequencyBand:
    name: str
    low_hz: float
    high_hz: float


DEFAULT_BANDS: tuple[FrequencyBand, ...] = (
    FrequencyBand("sub", 20.0, 50.0),
    FrequencyBand("bass", 50.0, 120.0),
    FrequencyBand("low_mid", 120.0, 400.0),
    FrequencyBand("mid", 400.0, 1500.0),
    FrequencyBand("presence", 1500.0, 4000.0),
    FrequencyBand("high", 4000.0, 10000.0),
    FrequencyBand("air", 10000.0, 20000.0),
)


@dataclass(frozen=True)
class FrameFeatures:
    time_seconds: float
    rms: float
    spectral_centroid_hz: float
    spectral_flatness: float
    zero_crossing_rate: float
    band_energy: dict[str, float]


@dataclass(frozen=True)
class GridCell:
    bar: int
    step: int
    start_seconds: float
    end_seconds: float
    mean_rms: float
    onset_count: int
    band_energy: dict[str, float]


def extract_frame_features(
    audio: np.ndarray,
    sample_rate: int,
    *,
    hop_length: int = 512,
    n_fft: int = 2048,
    bands: Iterable[FrequencyBand] = DEFAULT_BANDS,
) -> list[FrameFeatures]:
    """Convert raw audio into a compact time-frequency representation."""
    if audio.ndim != 1:
        audio = librosa.to_mono(audio)
    if audio.size == 0:
        return []

    stft = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
    power = np.abs(stft) ** 2
    frequencies = librosa.fft_frequencies(sr=sample_rate, n_fft=n_fft)
    times = librosa.frames_to_time(np.arange(power.shape[1]), sr=sample_rate, hop_length=hop_length)

    rms = librosa.feature.rms(S=np.abs(stft))[0]
    centroid = librosa.feature.spectral_centroid(S=np.abs(stft), sr=sample_rate)[0]
    flatness = librosa.feature.spectral_flatness(S=np.abs(stft))[0]
    zcr = librosa.feature.zero_crossing_rate(audio, frame_length=n_fft, hop_length=hop_length)[0]

    band_masks = {
        band.name: (frequencies >= band.low_hz) & (frequencies < min(band.high_hz, sample_rate / 2))
        for band in bands
    }
    total = np.sum(power, axis=0) + 1e-12

    features: list[FrameFeatures] = []
    for index, time_seconds in enumerate(times):
        band_energy = {
            name: float(np.sum(power[mask, index]) / total[index]) if np.any(mask) else 0.0
            for name, mask in band_masks.items()
        }
        features.append(
            FrameFeatures(
                time_seconds=float(time_seconds),
                rms=float(rms[index]),
                spectral_centroid_hz=float(centroid[index]),
                spectral_flatness=float(flatness[index]),
                zero_crossing_rate=float(zcr[index]),
                band_energy=band_energy,
            )
        )
    return features


def aggregate_to_musical_grid(
    frames: list[FrameFeatures],
    onset_times: list[float],
    *,
    bpm: float,
    bars: int,
    beats_per_bar: int = 4,
    steps_per_beat: int = 4,
) -> list[GridCell]:
    """Aggregate frame features to a bar/step grid such as 1/16 notes."""
    if bpm <= 0:
        raise ValueError("bpm must be positive")
    if bars <= 0:
        raise ValueError("bars must be positive")
    if beats_per_bar <= 0 or steps_per_beat <= 0:
        raise ValueError("grid dimensions must be positive")

    steps_per_bar = beats_per_bar * steps_per_beat
    step_seconds = 60.0 / bpm / steps_per_beat
    frame_times = np.asarray([frame.time_seconds for frame in frames], dtype=float)
    onset_array = np.asarray(onset_times, dtype=float)
    band_names = sorted({name for frame in frames for name in frame.band_energy})

    cells: list[GridCell] = []
    for bar in range(bars):
        for step in range(steps_per_bar):
            absolute_step = bar * steps_per_bar + step
            start = absolute_step * step_seconds
            end = start + step_seconds
            frame_mask = (frame_times >= start) & (frame_times < end)
            onset_count = int(np.sum((onset_array >= start) & (onset_array < end)))

            selected = [frame for frame, keep in zip(frames, frame_mask) if keep]
            mean_rms = float(np.mean([frame.rms for frame in selected])) if selected else 0.0
            band_energy = {
                name: float(np.mean([frame.band_energy.get(name, 0.0) for frame in selected])) if selected else 0.0
                for name in band_names
            }
            cells.append(
                GridCell(
                    bar=bar,
                    step=step,
                    start_seconds=start,
                    end_seconds=end,
                    mean_rms=mean_rms,
                    onset_count=onset_count,
                    band_energy=band_energy,
                )
            )
    return cells


def compare_layers(left: list[GridCell], right: list[GridCell]) -> dict[str, float]:
    """Estimate how two aligned layers interact on the same musical grid."""
    if len(left) != len(right):
        raise ValueError("layers must use the same grid")
    if not left:
        return {"rms_correlation": 0.0, "simultaneous_onset_ratio": 0.0, "spectral_overlap": 0.0}

    left_rms = np.asarray([cell.mean_rms for cell in left])
    right_rms = np.asarray([cell.mean_rms for cell in right])
    if np.std(left_rms) < 1e-12 or np.std(right_rms) < 1e-12:
        rms_correlation = 0.0
    else:
        rms_correlation = float(np.corrcoef(left_rms, right_rms)[0, 1])

    simultaneous = sum(1 for a, b in zip(left, right) if a.onset_count > 0 and b.onset_count > 0)
    active_union = sum(1 for a, b in zip(left, right) if a.onset_count > 0 or b.onset_count > 0)
    simultaneous_onset_ratio = simultaneous / active_union if active_union else 0.0

    overlaps: list[float] = []
    for a, b in zip(left, right):
        names = set(a.band_energy) | set(b.band_energy)
        overlaps.append(sum(min(a.band_energy.get(name, 0.0), b.band_energy.get(name, 0.0)) for name in names))

    return {
        "rms_correlation": rms_correlation,
        "simultaneous_onset_ratio": float(simultaneous_onset_ratio),
        "spectral_overlap": float(np.mean(overlaps)),
    }
