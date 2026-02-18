import pytest
from PIL import Image
import tempfile
from pathlib import Path
from src.video_builder import save_frames, assemble_video


def test_save_frames():
    frames = [Image.new("RGB", (100, 100), "red") for _ in range(3)]
    with tempfile.TemporaryDirectory() as tmpdir:
        save_frames(frames, tmpdir, prefix="test")
        saved_files = list(Path(tmpdir).glob("test_*.png"))
        assert len(saved_files) == 3


def test_save_frames_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        save_frames([], tmpdir, prefix="test")
        saved_files = list(Path(tmpdir).glob("test_*.png"))
        assert len(saved_files) == 0
