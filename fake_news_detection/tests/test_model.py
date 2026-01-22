import pytest
from src.model import clean_text, predict_news

class TestMLModel:
    """
    Unit tests for the Machine Learning model logic and text preprocessing.
    """

    @pytest.mark.parametrize("input_text, expected", [
        ("Hello WORLD!", "hello world"),
        ("Check this: https://google.com links should go.", "check this links should go"),
        ("Numbers 123 and [brackets] gone.", "numbers and gone"),
        ("   Too    many    spaces   ", "too many spaces"),
        (None, ""),
    ])
    def test_clean_text_utility(self, input_text, expected):
        """Verify text cleaning regex works as expected (lowercase, no links, no punctuation)."""
        assert clean_text(input_text) == expected

    def test_predict_news_responds(self):
        """Verify prediction function returns a probability (integer 0-100)."""
        # Testing with a simple string
        result = predict_news("A standard piece of text to test the model distribution.")
        assert isinstance(result, int)
        assert 0 <= result <= 100

    def test_predict_news_short_text(self):
        """Verify prediction handles short text without crashing."""
        result = predict_news("Breaking news!")
        assert isinstance(result, int)
