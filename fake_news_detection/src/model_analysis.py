import os
import joblib
import pandas as pd
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "data", "model.joblib")
TEST_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "test_data.csv")


def analyze_model():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(TEST_DATA_PATH):
        print(
            f"Error: Model or test data not found!\n"
            f"Model: {MODEL_PATH}\n"
            f"Test data: {TEST_DATA_PATH}"
        )
        return

    print("Loading model...")
    pipeline = joblib.load(MODEL_PATH)

    print("Loading test data...")
    df = pd.read_csv(TEST_DATA_PATH)

    X_test = df["text"].fillna("")
    y_test = df["label"].astype(int)

    print(f"Test dataset size: {len(df)}")

    print("Predicting on test data...")
    y_pred = pipeline.predict(X_test)
    probs = pipeline.predict_proba(X_test)

    fake_probs = probs[:, 0]
    real_probs = probs[:, 1]

    confidence = probs.max(axis=1)
    uncertain_mask = (confidence > 0.4) & (confidence < 0.6)
    uncertain_count = uncertain_mask.sum()

    print("\nConfidence Distribution:")
    print(f"Total samples: {len(confidence)}")
    print(
        f"Uncertain samples (40-60%): "
        f"{uncertain_count} ({uncertain_count / len(confidence) * 100:.2f}%)"
    )

    print("\n" + "=" * 50)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("=" * 50)

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        y_pred,
        target_names=["Fake", "Real"]
    ))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    df["predicted"] = y_pred
    df["fake_probability"] = fake_probs
    df["real_probability"] = real_probs

    misclassified = df[df["label"] != df["predicted"]]

    print("\n" + "=" * 50)
    print(f"Total Misclassified: {len(misclassified)}")

    if len(misclassified) > 0:
        print("\n--- False Positives: Fake predicted as Real ---")
        fp = misclassified[
            (misclassified["label"] == 0) & (misclassified["predicted"] == 1)
        ].head(3)

        for _, row in fp.iterrows():
            print(f"- {row['text'][:200]}...")

        print("\n--- False Negatives: Real predicted as Fake ---")
        fn = misclassified[
            (misclassified["label"] == 1) & (misclassified["predicted"] == 0)
        ].head(3)

        for _, row in fn.iterrows():
            print(f"- {row['text'][:200]}...")

    if hasattr(pipeline.named_steps["clf"], "coef_"):
        tfidf = pipeline.named_steps["tfidf"]
        clf = pipeline.named_steps["clf"]

        feature_names = tfidf.get_feature_names_out()
        coefficients = clf.coef_[0]

        importance_df = pd.DataFrame({
            "word": feature_names,
            "weight": coefficients
        })

        print("\n" + "=" * 50)
        print("Top words pushing towards REAL:")
        print(
            importance_df
            .sort_values(by="weight", ascending=False)
            .head(10)
        )

        print("\n" + "=" * 50)
        print("Top words pushing towards FAKE:")
        print(
            importance_df
            .sort_values(by="weight", ascending=True)
            .head(10)
        )


if __name__ == "__main__":
    analyze_model()