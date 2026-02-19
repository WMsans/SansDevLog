import pytest
from PIL import Image

from src.frame_generator import generate_sentence_frames, generate_pause_frames


def test_generate_sentence_frames_count():
    config = {
        "resolution": [1920, 1080],
        "font_size": 48,
        "text_color": "#FFFFFF",
        "background_color": "#000000",
        "text_position": [100, 500],
    }
    sentence = "Hello"
    frames = generate_sentence_frames(
        sentence, config, font_path=None, fps=30, character_duration_ms=33
    )
    assert len(frames) == 5


def test_generate_pause_frames_count():
    config = {
        "resolution": [1920, 1080],
        "font_size": 48,
        "text_color": "#FFFFFF",
        "background_color": "#000000",
        "text_position": [100, 500],
    }
    frames = generate_pause_frames(config, fps=30, pause_duration_ms=1000)
    assert len(frames) == 30


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
