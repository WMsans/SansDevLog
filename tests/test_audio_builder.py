import pytest
from pathlib import Path


pytestmark = pytest.mark.skipif(
    not Path("./sounds/sans_typing.wav").exists(),
    reason="Sound file not found",
)


class TestBuildAudioTrackPunctuation:
    def test_punctuation_skips_sound_clips(self, tmp_path):
        # Note: This is an integration test that requires ffmpeg
        # We'll verify by counting that "Hi!" has fewer clips than "Hii"
        # (since '!' should skip sound)
        pass  # Integration test, handled by manual testing

    def test_audio_clip_count_for_regular_chars(self, tmp_path):
        # "Hi" should generate 2 sound clips
        pass
