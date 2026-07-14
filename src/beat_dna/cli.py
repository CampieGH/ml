from __future__ import annotations

from pathlib import Path

import librosa
import typer

from .analyzer import analyze_track, find_audio_files
from .reporting import save_json_report, save_plot

app = typer.Typer(no_args_is_help=True, help="Analyze beats and export machine-readable reports.")


@app.command()
def analyze(
    input_dir: Path = typer.Argument(Path("input"), exists=True, file_okay=False),
    output_dir: Path = typer.Option(Path("output"), "--output", "-o"),
) -> None:
    """Analyze every supported audio file in INPUT_DIR."""
    files = find_audio_files(input_dir)
    if not files:
        typer.echo(f"No supported audio files found in {input_dir}")
        raise typer.Exit(code=1)

    for path in files:
        typer.echo(f"Analyzing {path.name}...")
        result = analyze_track(path)
        audio, sample_rate = librosa.load(path, sr=None, mono=True)
        json_path = save_json_report(result, output_dir)
        plot_path = save_plot(result, audio, sample_rate, output_dir)
        typer.echo(
            f"  BPM {result.estimated_bpm:.2f} | "
            f"{result.duration_seconds:.2f}s | {json_path.name} | {plot_path.name}"
        )


if __name__ == "__main__":
    app()
