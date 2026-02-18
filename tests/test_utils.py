from src.utils import check_ffmpeg


def test_check_ffmpeg():
    result = check_ffmpeg()
    assert isinstance(result, bool)
