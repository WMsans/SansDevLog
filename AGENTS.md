# AGENTS.md

Guidelines for agentic coding agents working in this repository.

## Project Overview

Sans Subtitle Generator - A Python tool that generates video files with typed subtitles synchronized to typing sounds. Supports Chinese and English text with configurable visual styles.

## Build, Lint, and Test Commands

### Installation

```bash
pip install -e .                    # Install package
pip install -e ".[dev]"             # Install with dev dependencies
```

### Testing

```bash
pytest                              # Run all tests
pytest -v                           # Run with verbose output
pytest tests/test_parser.py         # Run specific test file
pytest tests/test_parser.py::test_split_sentences_chinese  # Run single test
pytest -k "parser"                  # Run tests matching pattern
pytest --cov=src                    # Run with coverage
pytest --cov=src --cov-report=term-missing  # Coverage with missing lines
pytest -m "not integration"         # Skip integration tests
```

### Linting and Formatting

```bash
ruff check .                        # Run ruff linter
ruff check --fix .                  # Auto-fix lint issues
ruff format .                       # Format code with ruff
ruff format --check .               # Check formatting without modifying
```

### Running the CLI

```bash
sans-sub input.txt -o output.mp4              # Basic usage
sans-sub input.txt -o output.mp4 -c config.yaml  # With config
sans-sub input.txt -o output.mp4 -v           # Verbose mode
```

## Requirements

- Python 3.10+
- ffmpeg (system dependency) - required for video/audio processing
- ffprobe (comes with ffmpeg)

## Code Style Guidelines

### Imports

Order imports in three groups, separated by blank lines:

1. Standard library (alphabetically)
2. Third-party packages (alphabetically)
3. Local imports from `src.*` (alphabetically)

Example:
```python
import re
import subprocess
from pathlib import Path
from typing import Optional

import click
from PIL import Image

from src.config import load_config
from src.utils import verify_ffmpeg
```

### Type Annotations

Use type hints on all function signatures. Use Python 3.10+ union syntax:

```python
def calculate_pitch_shift(config: dict, seed: int | None = None) -> float:
def generate_sentence_frames(sentence: str, config: dict) -> list[Image.Image]:
```

Common types used:
- `list[str]`, `list[int]`, `list[Image.Image]`
- `dict` (untyped dicts for config)
- `Optional[str]` or `str | None`
- `Path` for file paths in type hints

### Naming Conventions

- **Functions/Variables**: `snake_case` (e.g., `split_sentences`, `frame_count`)
- **Classes**: `PascalCase` (not currently used in this codebase)
- **Constants**: `UPPER_SNAKE_CASE` at module level (e.g., `DEFAULT_CONFIG`)
- **Private functions**: Prefix with underscore (e.g., `_internal_helper`)
- **Test functions**: `test_<function>_<scenario>` (e.g., `test_split_sentences_chinese`)

### Function Style

Keep functions small and focused. Use early returns for edge cases:

```python
def split_sentences(text: str) -> list[str]:
    if not text.strip():
        return []
    # ... rest of logic
```

### Error Handling

- Use `raise click.ClickException()` for user-facing CLI errors
- Use standard exceptions (`FileNotFoundError`, `ValueError`) for internal errors
- Log warnings with `logger.warning()` for non-fatal issues
- Log errors with `logger.error()` before raising `SystemExit(1)` for fatal CLI errors

Example:
```python
if not Path(sound_path).exists():
    logger.error(f"Sound file not found: {sound_path}")
    raise SystemExit(1)
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Found {len(sentences)} sentences")
logger.debug(f"Processing frame {i}")
logger.warning(f"Font not found: {font_path}")
```

### Configuration

Configuration is loaded from YAML files. Use `dict.get()` with defaults for optional values:

```python
fps = config.get("fps", 30)
pitch_config = config.get("pitch_variation", {})
min_pitch = pitch_config.get("min", 0.9)
```

## Testing Guidelines

### Test File Organization

- Tests live in `tests/` directory
- Mirror source structure: `tests/test_<module>.py`
- Use `tests/fixtures/` for test data files

### Test Style

Use pytest fixtures for setup:

```python
def test_load_config_file_exists(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("video:\n  fps: 60\n")
    config = load_config(str(config_file))
    assert config["video"]["fps"] == 60
```

Use `monkeypatch` for mocking:

```python
def test_check_ffmpeg_false(monkeypatch):
    monkeypatch.setattr(utils.shutil, "which", lambda _: None)
    assert utils.check_ffmpeg() is False
```

Use `CliRunner` for CLI tests:

```python
from click.testing import CliRunner

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
```

Skip tests requiring external dependencies:

```python
ffmpeg_available = shutil.which("ffmpeg") is not None
pytestmark = pytest.mark.skipif(
    not ffmpeg_available,
    reason="ffmpeg not installed",
)
```

### Test Naming

Name tests descriptively: `<function>_<scenario>_<expected>`:

```python
test_split_sentences_chinese()
test_split_sentences_empty()
test_load_config_file_not_exists()
```

## Project Structure

```
sans_subtitle_generator/
├── src/                    # Source code
│   ├── __init__.py         # Package init with version
│   ├── main.py             # CLI entry point
│   ├── config.py           # Configuration loading
│   ├── parser.py           # Text parsing utilities
│   ├── frame_generator.py  # PIL image frame generation
│   ├── audio_builder.py    # Audio track creation via ffmpeg
│   ├── video_builder.py    # Video assembly via ffmpeg
│   └── utils.py            # Utility functions
├── tests/                   # Test files
│   ├── fixtures/           # Test data
│   └── test_*.py           # Unit and integration tests
├── fonts/                   # Font files
├── sounds/                  # Sound files
├── config.yaml              # Default configuration
├── pyproject.toml           # Project metadata
└── README.md                # User documentation
```

## Important Notes

- All file I/O uses UTF-8 encoding: `open(file, "r", encoding="utf-8")`
- Use `Path` from pathlib for file operations
- Temporary files/directories should use `tempfile.TemporaryDirectory()` context manager
- The `src` package is installed as `sans-subtitle-generator`
- CLI entry point is `sans-sub` defined in `src.main:main`