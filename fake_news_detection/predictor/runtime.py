import os
import re
from functools import lru_cache
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "data", "model.joblib")


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@lru_cache(maxsize=1)
def get_model():
    return joblib.load(MODEL_PATH)


def predict_news(text: str) -> int:
    model = get_model()
    cleaned = clean_text(text)

    proba = model.predict_proba([cleaned])[0]
    score = float(proba[0])

    return round(min(score * 100, 100))
