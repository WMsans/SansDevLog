from typing import Optional

from PIL import Image, ImageDraw, ImageFont


def generate_sentence_frames(
    sentence: str,
    config: dict,
    font_path: Optional[str] = None,
    fps: int = 30,
    character_duration_ms: int = 50,
) -> list[Image.Image]:
    if not sentence:
        return []

    width, height = config["resolution"]
    font_size = config["font_size"]
    text_color = config["text_color"]
    bg_color = config["background_color"]
    text_x, text_y = config["text_position"]

    frames = []
    frames_per_char = max(1, round(fps * character_duration_ms / 1000))

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
        for _ in range(frames_per_char):
            frames.append(frame.copy())

    return frames
