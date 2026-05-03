import os
import re
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "clean_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "data", "model.joblib")
TEST_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "test_data.csv")


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def train_and_save_model():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    df["title"] = df["title"].fillna("").apply(clean_text)
    df["text"] = df["text"].fillna("").apply(clean_text)
    df["full_text"] = df["title"] + " " + df["text"]
    df["label"] = df["label"].astype(int)

    X = df["full_text"].fillna("")
    y = df["label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=30000,
            ngram_range=(1, 3),
            stop_words="english",
            min_df=10,
            max_df=0.7,
            sublinear_tf=True
        )),
        ("clf", LogisticRegression(
            solver="saga",
            max_iter=2000,
            C=2.0,
            random_state=42
        ))
    ])

    pipeline.fit(X_train, y_train)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    test_df = pd.DataFrame({
        "text": X_test,
        "label": y_test
    })
    test_df.to_csv(TEST_DATA_PATH, index=False)

    print(f"Model saved to: {MODEL_PATH}")
    print(f"Test data saved to: {TEST_DATA_PATH}")

    return pipeline


if __name__ == "__main__":
    train_and_save_model()