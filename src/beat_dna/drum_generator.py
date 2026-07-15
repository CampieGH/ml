from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Literal

Instrument = Literal["kick", "snare", "hat"]


@dataclass(frozen=True)
class DrumHit:
    step: int
    instrument: Instrument
    velocity: int


@dataclass(frozen=True)
class DrumPattern:
    steps_per_bar: int
    bars: int
    hits: list[DrumHit]


def generate_drum_pattern(
    bars: int = 4,
    steps_per_bar: int = 16,
    seed: int | None = None,
    density: float = 0.5,
) -> DrumPattern:
    """Generate a trap-oriented drum pattern on a sixteenth-note grid."""
    if bars <= 0:
        raise ValueError("bars must be positive")
    if steps_per_bar != 16:
        raise ValueError("first version supports 16 steps per bar")
    if not 0.0 <= density <= 1.0:
        raise ValueError("density must be between 0 and 1")

    rng = random.Random(seed)
    hits: list[DrumHit] = []

    for bar in range(bars):
        offset = bar * steps_per_bar

        # Backbeat: trap commonly places snare/clap on beat 3.
        hits.append(DrumHit(offset + 8, "snare", rng.randint(92, 118)))

        # Eighth-note hats, with occasional sixteenth-note additions.
        for step in range(0, steps_per_bar, 2):
            hits.append(DrumHit(offset + step, "hat", rng.randint(58, 92)))
            if density > 0.55 and rng.random() < (density - 0.45) * 0.55:
                extra = step + 1
                if extra < steps_per_bar:
                    hits.append(DrumHit(offset + extra, "hat", rng.randint(42, 78)))

        # Kick starts strongly, then syncopates around the snare.
        kick_steps = {0}
        candidates = [3, 5, 7, 10, 11, 13, 14]
        for step in candidates:
            probability = 0.12 + density * 0.38
            if step in (7, 10, 14):
                probability += 0.12
            if rng.random() < probability:
                kick_steps.add(step)

        # Avoid a kick on every candidate. Restraint, a rare human invention.
        for step in sorted(kick_steps):
            hits.append(DrumHit(offset + step, "kick", rng.randint(92, 124)))

        # Small fill at the end of every fourth bar.
        if (bar + 1) % 4 == 0 and density >= 0.45:
            for step in (14, 15):
                hits.append(DrumHit(offset + step, "hat", rng.randint(68, 102)))

    unique = {(hit.step, hit.instrument): hit for hit in hits}
    ordered = sorted(unique.values(), key=lambda hit: (hit.step, hit.instrument))
    return DrumPattern(steps_per_bar=steps_per_bar, bars=bars, hits=ordered)
