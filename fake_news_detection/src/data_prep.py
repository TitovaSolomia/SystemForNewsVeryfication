import pandas as pd
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

true_news_path = os.path.join(RAW_DATA_DIR, "True.csv")
fake_news_path = os.path.join(RAW_DATA_DIR, "Fake.csv")

def remove_agency_prefix(text):
    if not isinstance(text, str):
        return ""
    clean_text = re.sub(r'^.*?\(Reuters\)\s*-\s*', '', text)
    clean_text = re.sub(r'^[A-Z,\s]+\s\(.*?\)\s?-?\s?', '', clean_text)
    return clean_text

def clean_data():
    print("Loading datasets...")
    try:
        true_news = pd.read_csv(true_news_path)
        fake_news = pd.read_csv(fake_news_path)
    except FileNotFoundError as e:
        print(f"Error: Could not find CSV files. Check paths: {e}")
        return

    true_news.dropna(subset=["text", "title"], inplace=True)
    fake_news.dropna(subset=["text", "title"], inplace=True)
    
    true_news.drop_duplicates(subset="text", inplace=True)
    fake_news.drop_duplicates(subset="text", inplace=True)

    print("Removing agency prefixes from real news...")
    true_news["text"] = true_news["text"].apply(remove_agency_prefix)

    for df in [true_news, fake_news]:
        df["text_length"] = df["text"].apply(len)
        df["word_count"] = df["text"].apply(lambda x: len(x.split()))

    true_news["label"] = 1
    fake_news["label"] = 0 

    print("Merging and saving clean dataset...")
    clean_dataset = pd.concat([true_news, fake_news], ignore_index=True)
    
    output_path = os.path.join(PROCESSED_DATA_DIR, "clean_data.csv")
    clean_dataset.to_csv(output_path, index=False)
    print(f"Done! Clean data saved to: {output_path}")

if __name__ == "__main__":
    clean_data()