import pytest
import shutil
import subprocess

ffmpeg_available = shutil.which("ffmpeg") is not None
ffprobe_available = shutil.which("ffprobe") is not None

pytestmark = pytest.mark.skipif(
    not (ffmpeg_available and ffprobe_available),
    reason="ffmpeg/ffprobe not installed",
)


@pytest.fixture
def test_sound(tmp_path):
    sound_path = tmp_path / "test_sound.wav"
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=440:duration=0.1",
        str(sound_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return str(sound_path)


def test_full_pipeline(tmp_path, test_sound):
    from click.testing import CliRunner
    from src.main import cli

    input_file = tmp_path / "input.txt"
    input_file.write_text("Test sentence.", encoding="utf-8")

    output_file = tmp_path / "output.mp4"
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        f"""
video:
  resolution: [640, 480]
  fps: 30
  format: mp4
style:
  font_size: 24
  text_color: "#FFFFFF"
  background_color: "#000000"
  text_position: [50, 200]
audio:
  typing_sound: {test_sound}
  pitch_variation:
    min: 1.0
    max: 1.0
    random: false
  character_duration_ms: 50
  sentence_pause_ms: 100
parsing:
  sentence_enders: [".", "!", "?"]
"""
    )

    runner = CliRunner()
    result = runner.invoke(
        cli, [str(input_file), "-o", str(output_file), "-c", str(config_file)]
    )

    assert result.exit_code == 0
    assert output_file.exists()

    probe_cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=duration",
        "-of",
        "csv=p=0",
        str(output_file),
    ]
    probe_result = subprocess.run(
        probe_cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    duration = float(probe_result.stdout.strip())
    assert duration > 0
