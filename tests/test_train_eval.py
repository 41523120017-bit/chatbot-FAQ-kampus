import json
from pathlib import Path

import joblib
import pandas as pd

import train_eval


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset_faq.json"
REQUIRED_ARTIFACTS = {
    "evaluation_summary.json",
    "classification_report.csv",
    "confusion_matrix.csv",
    "confusion_matrix.png",
    "dataset_distribution.csv",
    "dataset_distribution.png",
    "preprocessing_examples.csv",
    "misclassified_examples.csv",
}


def test_load_dataset_validates_and_adds_clean_text():
    frame = train_eval.load_dataset(DATASET)

    assert isinstance(frame, pd.DataFrame)
    assert len(frame) == 250
    assert set(frame.columns) >= {"text", "intent", "clean_text"}
    assert frame["clean_text"].str.len().min() > 0


def test_pipeline_uses_tfidf_features_and_logistic_regression():
    pipeline = train_eval.build_pipeline()

    assert pipeline.named_steps["features"].__class__.__name__ == "FeatureUnion"
    assert pipeline.named_steps["classifier"].__class__.__name__ == "LogisticRegression"
    assert hasattr(pipeline.named_steps["classifier"], "predict_proba")


def test_training_writes_model_and_required_artifacts(tmp_path):
    model_path = tmp_path / "intent_model.pkl"
    output_dir = tmp_path / "evaluation"

    summary = train_eval.train_and_evaluate(DATASET, model_path, output_dir)

    assert model_path.exists()
    assert REQUIRED_ARTIFACTS <= {path.name for path in output_dir.iterdir()}
    assert 0.0 <= summary["accuracy"] <= 1.0
    assert 0.0 <= summary["macro_f1"] <= 1.0
    assert summary["test_size"] == 50
    assert summary["train_size"] == 200

    persisted = json.loads(
        (output_dir / "evaluation_summary.json").read_text(encoding="utf-8")
    )
    assert persisted["accuracy"] == summary["accuracy"]

    model = joblib.load(model_path)
    assert set(model.classes_) == {
        "akses_portal",
        "jadwal_ujian",
        "pembayaran_ukt",
        "pendaftaran_krs",
        "syarat_beasiswa",
    }
