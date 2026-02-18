import click
import shutil


def check_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def verify_ffmpeg() -> None:
    if not check_ffmpeg():
        raise click.ClickException(
            "ffmpeg not found. Please install ffmpeg:\n"
            "  Windows: winget install ffmpeg\n"
            "  macOS: brew install ffmpeg\n"
            "  Linux: apt install ffmpeg"
        )
