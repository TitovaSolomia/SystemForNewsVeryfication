import pandas as pd
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

welfake_path = os.path.join(RAW_DATA_DIR, "WELFake_Dataset.csv")

def remove_agency_prefix(text):
    if not isinstance(text, str):
        return ""
    clean_text = re.sub(r'^.*?\(Reuters\)\s*-\s*', '', text)
    clean_text = re.sub(r'^[A-Z,\s]+\s\(.*?\)\s?-?\s?', '', clean_text)
    return clean_text

def clean_data():
    print(f"Loading WELFake dataset from: {welfake_path}")
    try:
        df = pd.read_csv(welfake_path)
    except FileNotFoundError as e:
        print(f"Error: Could not find WELFake_Dataset.csv. {e}")
        return
    
    df.dropna(subset=["text", "title"], inplace=True)
    
    df.drop_duplicates(subset="text", inplace=True)

    df["text"] = df["text"].apply(remove_agency_prefix)
    df["text_length"] = df["text"].apply(len)
    df["word_count"] = df["text"].apply(lambda x: len(x.split()))

    output_path = os.path.join(PROCESSED_DATA_DIR, "clean_data.csv")
    
    cols_to_save = ["title", "text", "label", "text_length", "word_count"]
    df[cols_to_save].to_csv(output_path, index=False)

if __name__ == "__main__":
    clean_data()