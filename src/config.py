import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "video": {
        "resolution": [1920, 1080],
        "fps": 30,
        "format": "mp4",
    },
    "style": {
        "font_path": "./fonts/default.ttf",
        "font_size": 48,
        "text_color": "#FFFFFF",
        "background_color": "#000000",
        "text_position": [100, 500],
    },
    "audio": {
        "typing_sound": "./sounds/sans_typing.wav",
        "pitch_variation": {
            "min": 0.9,
            "max": 1.1,
            "random": True,
        },
        "character_duration_ms": 50,
        "sentence_pause_ms": 500,
    },
    "parsing": {
        "sentence_enders": ["。", "！", "？", ".", "!", "?"],
        "sentence_pauses": ["，", "、", ","],
    },
}


def load_config(config_path: str) -> dict:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_default_config() -> dict:
    return DEFAULT_CONFIG.copy()
