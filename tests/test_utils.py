import click
import pytest

from src import utils


def test_check_ffmpeg_true(monkeypatch):
    monkeypatch.setattr(utils.shutil, "which", lambda _: "ffmpeg")
    assert utils.check_ffmpeg() is True


def test_check_ffmpeg_false(monkeypatch):
    monkeypatch.setattr(utils.shutil, "which", lambda _: None)
    assert utils.check_ffmpeg() is False


def test_verify_ffmpeg_raises(monkeypatch):
    monkeypatch.setattr(utils.shutil, "which", lambda _: None)
    with pytest.raises(click.ClickException):
        utils.verify_ffmpeg()
