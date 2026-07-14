from pathlib import Path

import numpy as np
import soundfile as sf

from beat_dna.analyzer import analyze_track, find_audio_files


def test_analyze_synthetic_click_track(tmp_path: Path) -> None:
    sample_rate = 22050
    duration_seconds = 4
    audio = np.zeros(sample_rate * duration_seconds, dtype=np.float32)

    for second in range(duration_seconds):
        start = second * sample_rate
        audio[start : start + 256] = np.hanning(256).astype(np.float32)

    source = tmp_path / "clicks.wav"
    sf.write(source, audio, sample_rate)

    result = analyze_track(source)

    assert result.duration_seconds == duration_seconds
    assert result.sample_rate == sample_rate
    assert result.estimated_bpm >= 0
    assert result.rms_values
    assert result.onset_times_seconds


def test_find_audio_files_ignores_other_files(tmp_path: Path) -> None:
    (tmp_path / "track.wav").write_bytes(b"")
    (tmp_path / "notes.txt").write_text("ignore me", encoding="utf-8")

    assert find_audio_files(tmp_path) == [tmp_path / "track.wav"]
