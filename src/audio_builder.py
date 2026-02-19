import random
import subprocess
from pathlib import Path


def get_character_count(sentences: list[str]) -> list[int]:
    return [len(sentence) for sentence in sentences]


def calculate_pitch_shift(config: dict, seed: int | None = None) -> float:
    pitch_config = config.get("pitch_variation", {})
    min_pitch = pitch_config.get("min", 0.9)
    max_pitch = pitch_config.get("max", 1.1)
    is_random = pitch_config.get("random", True)

    rng = random.Random(seed) if seed is not None else random

    if is_random:
        return rng.uniform(min_pitch, max_pitch)
    else:
        return (min_pitch + max_pitch) / 2


def get_audio_properties(sound_path: str) -> dict:
    """Return sample_rate and channels for the first audio stream."""
    probe_cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=sample_rate,channels",
        "-of",
        "default=nw=1:nk=1",
        sound_path,
    ]
    defaults = {"sample_rate": 44100, "channels": 2}
    try:
        probe_result = subprocess.run(
            probe_cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return defaults
    if probe_result.returncode != 0:
        return defaults
    try:
        lines = probe_result.stdout.strip().splitlines()
        return {
            "sample_rate": int(lines[0]),
            "channels": int(lines[1]),
        }
    except (ValueError, IndexError):
        return defaults


def get_audio_sample_rate(sound_path: str) -> int:
    return get_audio_properties(sound_path)["sample_rate"]


def build_audio_track(
    sentences: list[str],
    sound_path: str,
    output_path: str,
    config: dict,
) -> str:
    char_duration_ms = config.get("character_duration_ms", 50)
    sentence_pause_ms = config.get("sentence_pause_ms", 500)
    audio_props = get_audio_properties(sound_path)
    sample_rate = audio_props["sample_rate"]
    channels = audio_props["channels"]
    channel_layout = "stereo" if channels >= 2 else "mono"

    audio_clips = []
    temp_files = []

    for i, sentence in enumerate(sentences):
        for char_idx in range(len(sentence)):
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
