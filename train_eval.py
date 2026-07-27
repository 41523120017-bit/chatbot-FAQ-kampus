"""Pelatihan dan evaluasi model intent chatbot FAQ akademik."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

from preprocessing import preprocess_text


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET_PATH = BASE_DIR / "dataset_faq.json"
DEFAULT_MODEL_PATH = BASE_DIR / "intent_model.pkl"
DEFAULT_OUTPUT_DIR = BASE_DIR / "artifacts" / "evaluation"
RANDOM_STATE = 42


def load_dataset(dataset_path: Path | str = DEFAULT_DATASET_PATH) -> pd.DataFrame:
    """Muat dan validasi dataset intent, lalu tambahkan teks hasil preprocessing."""
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset tidak ditemukan: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    frame = pd.DataFrame(data)
    required_columns = {"text", "intent"}
    if not required_columns <= set(frame.columns):
        raise ValueError("Dataset wajib memiliki kolom 'text' dan 'intent'.")
    if frame.empty:
        raise ValueError("Dataset tidak boleh kosong.")
    if frame[["text", "intent"]].isna().any().any():
        raise ValueError("Dataset tidak boleh memiliki nilai kosong.")

    frame = frame[["text", "intent"]].copy()
    frame["text"] = frame["text"].astype(str).str.strip()
    frame["intent"] = frame["intent"].astype(str).str.strip()
    if (frame["text"] == "").any() or (frame["intent"] == "").any():
        raise ValueError("Teks dan intent tidak boleh berupa string kosong.")
    if frame["text"].str.casefold().duplicated().any():
        raise ValueError("Dataset mengandung utterance duplikat.")

    counts = frame["intent"].value_counts()
    if len(counts) < 4:
        raise ValueError("Dataset harus memiliki minimal empat intent.")
    if counts.min() < 2:
        raise ValueError("Setiap intent harus memiliki minimal dua data.")

    frame["clean_text"] = frame["text"].map(preprocess_text)
    if (frame["clean_text"] == "").any():
        raise ValueError("Hasil preprocessing tidak boleh kosong.")
    return frame


def build_pipeline() -> Pipeline:
    """Bangun pipeline TF-IDF kata/karakter dan Logistic Regression."""
    features = FeatureUnion(
        [
            (
                "word_tfidf",
                TfidfVectorizer(
                    analyzer="word",
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                    min_df=1,
                ),
            ),
            (
                "char_tfidf",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(2, 5),
                    sublinear_tf=True,
                    min_df=1,
                ),
            ),
        ]
    )
    classifier = LogisticRegression(
        C=2.0,
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )
    return Pipeline([("features", features), ("classifier", classifier)])


def _save_confusion_matrix(
    matrix: np.ndarray, labels: list[str], output_path: Path
) -> None:
    fig, ax = plt.subplots(figsize=(9, 7))
    image = ax.imshow(matrix, interpolation="nearest", cmap="Blues")
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    ax.set(
        xticks=np.arange(len(labels)),
        yticks=np.arange(len(labels)),
        xticklabels=[label.replace("_", "\n") for label in labels],
        yticklabels=[label.replace("_", " ") for label in labels],
        ylabel="Intent Aktual",
        xlabel="Intent Prediksi",
        title="Confusion Matrix Intent Classification",
    )
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    threshold = matrix.max() / 2 if matrix.size else 0
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            ax.text(
                col,
                row,
                str(matrix[row, col]),
                ha="center",
                va="center",
                color="white" if matrix[row, col] > threshold else "#0f172a",
                fontweight="bold",
            )
    fig.tight_layout()
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _save_distribution(distribution: pd.Series, output_path: Path) -> None:
    labels = [label.replace("_", " ") for label in distribution.index]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(labels, distribution.values, color="#0B3D91")
    ax.set(title="Distribusi Dataset per Intent", xlabel="Intent", ylabel="Jumlah")
    ax.set_ylim(0, max(distribution.values) * 1.18)
    ax.tick_params(axis="x", rotation=20)
    for bar, value in zip(bars, distribution.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 1,
            str(int(value)),
            ha="center",
            fontweight="bold",
        )
    fig.tight_layout()
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def train_and_evaluate(
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
    model_path: Path | str = DEFAULT_MODEL_PATH,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
) -> dict:
    """Latih model, simpan artefak evaluasi, dan kembalikan ringkasan metrik."""
    frame = load_dataset(dataset_path)
    model_path = Path(model_path)
    output_dir = Path(output_dir)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    x_train, x_test, y_train, y_test = train_test_split(
        frame["clean_text"],
        frame["intent"],
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=frame["intent"],
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)
    labels = sorted(frame["intent"].unique().tolist())

    accuracy = accuracy_score(y_test, predictions)
    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        y_test, predictions, average="macro", zero_division=0
    )
    weighted_precision, weighted_recall, weighted_f1, _ = (
        precision_recall_fscore_support(
            y_test, predictions, average="weighted", zero_division=0
        )
    )
    matrix = confusion_matrix(y_test, predictions, labels=labels)
    report = classification_report(
        y_test,
        predictions,
        labels=labels,
        target_names=labels,
        output_dict=True,
        zero_division=0,
    )

    summary = {
        "dataset_size": int(len(frame)),
        "train_size": int(len(x_train)),
        "test_size": int(len(x_test)),
        "random_state": RANDOM_STATE,
        "accuracy": float(accuracy),
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "macro_f1": float(macro_f1),
        "weighted_precision": float(weighted_precision),
        "weighted_recall": float(weighted_recall),
        "weighted_f1": float(weighted_f1),
        "labels": labels,
        "intent_distribution": {
            key: int(value)
            for key, value in frame["intent"].value_counts().sort_index().items()
        },
    }

    joblib.dump(pipeline, model_path)
    (output_dir / "evaluation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    pd.DataFrame(report).transpose().to_csv(
        output_dir / "classification_report.csv", index_label="label"
    )
    pd.DataFrame(matrix, index=labels, columns=labels).to_csv(
        output_dir / "confusion_matrix.csv", index_label="actual_intent"
    )
    _save_confusion_matrix(matrix, labels, output_dir / "confusion_matrix.png")

    distribution = frame["intent"].value_counts().sort_index()
    distribution.rename_axis("intent").rename("count").to_csv(
        output_dir / "dataset_distribution.csv"
    )
    _save_distribution(distribution, output_dir / "dataset_distribution.png")

    examples = frame.groupby("intent", sort=True).head(2)[
        ["intent", "text", "clean_text"]
    ]
    examples.to_csv(output_dir / "preprocessing_examples.csv", index=False)

    evaluated = pd.DataFrame(
        {
            "text": frame.loc[x_test.index, "text"],
            "clean_text": x_test,
            "actual_intent": y_test,
            "predicted_intent": predictions,
        }
    )
    evaluated[evaluated["actual_intent"] != evaluated["predicted_intent"]].to_csv(
        output_dir / "misclassified_examples.csv", index=False
    )
    return summary


def _print_summary(summary: dict) -> None:
    print("\n=== HASIL EVALUASI MODEL ===")
    print(f"Dataset      : {summary['dataset_size']} utterance")
    print(f"Train / Test : {summary['train_size']} / {summary['test_size']}")
    print(f"Accuracy     : {summary['accuracy']:.4f}")
    print(f"Precision    : {summary['macro_precision']:.4f} (macro)")
    print(f"Recall       : {summary['macro_recall']:.4f} (macro)")
    print(f"F1-Score     : {summary['macro_f1']:.4f} (macro)")
    print(f"Weighted F1  : {summary['weighted_f1']:.4f}")
    print(f"Model        : {DEFAULT_MODEL_PATH}")
    print(f"Artefak      : {DEFAULT_OUTPUT_DIR}")


if __name__ == "__main__":
    _print_summary(train_and_evaluate())
