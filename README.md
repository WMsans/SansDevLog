# Sans Subtitle Generator

Generate video files with typed subtitles synchronized to typing sounds.

## Features

- Chinese and English text support
- Per-character animation synced with audio
- Pitch variation per sentence
- Configurable visual style
- 1080p MP4 output

## Requirements

- Python 3.10+
- ffmpeg (system dependency)

## Installation

```bash
pip install -e .
```

## Usage

```bash
sans-sub input.txt -o output.mp4
```

With custom config:

```bash
sans-sub input.txt -o output.mp4 -c config.yaml
```

## Configuration

See `config.yaml` for all options.

## Development

```bash
pip install -e ".[dev]"
pytest
```
