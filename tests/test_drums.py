import numpy as np

from beat_dna.drum_generator import generate_drum_pattern
from beat_dna.drums import classify_transient


def _sine_burst(frequency: float, sample_rate: int = 22050, seconds: float = 0.12) -> np.ndarray:
    size = int(sample_rate * seconds)
    times = np.arange(size) / sample_rate
    envelope = np.exp(-times * 28.0)
    return (np.sin(2 * np.pi * frequency * times) * envelope).astype(np.float32)


def _noise_burst(sample_rate: int = 22050, seconds: float = 0.12) -> np.ndarray:
    rng = np.random.default_rng(7)
    size = int(sample_rate * seconds)
    times = np.arange(size) / sample_rate
    envelope = np.exp(-times * 22.0)
    return (rng.normal(0, 1, size) * envelope).astype(np.float32)


def test_classifier_separates_low_bass_from_snare_noise() -> None:
    bass = classify_transient(_sine_burst(60.0), 22050)
    snare = classify_transient(_noise_burst(), 22050)

    assert bass.label in {"bass", "kick"}
    assert snare.label in {"snare", "hat"}
    assert bass.low_ratio > snare.low_ratio
    assert snare.spectral_centroid_hz > bass.spectral_centroid_hz


def test_drum_generator_is_deterministic_and_structured() -> None:
    first = generate_drum_pattern(bars=4, seed=42, density=0.6)
    second = generate_drum_pattern(bars=4, seed=42, density=0.6)

    assert first == second
    assert any(hit.instrument == "kick" for hit in first.hits)
    assert any(hit.instrument == "snare" for hit in first.hits)
    assert any(hit.instrument == "hat" for hit in first.hits)
    assert all(0 <= hit.step < 64 for hit in first.hits)
    assert all(1 <= hit.velocity <= 127 for hit in first.hits)

    snare_steps = {hit.step for hit in first.hits if hit.instrument == "snare"}
    assert snare_steps == {8, 24, 40, 56}
