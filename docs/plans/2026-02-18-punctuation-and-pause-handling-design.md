# Punctuation and Pause Handling Design

## Problem Statement

1. Punctuation characters generate typing sounds, which sounds unnatural
2. Pause markers (，、,) are defined in config but never implemented — no pause occurs in audio or video

## Solution Overview

Process characters individually with special handling:
- **Non-punctuation**: Animated in with sound (current behavior)
- **Punctuation**: Appears instantly with previous character's frame (no animation, no sound)
- **Pause markers**: Appear instantly, then trigger a silent pause before next character

## Implementation Details

### Frame Generation (`frame_generator.py`)

Add helper functions:
```python
def is_punctuation(char: str) -> bool:
    # Non-letter, non-number, non-space characters
    
def is_pause_marker(char: str, pause_chars: list[str]) -> bool:
    # Check against configurable pause markers
```

Modify `generate_sentence_frames`:
- Track whether previous character was a "sound-producing" character
- For punctuation: include in the visible text but don't add extra frames
- For pause markers: include in visible text, then add silent frames using `generate_pause_frames`

### Audio Generation (`audio_builder.py`)

Modify `build_audio_track`:
- Skip sound clip generation for punctuation characters
- Insert silence clips when pause markers are encountered
- Use configurable `character_pause_ms` for pause marker duration (distinct from `sentence_pause_ms`)

### Configuration (`config.yaml`)

Add new config option:
```yaml
audio:
  character_pause_ms: 200  # Pause duration for pause markers (，、,)
```

The existing `sentence_pauses` list in parsing section will be used by the frame/audio generators.

### Main Pipeline (`main.py`)

Pass `sentence_pauses` config to frame and audio generators so they can identify pause markers.

## Edge Cases

| Case | Behavior |
|------|----------|
| Leading punctuation | Show on first frame, no sound |
| Consecutive punctuation | Each appears instantly; pause markers stack |
| Trailing punctuation | Appears with last character frame |
| Empty sentence | Returns empty (no change) |

## Testing

- Unit tests for `is_punctuation()` and `is_pause_marker()` helpers
- Frame count tests: punctuation doesn't add extra frames
- Audio clip count tests: punctuation doesn't generate sound clips
- Pause marker tests: correct number of silent frames/clips inserted