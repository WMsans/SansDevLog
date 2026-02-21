import subprocess
from pathlib import Path
from PIL import Image
from typing import Iterator

def assemble_video_stream(
    frames_iterator: Iterator[Image.Image],
    audio_path: str,
    output_path: str,
    config: dict,
) -> str:
    fps = config.get("fps", 30)
    resolution = config.get("resolution", [1920, 1080])

    cmd = [
        "ffmpeg",
        "-y",
        # Input settings for raw video stream from stdin
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{resolution[0]}x{resolution[1]}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",  # Read frames from standard input
        
        # Audio input
        "-i", audio_path,
        
        # Video encoding settings (Hardware acceleration using nvenc)
        "-c:v", "h264_nvenc",
        "-preset", "p4",        # NVENC preset (p4 is medium/good balance)
        "-cq", "23",            # NVENC constant quality target
        
        # Audio encoding settings
        "-c:a", "aac",
        "-b:a", "128k",
        
        # Output settings
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path,
    ]

    # Open subprocess with stdin piped
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    try:
        # Stream frames directly to ffmpeg
        for frame in frames_iterator:
            process.stdin.write(frame.convert("RGB").tobytes())
    except Exception as e:
        process.stdin.close()
        process.terminate()
        raise e

    # Close stdin to signal ffmpeg that the stream is finished
    process.stdin.close()
    process.wait()

    if process.returncode != 0:
        raise RuntimeError("FFmpeg encoding failed.")

    return output_path
