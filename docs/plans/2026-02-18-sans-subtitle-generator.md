# Sans Subtitle Generator Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python CLI tool that generates video files with typed subtitles synchronized to typing sounds, supporting Chinese mixed with English text.

**Architecture:** Frame-by-frame approach using Pillow for text rendering and ffmpeg for audio/video assembly. Each character gets one frame, audio is pitch-shifted per sentence.

**Tech Stack:** Python 3.10+, Pillow, ffmpeg, PyYAML, pytest

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `src/__init__.py`
- Create: `config.yaml`
- Create: `.gitignore`
- Create: `tests/__init__.py`

**Step 1: Create project structure**

```bash
mkdir -p src tests fonts sounds output tests/fixtures
```

**Step 2: Create pyproject.toml**

```toml
[project]
name = "sans-subtitle-generator"
version = "0.1.0"
description = "Generate video subtitles with typing sounds"
requires-python = ">=3.10"
dependencies = [
    "Pillow>=10.0.0",
    "PyYAML>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

[project.scripts]
sans-sub = "src.main:main"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools"
```

**Step 3: Create src/__init__.py**

```python
"""Sans Subtitle Generator - Generate video subtitles with typing sounds."""

__version__ = "0.1.0"
```

**Step 4: Create tests/__init__.py**

```python
"""Tests for sans-subtitle-generator."""
```

**Step 5: Create .gitignore**

```
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
build/
output/*.mp4
frames/
temp_audio.wav
```

**Step 6: Create default config.yaml**

```yaml
video:
  resolution: [1920, 1080]
  fps: 30
  format: mp4

style:
  font_path: ./fonts/default.ttf
  font_size: 48
  text_color: "#FFFFFF"
  background_color: "#000000"
  text_position: [100, 500]

audio:
  typing_sound: ./sounds/sans_typing.wav
  pitch_variation:
    min: 0.9
    max: 1.1
    random: true
  character_duration_ms: 50
  sentence_pause_ms: 500

parsing:
  sentence_enders: ["。", "！", "？", ".", "!", "?"]
  sentence_pauses: ["，", "、", ","]
```

**Step 7: Commit**

```bash
git add pyproject.toml src/__init__.py tests/__init__.py .gitignore config.yaml
git commit -m "chore: initialize project structure"
```

---

## Task 2: Configuration Module

**Files:**
- Create: `src/config.py`
- Create: `tests/test_config.py`

**Step 1: Write the failing test**

```python
# tests/test_config.py
import pytest
from src.config import load_config, get_default_config


def test_load_config_file_exists(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("video:\n  fps: 60\n")
    config = load_config(str(config_file))
    assert config["video"]["fps"] == 60


def test_load_config_file_not_exists():
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.yaml")


def test_get_default_config():
    config = get_default_config()
    assert config["video"]["fps"] == 30
    assert config["style"]["font_size"] == 48
    assert "sentence_enders" in config["parsing"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.config'"

**Step 3: Write minimal implementation**

```python
# src/config.py
import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "video": {
        "resolution": [1920, 1080],
        "fps": 30,
        "format": "mp4",
    },
    "style": {
        "font_path": "./fonts/default.ttf",
        "font_size": 48,
        "text_color": "#FFFFFF",
        "background_color": "#000000",
        "text_position": [100, 500],
    },
    "audio": {
        "typing_sound": "./sounds/sans_typing.wav",
        "pitch_variation": {
            "min": 0.9,
            "max": 1.1,
            "random": True,
        },
        "character_duration_ms": 50,
        "sentence_pause_ms": 500,
    },
    "parsing": {
        "sentence_enders": ["。", "！", "？", ".", "!", "?"],
        "sentence_pauses": ["，", "、", ","],
    },
}


def load_config(config_path: str) -> dict:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_default_config() -> dict:
    return DEFAULT_CONFIG.copy()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add configuration module with YAML loading"
```

---

## Task 3: Parser Module - Sentence Splitting

**Files:**
- Create: `src/parser.py`
- Create: `tests/test_parser.py`
- Create: `tests/fixtures/sample_chinese.txt`
- Create: `tests/fixtures/sample_mixed.txt`

**Step 1: Write the failing test**

```python
# tests/test_parser.py
import pytest
from src.parser import split_sentences


def test_split_sentences_chinese():
    text = "这是第一句。这是第二句！这是第三句？"
    sentences = split_sentences(text)
    assert len(sentences) == 3
    assert sentences[0] == "这是第一句。"
    assert sentences[1] == "这是第二句！"
    assert sentences[2] == "这是第三句？"


def test_split_sentences_english():
    text = "First sentence. Second sentence! Third sentence?"
    sentences = split_sentences(text)
    assert len(sentences) == 3
    assert sentences[0] == "First sentence."
    assert sentences[1] == "Second sentence!"
    assert sentences[2] == "Third sentence?"


def test_split_sentences_mixed():
    text = "这是Chinese text。And English text. 混合Mix！"
    sentences = split_sentences(text)
    assert len(sentences) == 3
    assert sentences[0] == "这是Chinese text。"
    assert sentences[1] == "And English text."
    assert sentences[2] == "混合Mix！"


def test_split_sentences_empty():
    sentences = split_sentences("")
    assert sentences == []


def test_split_sentences_no_enders():
    text = "No sentence enders here"
    sentences = split_sentences(text)
    assert len(sentences) == 1
    assert sentences[0] == "No sentence enders here"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_parser.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.parser'"

**Step 3: Write minimal implementation**

```python
# src/parser.py
import re


def split_sentences(text: str) -> list[str]:
    if not text.strip():
        return []
    
    pattern = r'[^。！？.!?]+[。！？.!?]?'
    matches = re.findall(pattern, text)
    
    sentences = []
    for match in matches:
        stripped = match.strip()
        if stripped:
            sentences.append(stripped)
    
    return sentences
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_parser.py -v`
Expected: PASS

**Step 5: Create test fixtures**

```bash
echo "这是测试文本。包含多个句子！有中文和English mix. 最后一句？" > tests/fixtures/sample_mixed.txt
echo "纯中文测试。第一句。第二句！第三句？" > tests/fixtures/sample_chinese.txt
```

**Step 6: Commit**

```bash
git add src/parser.py tests/test_parser.py tests/fixtures/
git commit -m "feat: add parser module with Chinese/English sentence splitting"
```

---

## Task 4: Frame Generator Module

**Files:**
- Create: `src/frame_generator.py`
- Create: `tests/test_frame_generator.py`

**Step 1: Write the failing test**

```python
# tests/test_frame_generator.py
import pytest
from PIL import Image
from src.frame_generator import generate_sentence_frames


def test_generate_sentence_frames_count():
    config = {
        "resolution": [1920, 1080],
        "font_size": 48,
        "text_color": "#FFFFFF",
        "background_color": "#000000",
        "text_position": [100, 500],
    }
    sentence = "Hello"
    frames = generate_sentence_frames(sentence, config, font_path=None)
    assert len(frames) == 5  # One frame per character


def test_generate_sentence_frames_dimensions():
    config = {
        "resolution": [1920, 1080],
        "font_size": 48,
        "text_color": "#FFFFFF",
        "background_color": "#000000",
        "text_position": [100, 500],
    }
    sentence = "Test"
    frames = generate_sentence_frames(sentence, config, font_path=None)
    for frame in frames:
        assert frame.size == (1920, 1080)


def test_generate_sentence_frames_empty():
    config = {
        "resolution": [1920, 1080],
        "font_size": 48,
        "text_color": "#FFFFFF",
        "background_color": "#000000",
        "text_position": [100, 500],
    }
    frames = generate_sentence_frames("", config, font_path=None)
    assert frames == []
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_frame_generator.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.frame_generator'"

**Step 3: Write minimal implementation**

```python
# src/frame_generator.py
from PIL import Image, ImageDraw, ImageFont
from typing import Optional


def generate_sentence_frames(
    sentence: str,
    config: dict,
    font_path: Optional[str] = None
) -> list[Image.Image]:
    if not sentence:
        return []
    
    width, height = config["resolution"]
    font_size = config["font_size"]
    text_color = config["text_color"]
    bg_color = config["background_color"]
    text_x, text_y = config["text_position"]
    
    frames = []
    
    try:
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    
    for i in range(1, len(sentence) + 1):
        frame = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(frame)
        visible_text = sentence[:i]
        draw.text((text_x, text_y), visible_text, fill=text_color, font=font)
        frames.append(frame)
    
    return frames
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_frame_generator.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/frame_generator.py tests/test_frame_generator.py
git commit -m "feat: add frame generator with PIL text rendering"
```

---

## Task 5: Audio Builder Module

**Files:**
- Create: `src/audio_builder.py`
- Create: `tests/test_audio_builder.py`

**Step 1: Write the failing test**

```python
# tests/test_audio_builder.py
import pytest
from src.audio_builder import calculate_pitch_shift, get_character_count


def test_get_character_count_chinese():
    sentences = ["这是中文。", "English text."]
    counts = get_character_count(sentences)
    assert counts[0] == 5
    assert counts[1] == 13


def test_calculate_pitch_shift():
    config = {
        "pitch_variation": {
            "min": 0.9,
            "max": 1.1,
            "random": False,
        }
    }
    pitch = calculate_pitch_shift(config, seed=0)
    assert 0.9 <= pitch <= 1.1


def test_calculate_pitch_shift_random():
    config = {
        "pitch_variation": {
            "min": 0.8,
            "max": 1.2,
            "random": True,
        }
    }
    import random
    random.seed(42)
    pitch1 = calculate_pitch_shift(config)
    pitch2 = calculate_pitch_shift(config)
    assert 0.8 <= pitch1 <= 1.2
    assert 0.8 <= pitch2 <= 1.2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_audio_builder.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.audio_builder'"

**Step 3: Write minimal implementation**

```python
# src/audio_builder.py
import random
import subprocess
from pathlib import Path


def get_character_count(sentences: list[str]) -> list[int]:
    return [len(sentence) for sentence in sentences]


def calculate_pitch_shift(config: dict, seed: int | None = None) -> float:
    pitch_config = config.get("pitch_variation", {})
    min_pitch = pitch_config.get("min", 0.9)
    max_pitch = pitch_config.get("max", 1.1)
    is_random = pitch_config.get("random", True)
    
    if seed is not None:
        random.seed(seed)
    
    if is_random:
        return random.uniform(min_pitch, max_pitch)
    else:
        return (min_pitch + max_pitch) / 2


def build_audio_track(
    sentences: list[str],
    sound_path: str,
    output_path: str,
    config: dict
) -> str:
    char_duration_ms = config.get("character_duration_ms", 50)
    sentence_pause_ms = config.get("sentence_pause_ms", 500)
    
    audio_clips = []
    temp_files = []
    
    for i, sentence in enumerate(sentences):
        pitch = calculate_pitch_shift(config)
        char_count = len(sentence)
        duration_ms = char_count * char_duration_ms
        
        temp_clip = f"temp_sentence_{i}.wav"
        temp_files.append(temp_clip)
        
        cmd = [
            "ffmpeg", "-y",
            "-i", sound_path,
            "-af", f"apad=whole_dur={duration_ms}ms,atempo={pitch}",
            "-t", f"{duration_ms / 1000}",
            temp_clip
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        audio_clips.append(temp_clip)
        
        if i < len(sentences) - 1:
            silence_path = f"temp_silence_{i}.wav"
            temp_files.append(silence_path)
            silence_cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", f"anullsrc=r=44100:cl=mono",
                "-t", f"{sentence_pause_ms / 1000}",
                silence_path
            ]
            subprocess.run(silence_cmd, check=True, capture_output=True)
            audio_clips.append(silence_path)
    
    concat_file = "temp_concat.txt"
    with open(concat_file, "w") as f:
        for clip in audio_clips:
            f.write(f"file '{clip}'\n")
    
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output_path
    ]
    subprocess.run(concat_cmd, check=True, capture_output=True)
    
    for temp_file in temp_files + [concat_file]:
        Path(temp_file).unlink(missing_ok=True)
    
    return output_path
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_audio_builder.py -v`
Expected: PASS (unit tests only, not build_audio_track which requires ffmpeg)

**Step 5: Commit**

```bash
git add src/audio_builder.py tests/test_audio_builder.py
git commit -m "feat: add audio builder with pitch shift support"
```

---

## Task 6: Video Builder Module

**Files:**
- Create: `src/video_builder.py`
- Create: `tests/test_video_builder.py`

**Step 1: Write the failing test**

```python
# tests/test_video_builder.py
import pytest
from PIL import Image
import tempfile
from pathlib import Path
from src.video_builder import save_frames, assemble_video


def test_save_frames():
    frames = [Image.new("RGB", (100, 100), "red") for _ in range(3)]
    with tempfile.TemporaryDirectory() as tmpdir:
        save_frames(frames, tmpdir, prefix="test")
        saved_files = list(Path(tmpdir).glob("test_*.png"))
        assert len(saved_files) == 3


def test_save_frames_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        save_frames([], tmpdir, prefix="test")
        saved_files = list(Path(tmpdir).glob("test_*.png"))
        assert len(saved_files) == 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_video_builder.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.video_builder'"

**Step 3: Write minimal implementation**

```python
# src/video_builder.py
import subprocess
from pathlib import Path
from PIL import Image


def save_frames(frames: list[Image.Image], output_dir: str, prefix: str = "frame") -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for i, frame in enumerate(frames):
        frame_path = output_path / f"{prefix}_{i:06d}.png"
        frame.save(frame_path)


def assemble_video(
    frames_dir: str,
    audio_path: str,
    output_path: str,
    config: dict
) -> str:
    fps = config.get("fps", 30)
    resolution = config.get("resolution", [1920, 1080])
    
    frames_pattern = f"{frames_dir}/frame_%06d.png"
    
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", frames_pattern,
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-s", f"{resolution[0]}x{resolution[1]}",
        "-shortest",
        output_path
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    
    return output_path
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_video_builder.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/video_builder.py tests/test_video_builder.py
git commit -m "feat: add video builder with ffmpeg assembly"
```

---

## Task 7: Main CLI Entry Point

**Files:**
- Create: `src/main.py`
- Create: `tests/test_main.py`

**Step 1: Write the failing test**

```python
# tests/test_main.py
import pytest
from click.testing import CliRunner
from src.main import cli


def test_cli_missing_input():
    runner = CliRunner()
    result = runner.invoke(cli, ["nonexistent.txt"])
    assert result.exit_code != 0


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Generate subtitle video" in result.output
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_main.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.main'"

**Step 3: Add click dependency to pyproject.toml**

```toml
dependencies = [
    "Pillow>=10.0.0",
    "PyYAML>=6.0",
    "click>=8.0.0",
]
```

**Step 4: Write minimal implementation**

```python
# src/main.py
import click
import logging
from pathlib import Path
from typing import Optional

from src.config import load_config, get_default_config
from src.parser import split_sentences
from src.frame_generator import generate_sentence_frames
from src.video_builder import save_frames, assemble_video
from src.audio_builder import build_audio_track

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", default="output/video.mp4", help="Output video path")
@click.option("-c", "--config", "config_path", type=click.Path(exists=True), help="Config file path")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
def cli(input_file: str, output: str, config_path: Optional[str], verbose: bool):
    """Generate subtitle video with typing sounds from text file."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    config = load_config(config_path) if config_path else get_default_config()
    
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    if not text.strip():
        logger.error("Input file is empty")
        raise SystemExit(1)
    
    sentences = split_sentences(text)
    logger.info(f"Found {len(sentences)} sentences")
    
    font_path = config["style"].get("font_path")
    if font_path and not Path(font_path).exists():
        logger.warning(f"Font file not found: {font_path}, using default")
        font_path = None
    
    sound_path = config["audio"]["typing_sound"]
    if not Path(sound_path).exists():
        logger.error(f"Sound file not found: {sound_path}")
        raise SystemExit(1)
    
    all_frames = []
    for i, sentence in enumerate(sentences):
        logger.debug(f"Generating frames for sentence {i+1}/{len(sentences)}")
        frames = generate_sentence_frames(sentence, config["style"], font_path)
        all_frames.extend(frames)
    
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    
    frames_dir = "frames"
    Path(frames_dir).mkdir(exist_ok=True)
    
    save_frames(all_frames, frames_dir)
    logger.info(f"Saved {len(all_frames)} frames")
    
    audio_output = "temp_audio.wav"
    build_audio_track(sentences, sound_path, audio_output, config["audio"])
    logger.info("Built audio track")
    
    assemble_video(frames_dir, audio_output, output, config["video"])
    logger.info(f"Video saved to {output}")
    
    Path(audio_output).unlink(missing_ok=True)
    for frame in Path(frames_dir).glob("*.png"):
        frame.unlink()


def main():
    cli()


if __name__ == "__main__":
    main()
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_main.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/main.py tests/test_main.py pyproject.toml
git commit -m "feat: add CLI entry point with full pipeline"
```

---

## Task 8: ffmpeg Check Utility

**Files:**
- Create: `src/utils.py`
- Create: `tests/test_utils.py`

**Step 1: Write the failing test**

```python
# tests/test_utils.py
import pytest
from src.utils import check_ffmpeg


def test_check_ffmpeg():
    result = check_ffmpeg()
    assert isinstance(result, bool)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_utils.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.utils'"

**Step 3: Write minimal implementation**

```python
# src/utils.py
import subprocess
import shutil


def check_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def verify_ffmpeg() -> None:
    if not check_ffmpeg():
        raise RuntimeError(
            "ffmpeg not found. Please install ffmpeg:\n"
            "  Windows: winget install ffmpeg\n"
            "  macOS: brew install ffmpeg\n"
            "  Linux: apt install ffmpeg"
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_utils.py -v`
Expected: PASS

**Step 5: Update main.py to use verify_ffmpeg**

Add import and call at the start of cli():

```python
from src.utils import verify_ffmpeg

def cli(...):
    verify_ffmpeg()
    # ... rest of function
```

**Step 6: Commit**

```bash
git add src/utils.py tests/test_utils.py src/main.py
git commit -m "feat: add ffmpeg verification utility"
```

---

## Task 9: Integration Test

**Files:**
- Create: `tests/test_integration.py`
- Create: `tests/fixtures/test_sound.wav` (placeholder)

**Step 1: Write integration test**

```python
# tests/test_integration.py
import pytest
import tempfile
from pathlib import Path
from PIL import Image
import subprocess

pytestmark = pytest.mark.skipif(
    not subprocess.run(["which", "ffmpeg"], capture_output=True).returncode == 0,
    reason="ffmpeg not installed"
)


@pytest.fixture
def test_sound(tmp_path):
    sound_path = tmp_path / "test_sound.wav"
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "sine=frequency=440:duration=0.1",
        str(sound_path)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return str(sound_path)


def test_full_pipeline(tmp_path, test_sound):
    from src.main import cli
    from click.testing import CliRunner
    
    input_file = tmp_path / "input.txt"
    input_file.write_text("Test sentence.", encoding="utf-8")
    
    output_file = tmp_path / "output.mp4"
    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"""
video:
  resolution: [640, 480]
  fps: 30
  format: mp4
style:
  font_size: 24
  text_color: "#FFFFFF"
  background_color: "#000000"
  text_position: [50, 200]
audio:
  typing_sound: {test_sound}
  pitch_variation:
    min: 1.0
    max: 1.0
    random: false
  character_duration_ms: 50
  sentence_pause_ms: 100
parsing:
  sentence_enders: [".", "!", "?"]
""")
    
    runner = CliRunner()
    result = runner.invoke(cli, [
        str(input_file),
        "-o", str(output_file),
        "-c", str(config_file)
    ])
    
    assert result.exit_code == 0
    assert output_file.exists()
    
    probe_cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=duration",
        "-of", "csv=p=0",
        str(output_file)
    ]
    probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
    duration = float(probe_result.stdout.strip())
    assert duration > 0
```

**Step 2: Run integration test**

Run: `pytest tests/test_integration.py -v -m "not skip"`
Expected: May skip if ffmpeg not available, otherwise PASS

**Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration test for full pipeline"
```

---

## Task 10: Documentation and Final Polish

**Files:**
- Create: `README.md`
- Update: `pyproject.toml`

**Step 1: Create README.md**

```markdown
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
```

**Step 2: Update pyproject.toml with README**

Add to project section:

```toml
readme = "README.md"
license = {text = "MIT"}
```

**Step 3: Run all tests**

Run: `pytest -v`
Expected: All tests pass

**Step 4: Commit**

```bash
git add README.md pyproject.toml
git commit -m "docs: add README and finalize project metadata"
```

---

## Verification

After all tasks complete, verify:

```bash
pytest -v --cov=src
sans-sub --help
```

Expected: All tests pass, CLI shows help message.