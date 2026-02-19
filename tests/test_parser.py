import pytest

from src.parser import is_punctuation, is_pause_marker, split_sentences


def test_split_sentences_chinese():
    text = "这是第一句。这是第二句！这是第三句？"
    sentences = split_sentences(text)
    assert len(sentences) == 3
    assert sentences[0] == "这是第一句。"
    assert sentences[1] == "这是第二句！"
    assert sentences[2] == "这是第三句？"


def test_split_sentences_english():
    text = "First sentence. Second sentence! Third sentence?"
    sentences = split_sentences(text)
    assert len(sentences) == 3
    assert sentences[0] == "First sentence."
    assert sentences[1] == "Second sentence!"
    assert sentences[2] == "Third sentence?"


def test_split_sentences_mixed():
    text = "这是Chinese text。And English text. 混合Mix！"
    sentences = split_sentences(text)
    assert len(sentences) == 3
    assert sentences[0] == "这是Chinese text。"
    assert sentences[1] == "And English text."
    assert sentences[2] == "混合Mix！"


def test_split_sentences_empty():
    sentences = split_sentences("")
    assert sentences == []


def test_split_sentences_no_enders():
    text = "No sentence enders here"
    sentences = split_sentences(text)
    assert len(sentences) == 1
    assert sentences[0] == "No sentence enders here"


class TestIsPunctuation:
    def test_letters_are_not_punctuation(self):
        assert is_punctuation("a") is False
        assert is_punctuation("Z") is False
        assert is_punctuation("你") is False

    def test_numbers_are_not_punctuation(self):
        assert is_punctuation("1") is False
        assert is_punctuation("9") is False

    def test_spaces_are_not_punctuation(self):
        assert is_punctuation(" ") is False

    def test_punctuation_returns_true(self):
        assert is_punctuation("。") is True
        assert is_punctuation("！") is True
        assert is_punctuation("？") is True
        assert is_punctuation(".") is True
        assert is_punctuation("!") is True
        assert is_punctuation("?") is True
        assert is_punctuation("，") is True
        assert is_punctuation("、") is True
        assert is_punctuation(",") is True
        assert is_punctuation(":") is True
        assert is_punctuation(";") is True


class TestIsPauseMarker:
    def test_pause_markers_return_true(self):
        pause_chars = ["，", "、", ","]
        assert is_pause_marker("，", pause_chars) is True
        assert is_pause_marker("、", pause_chars) is True
        assert is_pause_marker(",", pause_chars) is True

    def test_non_pause_punctuation_returns_false(self):
        pause_chars = ["，", "、", ","]
        assert is_pause_marker("。", pause_chars) is False
        assert is_pause_marker(".", pause_chars) is False
        assert is_pause_marker("!", pause_chars) is False

    def test_letters_return_false(self):
        pause_chars = ["，", "、", ","]
        assert is_pause_marker("a", pause_chars) is False
