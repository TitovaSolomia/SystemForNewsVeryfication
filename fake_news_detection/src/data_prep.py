import os
import re
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

RAW_PATH = os.path.join(RAW_DATA_DIR, "WELFake_Dataset.csv")
OUTPUT_PATH = os.path.join(PROCESSED_DATA_DIR, "clean_data.csv")

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)


CONTRACTIONS = {
    "don't": "do not", "doesn't": "does not", "didn't": "did not",
    "can't": "cannot", "couldn't": "could not", "won't": "will not",
    "wouldn't": "would not", "shouldn't": "should not",
    "isn't": "is not", "aren't": "are not", "wasn't": "was not",
    "weren't": "were not", "haven't": "have not", "hasn't": "has not",
    "hadn't": "had not", "i'm": "i am", "it's": "it is",
    "that's": "that is", "there's": "there is", "what's": "what is",
    "you're": "you are", "they're": "they are", "we're": "we are",
}


def expand_contractions(text: str) -> str:
    for c, e in CONTRACTIONS.items():
        text = re.sub(rf"\b{re.escape(c)}\b", e, text)
    return text


def remove_agency_prefix(text: str) -> str:
    text = re.sub(r"^.*?\(Reuters\)\s*-\s*", "", text)
    text = re.sub(r"^[A-Z,\s]+\(.*?\)\s?-?\s?", "", text)
    return text


def clean_text(text) -> str:
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = expand_contractions(text)
    text = remove_agency_prefix(text)

    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"\[.*?\]", " ", text)
    text = re.sub(r"\(.*?\)", " ", text)

    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\b[a-z]\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def clean_data():
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(f"Dataset not found: {RAW_PATH}")

    df = pd.read_csv(RAW_PATH)

    print("RAW DATA:")
    print(df.shape)
    print(df["label"].value_counts(dropna=False))
    print(df["label"].unique())

    df["title"] = df["title"].fillna("")
    df["text"] = df["text"].fillna("")
    df["label"] = df["label"].fillna(0)

    df["title"] = df["title"].apply(clean_text)
    df["text"] = df["text"].apply(clean_text)

    df["full_text"] = (df["title"] + " " + df["text"]).str.strip()

    df = df[df["full_text"].str.len() > 50]

    df = df.drop_duplicates(subset=["full_text"])

    df["label"] = df["label"].astype(int)

    print("\nAFTER CLEAN:")
    print(df["label"].value_counts())
    
    df["text_length"] = df["full_text"].apply(len)
    df["word_count"] = df["full_text"].apply(lambda x: len(x.split()))

    df = df[["title", "text", "full_text", "label", "text_length", "word_count"]]

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved to: {OUTPUT_PATH}")
    print(f"Rows: {len(df)}")


if __name__ == "__main__":
    clean_data()