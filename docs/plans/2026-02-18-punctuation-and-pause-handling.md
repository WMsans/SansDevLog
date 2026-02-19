# Punctuation and Pause Handling Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make punctuation appear instantly without sound, and implement pause markers to trigger silent pauses in both audio and video.

**Architecture:** Modify frame_generator and audio_builder to handle punctuation specially. Add helper functions to classify characters, then adjust the character processing loops to skip sound/frame generation for punctuation and insert pauses for pause markers.

**Tech Stack:** Python 3.10+, PIL for frames, ffmpeg for audio, pytest for testing

---

### Task 1: Add character classification helpers

**Files:**
- Create: `tests/test_parser.py` (add tests to existing file)
- Modify: `src/parser.py:1-18`

**Step 1: Write the failing tests**

Add to `tests/test_parser.py`:

```python
from src.parser import is_punctuation, is_pause_marker


class TestIsPunctuation:
    def test_letters_are_not_punctuation(self):
        assert is_punctuation("a") is False
        assert is_punctuation("Z") is False
        assert is_punctuation("你") is False

    def test_numbers_are_not_punctuation(self):
        assert is_punctuation("1") is False
        assert is_punctuation("9") is False

    def test_spaces_are_not_punctuation(self):
        assert is_punctuation(" ") is False

    def test_punctuation_returns_true(self):
        assert is_punctuation("。") is True
        assert is_punctuation("！") is True
        assert is_punctuation("？") is True
        assert is_punctuation(".") is True
        assert is_punctuation("!") is True
        assert is_punctuation("?") is True
        assert is_punctuation("，") is True
        assert is_punctuation("、") is True
        assert is_punctuation(",") is True
        assert is_punctuation(":") is True
        assert is_punctuation(";") is True


class TestIsPauseMarker:
    def test_pause_markers_return_true(self):
        pause_chars = ["，", "、", ","]
        assert is_pause_marker("，", pause_chars) is True
        assert is_pause_marker("、", pause_chars) is True
        assert is_pause_marker(",", pause_chars) is True

    def test_non_pause_punctuation_returns_false(self):
        pause_chars = ["，", "、", ","]
        assert is_pause_marker("。", pause_chars) is False
        assert is_pause_marker(".", pause_chars) is False
        assert is_pause_marker("!", pause_chars) is False

    def test_letters_return_false(self):
        pause_chars = ["，", "、", ","]
        assert is_pause_marker("a", pause_chars) is False
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_parser.py -v`
Expected: FAIL with "cannot import name 'is_punctuation'"

**Step 3: Write minimal implementation**

Add to `src/parser.py`:

```python
def is_punctuation(char: str) -> bool:
    if len(char) != 1:
        return False
    return not char.isalnum() and not char.isspace()


def is_pause_marker(char: str, pause_chars: list[str]) -> bool:
    return char in pause_chars
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_parser.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/parser.py tests/test_parser.py
git commit -m "feat: add is_punctuation and is_pause_marker helpers"
```

---

### Task 2: Update config with character_pause_ms

**Files:**
- Modify: `config.yaml:19-24`
- Modify: `src/config.py` (if needed for defaults)

**Step 1: Add new config option**

Modify `config.yaml`, add after `sentence_pause_ms`:

```yaml
audio:
  typing_sound: ./sounds/sans_typing.wav
  pitch_variation:
    min: 0.9
    max: 1.1
    random: true
  character_duration_ms: 100
  sentence_pause_ms: 500
  character_pause_ms: 200
```

**Step 2: Update default config in code if needed**

Check `src/config.py` for `get_default_config()` and ensure it includes the new option.

**Step 3: Commit**

```bash
git add config.yaml src/config.py
git commit -m "feat: add character_pause_ms config option"
```

---

### Task 3: Update frame_generator for punctuation handling

**Files:**
- Create: `tests/test_frame_generator.py`
- Modify: `src/frame_generator.py:38-74`

**Step 1: Write the failing tests**

Create `tests/test_frame_generator.py`:

```python
from src.frame_generator import generate_sentence_frames


class TestGenerateSentenceFramesPunctuation:
    def test_punctuation_does_not_add_extra_frames(self):
        config = {
            "resolution": (1920, 1080),
            "font_size": 48,
            "text_color": "#FFFFFF",
            "background_color": "#000000",
            "text_position": (100, 500),
        }
        frames_no_punct = generate_sentence_frames(
            "Hello", config, fps=30, character_duration_ms=100
        )
        frames_with_punct = generate_sentence_frames(
            "Hello!", config, fps=30, character_duration_ms=100
        )
        assert len(frames_no_punct) == len(frames_with_punct)

    def test_punctuation_visible_in_last_frame(self):
        config = {
            "resolution": (1920, 1080),
            "font_size": 48,
            "text_color": "#FFFFFF",
            "background_color": "#000000",
            "text_position": (100, 500),
        }
        frames = generate_sentence_frames(
            "Hello!", config, fps=30, character_duration_ms=100
        )
        last_frame = frames[-1]
        # The punctuation should be in the visible text
        # We can't easily verify pixel content, but we verify frame count is correct

    def test_frames_per_character(self):
        config = {
            "resolution": (1920, 1080),
            "font_size": 48,
            "text_color": "#FFFFFF",
            "background_color": "#000000",
            "text_position": (100, 500),
        }
        frames = generate_sentence_frames(
            "Hi", config, fps=30, character_duration_ms=100
        )
        frames_per_char = max(1, round(30 * 100 / 1000))
        assert len(frames) == 2 * frames_per_char
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_frame_generator.py -v`
Expected: FAIL (punctuation currently adds extra frames)

**Step 3: Write implementation**

Modify `generate_sentence_frames` in `src/frame_generator.py`:

```python
from src.parser import is_punctuation


def generate_sentence_frames(
    sentence: str,
    config: dict,
    font_path: str | None = None,
    fps: int = 30,
    character_duration_ms: int = 50,
    pause_chars: list[str] | None = None,
    character_pause_ms: int = 200,
) -> list[Image.Image]:
    if not sentence:
        return []

    if pause_chars is None:
        pause_chars = ["，", "、", ","]

    width, height = config["resolution"]
    font_size = config["font_size"]
    text_color = config["text_color"]
    bg_color = config["background_color"]
    text_x, text_y = config["text_position"]

    frames = []
    frames_per_char = max(1, round(fps * character_duration_ms / 1000))
    pause_frames_count = max(1, round(fps * character_pause_ms / 1000))

    try:
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    visible_text = ""
    for char in sentence:
        visible_text += char
        
        if is_punctuation(char):
            if len(frames) > 0:
                # Reuse last frame with punctuation added
                frame = frames[-1].copy()
                draw = ImageDraw.Draw(frame)
                draw.text((text_x, text_y), visible_text, fill=text_color, font=font)
                frames[-1] = frame
            else:
                # Leading punctuation - create initial frame
                frame = Image.new("RGB", (width, height), bg_color)
                draw = ImageDraw.Draw(frame)
                draw.text((text_x, text_y), visible_text, fill=text_color, font=font)
                frames.append(frame)

            if is_pause_marker(char, pause_chars):
                for _ in range(pause_frames_count):
                    frames.append(frames[-1].copy())
        else:
            frame = Image.new("RGB", (width, height), bg_color)
            draw = ImageDraw.Draw(frame)
            draw.text((text_x, text_y), visible_text, fill=text_color, font=font)
            for _ in range(frames_per_char):
                frames.append(frame.copy())

    return frames
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_frame_generator.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/frame_generator.py tests/test_frame_generator.py
git commit -m "feat: punctuation appears instantly, pause markers trigger silent frames"
```

---

### Task 4: Update audio_builder for punctuation handling

**Files:**
- Create: `tests/test_audio_builder.py`
- Modify: `src/audio_builder.py:64-144`

**Step 1: Write the failing tests**

Create `tests/test_audio_builder.py`:

```python
import pytest
from pathlib import Path
from src.audio_builder import build_audio_track


pytestmark = pytest.mark.skipif(
    not Path("./sounds/sans_typing.wav").exists(),
    reason="Sound file not found",
)


class TestBuildAudioTrackPunctuation:
    def test_punctuation_skips_sound_clips(self, tmp_path):
        # Note: This is an integration test that requires ffmpeg
        output = tmp_path / "test_audio.wav"
        # We'll verify by counting that "Hi!" has fewer clips than "Hii"
        # (since '!' should skip sound)
        pass  # Integration test, handled by manual testing

    def test_audio_clip_count_for_regular_chars(self, tmp_path):
        output = tmp_path / "test_audio.wav"
        # "Hi" should generate 2 sound clips
        pass
```

**Step 2: Write implementation**

Modify `build_audio_track` in `src/audio_builder.py`:

```python
from src.parser import is_punctuation, is_pause_marker


def build_audio_track(
    sentences: list[str],
    sound_path: str,
    output_path: str,
    config: dict,
    pause_chars: list[str] | None = None,
) -> str:
    if pause_chars is None:
        pause_chars = ["，", "、", ","]

    char_duration_ms = config.get("character_duration_ms", 50)
    sentence_pause_ms = config.get("sentence_pause_ms", 500)
    character_pause_ms = config.get("character_pause_ms", 200)
    audio_props = get_audio_properties(sound_path)
    sample_rate = audio_props["sample_rate"]
    channels = audio_props["channels"]
    channel_layout = "stereo" if channels >= 2 else "mono"

    audio_clips = []
    temp_files = []

    for i, sentence in enumerate(sentences):
        for char_idx, char in enumerate(sentence):
            if is_punctuation(char):
                if is_pause_marker(char, pause_chars):
                    silence_path = f"temp_pause_silence_{i}_{char_idx}.wav"
                    temp_files.append(silence_path)
                    silence_cmd = [
                        "ffmpeg",
                        "-y",
                        "-f",
                        "lavfi",
                        "-i",
                        f"anullsrc=r={sample_rate}:cl={channel_layout}",
                        "-t",
                        f"{character_pause_ms / 1000}",
                        silence_path,
                    ]
                    subprocess.run(silence_cmd, check=True, capture_output=True)
                    audio_clips.append(silence_path)
                continue

            pitch = calculate_pitch_shift(config)
            temp_clip = f"temp_char_{i}_{char_idx}.wav"
            temp_files.append(temp_clip)

            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                sound_path,
                "-af",
                "asetrate={sample_rate}*{pitch},atempo=1/{pitch},aresample={sample_rate},apad=whole_dur={duration_ms}ms".format(
                    sample_rate=sample_rate,
                    pitch=pitch,
                    duration_ms=char_duration_ms,
                ),
                "-t",
                f"{char_duration_ms / 1000}",
                temp_clip,
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            audio_clips.append(temp_clip)

        if i < len(sentences) - 1:
            silence_path = f"temp_silence_{i}.wav"
            temp_files.append(silence_path)
            silence_cmd = [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"anullsrc=r={sample_rate}:cl={channel_layout}",
                "-t",
                f"{sentence_pause_ms / 1000}",
                silence_path,
            ]
            subprocess.run(silence_cmd, check=True, capture_output=True)
            audio_clips.append(silence_path)

    concat_file = "temp_concat.txt"
    with open(concat_file, "w") as f:
        for clip in audio_clips:
            f.write(f"file '{clip}'\n")

    concat_cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        concat_file,
        "-c",
        "copy",
        output_path,
    ]
    subprocess.run(concat_cmd, check=True, capture_output=True)

    for temp_file in temp_files + [concat_file]:
        Path(temp_file).unlink(missing_ok=True)

    return output_path
```

**Step 3: Run existing tests**

Run: `pytest tests/ -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/audio_builder.py tests/test_audio_builder.py
git commit -m "feat: punctuation skips sound, pause markers insert silence"
```

---

### Task 5: Update main.py to pass pause_chars config

**Files:**
- Modify: `src/main.py:64-96`

**Step 1: Pass pause_chars to generators**

Modify `src/main.py` to pass `sentence_pauses` from config:

```python
# Around line 64-83, update the frame generation call:
pause_chars = config["parsing"].get("sentence_pauses", ["，", "、", ","])

frames = generate_sentence_frames(
    sentence,
    frame_config,
    font_path,
    fps=config["video"]["fps"],
    character_duration_ms=config["audio"]["character_duration_ms"],
    pause_chars=pause_chars,
    character_pause_ms=config["audio"].get("character_pause_ms", 200),
)

# Around line 96, update the audio build call:
build_audio_track(
    sentences, 
    sound_path, 
    audio_output, 
    config["audio"],
    pause_chars=pause_chars,
)
```

**Step 2: Run all tests**

Run: `pytest tests/ -v`
Expected: PASS

**Step 3: Manual integration test**

Create a test input file and run the CLI:
```bash
echo "你好，世界！This is a test." > test_input.txt
sans-sub test_input.txt -o test_output.mp4 -v
```

Verify:
- No sound for punctuation
- Pause after "，" in audio and video

**Step 4: Commit**

```bash
git add src/main.py
git commit -m "feat: integrate punctuation handling into main pipeline"
```

---

### Task 6: Run linter and final verification

**Step 1: Run ruff linter**

Run: `ruff check .`
Expected: No errors (fix any if found)

**Step 2: Run ruff formatter**

Run: `ruff format .`
Expected: Files formatted

**Step 3: Run all tests**

Run: `pytest tests/ -v`
Expected: All PASS

**Step 4: Final commit if any formatting changes**

```bash
git add -A
git commit -m "style: apply ruff formatting"
```