import re


def is_punctuation(char: str) -> bool:
    if len(char) != 1:
        return False
    return not char.isalnum() and not char.isspace()


def is_pause_marker(char: str, pause_chars: list[str]) -> bool:
    return char in pause_chars


def split_sentences(text: str) -> list[str]:
    if not text.strip():
        return []

    pattern = r"[^。！？.!?]+[。！？.!?]?"
    matches = re.findall(pattern, text)

    sentences = []
    for match in matches:
        stripped = match.strip()
        if stripped:
            sentences.append(stripped)

    return sentences
