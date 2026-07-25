import os
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import joblib

from preprocessing import preprocess_text

def train_and_evaluate():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATASET_PATH = os.path.join(BASE_DIR, "dataset_faq.json")
    MODEL_PATH = os.path.join(BASE_DIR, "intent_model.pkl")

    print("1. Memuat dataset...")
    if not os.path.exists(DATASET_PATH):
        print(f"❌ File '{DATASET_PATH}' tidak ditemukan!")
        return

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    print(f"✅ Total data: {len(df)} baris")

    df['clean_text'] = df['text'].apply(preprocess_text)

    # Split Train/Test
    X_train, X_test, y_train, y_test = train_test_split(
        df['clean_text'], df['intent'], test_size=0.2, random_state=42, stratify=df['intent']
    )

    # Combined Word + Char TF-IDF Pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), sublinear_tf=True)),
        ('classifier', LogisticRegression(C=2.0, max_iter=300, class_weight='balanced'))
    ])

    print("\n2. Melatih Model Intent Classification...")
    pipeline.fit(X_train, y_train)

    print("\n3. Evaluasi Performa Model...")
    y_pred = pipeline.predict(X_test)

    print("\n================ CLASSIFICATION REPORT ================")
    print(classification_report(y_test, y_pred))

    print("================ CONFUSION MATRIX ================")
    labels = sorted(list(set(df['intent'])))
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    print(pd.DataFrame(cm, index=labels, columns=labels))

    joblib.dump(pipeline, MODEL_PATH)
    print(f"\n✅ Model baru berhasil disimpan ke '{MODEL_PATH}'!")

if __name__ == "__main__":
    train_and_evaluate()