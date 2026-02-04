import os
import re
from functools import lru_cache
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "clean_data.csv")

# Куди зберігаємо готовий pipeline
MODEL_PATH = os.path.join(BASE_DIR, "data", "model.joblib")


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def train_and_save_model():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    df["title"] = df["title"].fillna("").apply(clean_text)
    df["text"] = df["text"].fillna("").apply(clean_text)

    X = df["title"] + " " + df["text"]
    y = df["label"].astype(int)

    X_train, _, y_train, _ = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=20000,
            ngram_range=(1, 2),
            stop_words="english",
            min_df=10,
            max_df=0.7,
            sublinear_tf=True
        )),
        ("clf", LogisticRegression(
            solver="saga",
            max_iter=2000,
            C=0.1
        ))
    ])

    pipeline.fit(X_train, y_train)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    return pipeline


@lru_cache(maxsize=1)
def get_model():
    # На сервері: тільки завантаження готової моделі
    if not os.path.exists(MODEL_PATH):
        # НІКОЛИ не тренуємо тут автоматично — краще явно згенерувати модель локально
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}. "
            "Run training locally to generate it."
        )
    return joblib.load(MODEL_PATH)


def predict_news(text: str) -> int:
    model = get_model()
    cleaned = clean_text(text)

    proba = model.predict_proba([cleaned])[0]
    score = float(proba[1])

    word_count = len(cleaned.split())
    if word_count > 100 and score < 0.5:
        score += 0.1

    return round(min(score * 100, 100))
