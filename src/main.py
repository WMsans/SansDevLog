import click
import logging
import tempfile
from pathlib import Path
from typing import Optional

from src.config import load_config, get_default_config
from src.parser import split_sentences
from src.frame_generator import generate_sentence_frames, generate_pause_frames
from src.video_builder import save_frames, assemble_video
from src.audio_builder import build_audio_track
from src.utils import verify_ffmpeg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", default="output/video.mp4", help="Output video path")
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True),
    help="Config file path",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
def cli(input_file: str, output: str, config_path: Optional[str], verbose: bool):
    """Generate subtitle video with typing sounds from text file."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    verify_ffmpeg()

    config = load_config(config_path) if config_path else get_default_config()

    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        logger.error("Input file is empty")
        raise SystemExit(1)

    sentences = split_sentences(text)
    logger.info(f"Found {len(sentences)} sentences")

    font_path = config["style"].get("font_path")
    if font_path and not Path(font_path).exists():
        logger.warning(f"Font file not found: {font_path}, using default")
        font_path = None

    sound_path = config["audio"]["typing_sound"]
    if not Path(sound_path).exists():
        logger.error(f"Sound file not found: {sound_path}")
        raise SystemExit(1)

    frame_config = {
        **config["style"],
        "resolution": config["video"]["resolution"],
    }

    all_frames = []
    for i, sentence in enumerate(sentences):
        logger.debug(f"Generating frames for sentence {i + 1}/{len(sentences)}")
        frames = generate_sentence_frames(
            sentence,
            frame_config,
            font_path,
            fps=config["video"]["fps"],
            character_duration_ms=config["audio"]["character_duration_ms"],
        )
        all_frames.extend(frames)

        if i < len(sentences) - 1:
            pause_frames = generate_pause_frames(
                frame_config,
                fps=config["video"]["fps"],
                pause_duration_ms=config["audio"]["sentence_pause_ms"],
                visible_text=sentence,
                font_path=font_path,
            )
            all_frames.extend(pause_frames)

    Path(output).parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        frames_dir = temp_path / "frames"
        frames_dir.mkdir(exist_ok=True)

        save_frames(all_frames, str(frames_dir))
        logger.info(f"Saved {len(all_frames)} frames")

        audio_output = str(temp_path / "temp_audio.wav")
        build_audio_track(sentences, sound_path, audio_output, config["audio"])
        logger.info("Built audio track")

        assemble_video(str(frames_dir), audio_output, output, config["video"])
        logger.info(f"Video saved to {output}")


def main():
    cli()


if __name__ == "__main__":
    main()
