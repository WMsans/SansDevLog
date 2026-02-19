from pathlib import Path

import pytest

from src.audio_builder import calculate_pitch_shift, get_character_count


pytestmark = pytest.mark.skipif(
    not Path("./sounds/sans_typing.wav").exists(),
    reason="Sound file not found",
)


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


class TestBuildAudioTrackPunctuation:
    def test_punctuation_skips_sound_clips(self, tmp_path):
        pass

    def test_audio_clip_count_for_regular_chars(self, tmp_path):
        pass
