from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from src.parser import is_punctuation, is_pause_marker


def generate_pause_frames(
    config: dict,
    fps: int = 30,
    pause_duration_ms: int = 500,
    visible_text: str = "",
    font_path: Optional[str] = None,
) -> list[Image.Image]:
    width, height = config["resolution"]
    bg_color = config["background_color"]
    pause_frames_count = max(1, round(fps * pause_duration_ms / 1000))

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

    return [frame.copy() for _ in range(pause_frames_count)]


def generate_sentence_frames(
    sentence: str,
    config: dict,
    font_path: Optional[str] = None,
    fps: int = 30,
    character_duration_ms: int = 50,
    pause_chars: Optional[list[str]] = None,
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
                for _ in range(pause_frames_count):
                    frames.append(frames[-1].copy())
        else:
            frame = Image.new("RGB", (width, height), bg_color)
            draw = ImageDraw.Draw(frame)
            draw.text((text_x, text_y), visible_text, fill=text_color, font=font)
            for _ in range(frames_per_char):
                frames.append(frame.copy())

    return frames
