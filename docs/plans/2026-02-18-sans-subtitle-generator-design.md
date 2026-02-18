# Sans Subtitle Generator - Design Document

## Overview

A Python tool that generates video files with typed subtitles synchronized to typing sounds. Designed for Chinese text mixed with English, featuring configurable visual style and pitch-varied audio per sentence.

## Requirements

- Parse plain text files and split into sentences
- Generate video with per-character subtitle animation
- Sync subtitle typing with audio typing sounds
- Support Chinese mixed with English text with Chinese punctuation
- Configurable visual style (font, colors, position)
- Pitch variation per sentence for typing sounds
- Output: 1080p 30fps MP4 video

## Architecture

```
sans-subtitle-generator/
├── src/
│   ├── __init__.py
│   ├── main.py              # CLI entry point
│   ├── parser.py            # Text parsing & sentence splitting
│   ├── frame_generator.py   # PIL-based frame generation
│   ├── audio_builder.py     # Audio concatenation with pitch shifts
│   └── video_builder.py     # ffmpeg video assembly
├── config.yaml              # Default configuration
├── sounds/                  # Default typing sounds (user provides)
├── fonts/                   # Default fonts (user provides)
└── output/                  # Generated videos
```

## Components

### parser.py

- `split_sentences(text: str) -> list[str]`: Splits on Chinese (。！？) and English (. ! ?) punctuation
- Handles mixed Chinese/English text, preserves punctuation with sentence

### frame_generator.py

- `generate_sentence_frames(sentence: str, config: dict) -> list[Image]`:
  - Creates one frame per character
  - Uses Pillow with configurable font, color, background
  - Each frame shows accumulated text up to current character
  - Returns list of PIL Image objects

### audio_builder.py

- `build_audio_track(sentences: list[str], sound_path: str, config: dict) -> str`:
  - Loads base typing sound
  - For each sentence, applies pitch shift (configurable range)
  - Concatenates sounds matching character count
  - Outputs temporary audio file

### video_builder.py

- `assemble_video(frames_dir: str, audio_path: str, output_path: str, config: dict)`:
  - Uses ffmpeg to encode frames at 30fps
  - Merges with audio track
  - Outputs 1080p H.264 MP4

## Data Flow

```
input.txt
    │
    ▼
┌─────────────┐
│   parser    │ ──→ sentences: ["Sentence 1。", "Sentence 2?", ...]
└─────────────┘
    │
    ▼
┌──────────────────────┐     ┌──────────────────┐
│  frame_generator     │     │   audio_builder  │
│  (per sentence)      │     │  (per sentence)  │
└──────────────────────┘     └──────────────────┘
    │                              │
    ▼                              ▼
frames/sentence_001/         audio_track.wav
  frame_001.png                (with pitch shifts)
  frame_002.png
  ...
    │                              │
    └──────────┬───────────────────┘
               ▼
       ┌───────────────┐
       │ video_builder │
       └───────────────┘
               │
               ▼
          output.mp4
```

**Timing logic:**
- Each character = 1 frame at 30fps (~33ms per character)
- Audio clips are trimmed/padded to match frame duration
- Gap between sentences = configurable pause (default 0.5s)

## Configuration

**config.yaml:**
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
  text_position: [100, 500]  # x, y position

audio:
  typing_sound: ./sounds/sans_typing.wav
  pitch_variation:
    min: 0.9   # 90% of original pitch
    max: 1.1   # 110% of original pitch
    random: true  # random within range per sentence
  character_duration_ms: 50
  sentence_pause_ms: 500

parsing:
  sentence_enders: ["。", "！", "？", ".", "!", "?"]
  sentence_pauses: ["，", "、", ","]  # adds extra pause within sentence
```

**CLI usage:**
```bash
python -m src.main input.txt -o output.mp4 --config config.yaml
```

## Error Handling

- **Missing font file**: Exit with clear error message showing required path
- **Missing sound file**: Exit with clear error message showing required path
- **Invalid text encoding**: Auto-detect encoding (UTF-8, GBK), warn if fallback used
- **ffmpeg not found**: Check at startup, exit with installation instructions
- **Empty input file**: Warn and exit gracefully
- **Frame generation failure**: Log to stderr, continue with next sentence

All errors use Python's `logging` module with configurable verbosity (`-v` flag).

## Testing

**Unit tests** (pytest):
- `test_parser.py`: Sentence splitting for Chinese, English, mixed text
- `test_frame_generator.py`: Frame dimensions, text positioning, font loading
- `test_audio_builder.py`: Pitch shifting, audio duration calculation

**Integration tests**:
- End-to-end test with sample input → verify output MP4 exists and has correct duration

**Test fixtures**:
- `tests/fixtures/sample_chinese.txt`
- `tests/fixtures/sample_mixed.txt`
- `tests/fixtures/test_sound.wav` (simple beep)

## Dependencies

- Python 3.10+
- Pillow (PIL)
- ffmpeg (system dependency)
- PyYAML
- pytest (development)