import subprocess
from pathlib import Path
from PIL import Image


def save_frames(
    frames: list[Image.Image], output_dir: str, prefix: str = "frame"
) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for i, frame in enumerate(frames):
        frame_path = output_path / f"{prefix}_{i:06d}.png"
        frame.save(frame_path)


def assemble_video(
    frames_dir: str,
    audio_path: str,
    output_path: str,
    config: dict,
    prefix: str = "frame",
) -> str:
    fps = config.get("fps", 30)
    resolution = config.get("resolution", [1920, 1080])

    frames_pattern = f"{frames_dir}/{prefix}_%06d.png"

    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        frames_pattern,
        "-i",
        audio_path,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-pix_fmt",
        "yuv420p",
        "-s",
        f"{resolution[0]}x{resolution[1]}",
        "-shortest",
        output_path,
    ]

    subprocess.run(cmd, check=True, capture_output=True)

    return output_path
