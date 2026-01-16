import os
import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "clean_data.csv")

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def train_model():
    if not os.path.exists(DATA_PATH):
        return None

    df = pd.read_csv(DATA_PATH)
    df['title'] = df['title'].fillna('').apply(clean_text)
    df['text'] = df['text'].fillna('').apply(clean_text)
    
    X = df["title"] + " " + df["text"]
    y = df["label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
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
            C=0.1,                   
            n_jobs=-1
        ))
    ])

    pipeline.fit(X_train, y_train)
    return pipeline

trained_model = train_model()

def predict_news(text):
    if trained_model is None:
        return 0
    
    cleaned = clean_text(text)
    proba = trained_model.predict_proba([cleaned])[0]
    score = proba[1]

    word_count = len(cleaned.split())
    if word_count > 100 and score < 0.5:
        score += 0.1 

    return round(min(score * 100, 100))