# Beat DNA

Локальный инструмент для анализа битов и последующего построения генератора аранжировок и MIDI-паттернов.

## Первая версия

- читает WAV/MP3 из папки `input/`;
- определяет длительность и примерный BPM;
- строит beat grid;
- находит onset-события;
- считает RMS energy;
- сохраняет JSON и PNG-отчёты в `output/`.

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
```

## Запуск

```bash
beat-dna analyze input --output output
```

## Тесты

```bash
pytest
```

Аудиофайлы, стемы и результаты анализа не коммитятся в Git.
