from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class TrackAnalysis(BaseModel):
    source_file: str
    duration_seconds: float = Field(ge=0)
    sample_rate: int = Field(gt=0)
    estimated_bpm: float = Field(ge=0)
    beat_times_seconds: list[float]
    onset_times_seconds: list[float]
    rms_times_seconds: list[float]
    rms_values: list[float]

    @property
    def stem(self) -> str:
        return Path(self.source_file).stem
