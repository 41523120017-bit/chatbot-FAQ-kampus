import json
from collections import Counter
from pathlib import Path

from preprocessing import preprocess_text


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_INTENTS = {
    "pendaftaran_krs",
    "pembayaran_ukt",
    "jadwal_ujian",
    "syarat_beasiswa",
    "akses_portal",
}


def load_dataset():
    return json.loads((ROOT / "dataset_faq.json").read_text(encoding="utf-8"))


def test_dataset_has_250_unique_balanced_utterances():
    dataset = load_dataset()
    counts = Counter(row["intent"] for row in dataset)

    assert len(dataset) == 250
    assert set(counts) == EXPECTED_INTENTS
    assert all(count == 50 for count in counts.values())
    assert len({row["text"].strip().casefold() for row in dataset}) == 250


def test_every_dataset_record_has_nonempty_text_and_known_intent():
    dataset = load_dataset()

    assert all(set(row) == {"text", "intent"} for row in dataset)
    assert all(row["text"].strip() for row in dataset)
    assert all(row["intent"] in EXPECTED_INTENTS for row in dataset)


def test_preprocess_normalizes_student_language():
    assert preprocess_text("BGmn cra ngisi KRS smstr 5??") == (
        "bagaimana cara isi krs semester 5"
    )


def test_preprocess_handles_empty_and_symbols():
    assert preprocess_text(None) == ""
    assert preprocess_text("  UKT!!! via BCA @2026  ") == "ukt via bca 2026"
