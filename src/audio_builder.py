import random
import subprocess
from pathlib import Path

from src.parser import is_pause_marker, is_punctuation


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
    pause_chars: list[str] | None = None,
) -> str:
    if pause_chars is None:
        pause_chars = ["，", "、", ","]

    char_duration_ms = config.get("character_duration_ms", 50)
    sentence_pause_ms = config.get("sentence_pause_ms", 500)
    character_pause_ms = config.get("character_pause_ms", 200)
    audio_props = get_audio_properties(sound_path)
    sample_rate = audio_props["sample_rate"]
    channels = audio_props["channels"]
    channel_layout = "stereo" if channels >= 2 else "mono"

    audio_clips = []
    temp_files = []

    for i, sentence in enumerate(sentences):
        pitch = calculate_pitch_shift(config)
        clips_to_generate = []

        # Group durations to allow sounds to naturally decay into pauses
        for char_idx, char in enumerate(sentence):
            if is_punctuation(char):
                if is_pause_marker(char, pause_chars):
                    # If there's an active character before this pause, let it ring out by absorbing the pause
                    if clips_to_generate and clips_to_generate[-1]["type"] == "char":
                        clips_to_generate[-1]["duration"] += character_pause_ms
                    else:
                        clips_to_generate.append(
                            {
                                "type": "silence",
                                "duration": character_pause_ms,
                                "char_idx": char_idx,
                            }
                        )
                continue

            clips_to_generate.append(
                {"type": "char", "duration": char_duration_ms, "char_idx": char_idx}
            )

        # Add the sentence pause (line break / sentence end padding)
        if i < len(sentences) - 1:
            if clips_to_generate and clips_to_generate[-1]["type"] == "char":
                clips_to_generate[-1]["duration"] += sentence_pause_ms
            else:
                clips_to_generate.append(
                    {
                        "type": "silence",
                        "duration": sentence_pause_ms,
                        "char_idx": "end",
                    }
                )

        # Generate the scheduled clips
        for clip_info in clips_to_generate:
            duration_ms = clip_info["duration"]
            idx = clip_info["char_idx"]

            if clip_info["type"] == "char":
                temp_clip = f"temp_char_{i}_{idx}.wav"
                temp_files.append(temp_clip)

                duration_s = duration_ms / 1000
                fade_ms = 10
                fade_s = fade_ms / 1000
                fade_start_s = max(0, duration_s - fade_s)

                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    sound_path,
                    "-af",
                    (
                        f"asetrate={sample_rate}*{pitch},"
                        f"atempo=1/{pitch},"
                        f"aresample={sample_rate},"
                        f"apad=whole_dur={duration_ms}ms,"
                        f"afade=t=out:st={fade_start_s}:d={fade_s}"
                    ),
                    "-t",
                    f"{duration_s}",
                    temp_clip,
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                audio_clips.append(temp_clip)
            else:
                silence_path = f"temp_silence_{i}_{idx}.wav"
                temp_files.append(silence_path)

                silence_cmd = [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    f"anullsrc=r={sample_rate}:cl={channel_layout}",
                    "-t",
                    f"{duration_ms / 1000}",
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
