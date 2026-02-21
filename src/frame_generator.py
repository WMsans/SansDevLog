from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from src.parser import is_punctuation, is_pause_marker


def generate_pause_frames(
    config: dict,
    fps: int = 30,
    pause_duration_ms: int = 500,
    visible_text: str = "",
    font_path: Optional[str] = None,
    elapsed_ms: float = 0.0,
) -> tuple[list[Image.Image], float]:
    """Generate static pause frames and return (frames, updated_elapsed_ms).

    Uses cumulative time tracking to avoid frame-count drift relative to audio.
    The caller passes in the running elapsed_ms; this function advances it by
    pause_duration_ms and computes frame count from the difference in the
    cumulative frame position, keeping total error within ±1 frame.
    """
    width, height = config["resolution"]
    bg_color = config["background_color"]

    frames_before = round(elapsed_ms * fps / 1000)
    elapsed_ms += pause_duration_ms
    frames_after = round(elapsed_ms * fps / 1000)
    pause_frames_count = max(1, frames_after - frames_before)

    frame = Image.new("RGB", (width, height), bg_color)

    if visible_text:
        font_size = config["font_size"]
        text_color = config["text_color"]
        text_x, text_y = config["text_position"]

        try:
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        draw = ImageDraw.Draw(frame)
        draw.text((text_x, text_y), visible_text, fill=text_color, font=font)

    return [frame.copy() for _ in range(pause_frames_count)], elapsed_ms


def generate_sentence_frames(
    sentence: str,
    config: dict,
    font_path: Optional[str] = None,
    fps: int = 30,
    character_duration_ms: int = 50,
    pause_chars: Optional[list[str]] = None,
    character_pause_ms: int = 200,
    elapsed_ms: float = 0.0,
) -> tuple[list[Image.Image], float]:
    """Generate frames for a sentence and return (frames, updated_elapsed_ms).

    Uses cumulative time tracking to stay in sync with the audio track.
    The audio builder absorbs pause-marker durations into the preceding
    character's clip (so the typing sound naturally fades into silence).
    This function mirrors that: when a pause marker follows a character,
    the elapsed time advances by character_pause_ms and the extra frames
    are copies of the last frame (showing the pause-marker text).

    The caller passes in the running elapsed_ms counter; this function
    returns the updated value so it can be threaded across sentences and
    inter-sentence pauses.
    """
    if not sentence:
        return [], elapsed_ms

    if pause_chars is None:
        pause_chars = ["，", "、", ","]

    width, height = config["resolution"]
    font_size = config["font_size"]
    text_color = config["text_color"]
    bg_color = config["background_color"]
    text_x, text_y = config["text_position"]

    frames: list[Image.Image] = []

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
            # Draw punctuation onto the last frame (in-place update)
            if len(frames) > 0:
                frame = frames[-1].copy()
                draw = ImageDraw.Draw(frame)
                draw.text((text_x, text_y), visible_text, fill=text_color, font=font)
                frames[-1] = frame
            else:
                frame = Image.new("RGB", (width, height), bg_color)
                draw = ImageDraw.Draw(frame)
                draw.text((text_x, text_y), visible_text, fill=text_color, font=font)
                frames.append(frame)

            if is_pause_marker(char, pause_chars):
                # Mirror audio_builder: absorb pause into preceding char's
                # duration so the typing sound fades naturally into silence.
                frames_before = round(elapsed_ms * fps / 1000)
                elapsed_ms += character_pause_ms
                frames_after = round(elapsed_ms * fps / 1000)
                pause_frame_count = max(1, frames_after - frames_before)
                for _ in range(pause_frame_count):
                    frames.append(frames[-1].copy())
        else:
            frame = Image.new("RGB", (width, height), bg_color)
            draw = ImageDraw.Draw(frame)
            draw.text((text_x, text_y), visible_text, fill=text_color, font=font)

            frames_before = round(elapsed_ms * fps / 1000)
            elapsed_ms += character_duration_ms
            frames_after = round(elapsed_ms * fps / 1000)
            char_frame_count = max(1, frames_after - frames_before)
            for _ in range(char_frame_count):
                frames.append(frame.copy())

    return frames, elapsed_ms
