import pytest
from src.config import load_config, get_default_config


def test_load_config_file_exists(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("video:\n  fps: 60\n")
    config = load_config(str(config_file))
    assert config["video"]["fps"] == 60


def test_load_config_file_not_exists():
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.yaml")


def test_get_default_config():
    config = get_default_config()
    assert config["video"]["fps"] == 30
    assert config["style"]["font_size"] == 48
    assert "sentence_enders" in config["parsing"]
