from pathlib import Path

from beat_dna.analyzer import analyze_track
from beat_dna.structure import estimate_bar_energy, segment_by_energy
from beat_dna.synthetic import SyntheticBeatSpec, generate_synthetic_beat


def test_synthetic_beat_has_expected_tempo(tmp_path: Path) -> None:
    spec = SyntheticBeatSpec(bpm=120.0, bars=16)
    source = generate_synthetic_beat(tmp_path / "synthetic.wav", spec)

    result = analyze_track(source)

    assert abs(result.duration_seconds - spec.duration_seconds) < 0.1
    assert abs(result.estimated_bpm - spec.bpm) < 4.0
    assert len(result.beat_times_seconds) >= 48


def test_energy_segmentation_detects_contrast(tmp_path: Path) -> None:
    source = generate_synthetic_beat(
        tmp_path / "sections.wav",
        SyntheticBeatSpec(bpm=140.0, bars=16),
    )
    result = analyze_track(source)

    energies = estimate_bar_energy(result)
    sections = segment_by_energy(energies, min_section_bars=2, relative_change=0.12)

    assert len(energies) >= 12
    assert len(sections) >= 2
    assert {section.label for section in sections} == {"sparse", "dense"}
