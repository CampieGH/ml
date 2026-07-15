from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .models import TrackAnalysis


@dataclass(frozen=True)
class SectionBoundary:
    start_bar: int
    end_bar: int
    mean_rms: float
    label: str


def estimate_bar_energy(
    analysis: TrackAnalysis,
    beats_per_bar: int = 4,
) -> list[float]:
    """Average RMS energy between groups of beat timestamps."""
    beat_times = analysis.beat_times_seconds
    if len(beat_times) < beats_per_bar + 1:
        return []

    rms_times = np.asarray(analysis.rms_times_seconds)
    rms_values = np.asarray(analysis.rms_values)
    energies: list[float] = []

    for start_index in range(0, len(beat_times) - beats_per_bar, beats_per_bar):
        start = beat_times[start_index]
        end = beat_times[start_index + beats_per_bar]
        mask = (rms_times >= start) & (rms_times < end)
        energies.append(float(np.mean(rms_values[mask])) if np.any(mask) else 0.0)

    return energies


def segment_by_energy(
    bar_energies: list[float],
    min_section_bars: int = 2,
    relative_change: float = 0.22,
) -> list[SectionBoundary]:
    """Split bars when smoothed energy changes materially.

    Labels are intentionally neutral. Hook/verse naming needs musical context
    and should not be fabricated from loudness alone, despite software's
    historical enthusiasm for confident nonsense.
    """
    if not bar_energies:
        return []

    values = np.asarray(bar_energies, dtype=float)
    if values.size >= 3:
        values = np.convolve(values, np.ones(3) / 3, mode="same")

    boundaries = [0]
    for index in range(1, len(values)):
        section_start = boundaries[-1]
        if index - section_start < min_section_bars:
            continue
        baseline = max(abs(values[index - 1]), 1e-9)
        change = abs(values[index] - values[index - 1]) / baseline
        if change >= relative_change:
            boundaries.append(index)

    boundaries.append(len(values))
    sections: list[SectionBoundary] = []
    median = float(np.median(values))
    for start, end in zip(boundaries, boundaries[1:]):
        mean = float(np.mean(values[start:end]))
        label = "dense" if mean >= median else "sparse"
        sections.append(SectionBoundary(start, end, mean, label))
    return sections
