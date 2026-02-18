import re


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
