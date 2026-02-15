import os
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "data", "model.joblib")
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "clean_data.csv")

def analyze_model():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(DATA_PATH):
        print(f"Error: Model or data not found!\nModel: {MODEL_PATH}\nData: {DATA_PATH}")
        return

    print("Loading model...")
    pipeline = joblib.load(MODEL_PATH)
    
    print("Loading data...")
    try:
        df = pd.read_csv(DATA_PATH)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
        
    print(f"Dataset size: {len(df)}")
    
    X = df["title"].fillna("") + " " + df["text"].fillna("")
    y = df["label"].astype(int)

    print("Predicting...")
    y_pred = pipeline.predict(X)
    probs = pipeline.predict_proba(X)[:, 0]
    
    uncertain_mask = (probs > 0.4) & (probs < 0.6)
    uncertain_count = uncertain_mask.sum()
    print(f"\nConfidence Distribution:")
    print(f"Total samples: {len(probs)}")
    print(f"Uncertain samples (40-60%): {uncertain_count} ({uncertain_count/len(probs)*100:.2f}%)")
    
    print("\n" + "="*50)
    print(f"Accuracy: {accuracy_score(y, y_pred):.4f}")
    print("="*50)
    print("\nReport:")
    print(classification_report(y, y_pred, target_names=['Fake', 'Real'])) 

    df['predicted'] = y_pred
    misclassified = df[df['label'] != df['predicted']]
    
    print("\n" + "="*50)
    print(f"Total Misclassified: {len(misclassified)}")
    
    if len(misclassified) > 0:
        print("\n--- False Positives (Real labeled as Fake) ---")
        
        fp = misclassified[misclassified['predicted'] == 1].head(3)
        print(f"\nExample: Predicted REAL but was FAKE (len={len(misclassified[misclassified['predicted'] == 1])}):")
        for i, row in fp.iterrows():
            print(f"- {row['title']} (Text len: {len(str(row['text']))})")

        fn = misclassified[misclassified['predicted'] == 0].head(3)
        print(f"\nExample: Predicted FAKE but was REAL (len={len(misclassified[misclassified['predicted'] == 0])}):")
        for i, row in fn.iterrows():
            print(f"- {row['title']} (Text len: {len(str(row['text']))})")

    if hasattr(pipeline.named_steps['clf'], 'coef_'):
        tfidf = pipeline.named_steps['tfidf']
        clf = pipeline.named_steps['clf']
        feature_names = tfidf.get_feature_names_out()
        coefficients = clf.coef_[0]

        importance_df = pd.DataFrame({
            'word': feature_names,
            'weight': coefficients
        })

        print("\n" + "="*50)
        print("Top words pushing towards REAL (Positive weight):")
        print(importance_df.sort_values(by='weight', ascending=False).head(10)[['word', 'weight']])

        print("\n" + "="*50)
        print("Top words pushing towards FAKE (Negative weight):")
        print(importance_df.sort_values(by='weight', ascending=True).head(10)[['word', 'weight']])
    else:
        print("Model does not provide coefficients.")

if __name__ == "__main__":
    analyze_model()