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
    frames, elapsed = generate_sentence_frames(
        sentence, config, font_path=None, fps=30, character_duration_ms=33
    )
    assert len(frames) == 5
    assert elapsed == 5 * 33


def test_generate_pause_frames_count():
    config = {
        "resolution": [1920, 1080],
        "font_size": 48,
        "text_color": "#FFFFFF",
        "background_color": "#000000",
        "text_position": [100, 500],
    }
    frames, elapsed = generate_pause_frames(config, fps=30, pause_duration_ms=1000)
    assert len(frames) == 30
    assert elapsed == 1000


def test_generate_sentence_frames_dimensions():
    config = {
        "resolution": [1920, 1080],
        "font_size": 48,
        "text_color": "#FFFFFF",
        "background_color": "#000000",
        "text_position": [100, 500],
    }
    sentence = "Test"
    frames, _ = generate_sentence_frames(sentence, config, font_path=None)
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
    frames, elapsed = generate_sentence_frames("", config, font_path=None)
    assert frames == []
    assert elapsed == 0.0


class TestGenerateSentenceFramesPunctuation:
    def test_punctuation_does_not_add_extra_frames(self):
        config = {
            "resolution": [1920, 1080],
            "font_size": 48,
            "text_color": "#FFFFFF",
            "background_color": "#000000",
            "text_position": [100, 500],
        }
        frames_no_punct, _ = generate_sentence_frames(
            "Hello", config, fps=30, character_duration_ms=100
        )
        frames_with_punct, _ = generate_sentence_frames(
            "Hello!", config, fps=30, character_duration_ms=100
        )
        assert len(frames_no_punct) == len(frames_with_punct)

    def test_punctuation_visible_in_last_frame(self):
        config = {
            "resolution": [1920, 1080],
            "font_size": 48,
            "text_color": "#FFFFFF",
            "background_color": "#000000",
            "text_position": [100, 500],
        }
        frames, _ = generate_sentence_frames(
            "Hello!", config, fps=30, character_duration_ms=100
        )
        assert len(frames) > 0
        assert frames[-1] is not None

    def test_frames_per_character(self):
        config = {
            "resolution": [1920, 1080],
            "font_size": 48,
            "text_color": "#FFFFFF",
            "background_color": "#000000",
            "text_position": [100, 500],
        }
        frames, _ = generate_sentence_frames(
            "Hi", config, fps=30, character_duration_ms=100
        )
        frames_per_char = max(1, round(30 * 100 / 1000))
        assert len(frames) == 2 * frames_per_char


class TestCumulativeTimeTracking:
    """Verify that cumulative tracking eliminates drift."""

    def test_elapsed_ms_matches_audio_duration(self):
        """Total elapsed_ms must equal sum of character durations (what audio uses)."""
        config = {
            "resolution": [1920, 1080],
            "font_size": 48,
            "text_color": "#FFFFFF",
            "background_color": "#000000",
            "text_position": [100, 500],
        }
        # 20 non-punctuation chars at 80ms each = 1600ms audio
        sentence = "abcdefghijklmnopqrst"
        _, elapsed = generate_sentence_frames(
            sentence, config, fps=30, character_duration_ms=80
        )
        assert elapsed == 20 * 80

    def test_pause_marker_absorbed_into_elapsed(self):
        """Pause marker duration is added to elapsed, matching audio absorption."""
        config = {
            "resolution": [1920, 1080],
            "font_size": 48,
            "text_color": "#FFFFFF",
            "background_color": "#000000",
            "text_position": [100, 500],
        }
        # "ab，cd" -> 4 chars at 80ms + 1 pause at 250ms = 570ms
        sentence = "ab，cd"
        _, elapsed = generate_sentence_frames(
            sentence,
            config,
            fps=30,
            character_duration_ms=80,
            character_pause_ms=250,
        )
        assert elapsed == 4 * 80 + 250

    def test_frame_count_stays_close_to_audio_duration(self):
        """Total video duration should be within 1 frame of audio duration."""
        config = {
            "resolution": [1920, 1080],
            "font_size": 48,
            "text_color": "#FFFFFF",
            "background_color": "#000000",
            "text_position": [100, 500],
        }
        fps = 30
        char_ms = 80
        sentence = "a" * 100  # 100 chars -> 8000ms audio
        frames, elapsed = generate_sentence_frames(
            sentence, config, fps=fps, character_duration_ms=char_ms
        )
        audio_duration_ms = 100 * char_ms
        video_duration_ms = len(frames) / fps * 1000
        # Drift must be less than one frame duration
        assert abs(video_duration_ms - audio_duration_ms) <= 1000 / fps + 0.01

    def test_elapsed_threads_across_calls(self):
        """elapsed_ms from one call can seed the next for cross-sentence sync."""
        config = {
            "resolution": [1920, 1080],
            "font_size": 48,
            "text_color": "#FFFFFF",
            "background_color": "#000000",
            "text_position": [100, 500],
        }
        fps = 30
        frames1, elapsed1 = generate_sentence_frames(
            "Hello", config, fps=fps, character_duration_ms=80, elapsed_ms=0.0
        )
        pause_frames, elapsed2 = generate_pause_frames(
            config, fps=fps, pause_duration_ms=1000, elapsed_ms=elapsed1
        )
        frames2, elapsed3 = generate_sentence_frames(
            "World", config, fps=fps, character_duration_ms=80, elapsed_ms=elapsed2
        )
        total_audio_ms = 5 * 80 + 1000 + 5 * 80
        assert elapsed3 == total_audio_ms
        total_frames = len(frames1) + len(pause_frames) + len(frames2)
        video_ms = total_frames / fps * 1000
        assert abs(video_ms - total_audio_ms) <= 1000 / fps + 0.01
