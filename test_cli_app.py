import csv
import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def make_input(values):
    answers = iter(values)
    return lambda _prompt: next(answers)


def test_cli_can_exit_cleanly(tmp_path):
    cli_app = importlib.import_module("cli_app")
    outputs = []

    code = cli_app.run_cli(
        input_fn=make_input(["keluar"]),
        output_fn=outputs.append,
        model_path=ROOT / "intent_model.pkl",
        log_path=tmp_path / "chat.csv",
    )

    assert code == 0
    assert any("sampai jumpa" in line.lower() for line in outputs)


def test_cli_faq_is_answered_and_logged(tmp_path):
    cli_app = importlib.import_module("cli_app")
    outputs = []
    log_path = tmp_path / "chat.csv"

    cli_app.run_cli(
        input_fn=make_input(["cara bayar ukt lewat bca", "keluar"]),
        output_fn=outputs.append,
        model_path=ROOT / "intent_model.pkl",
        log_path=log_path,
    )

    assert any("Pembayaran UKT" in line for line in outputs)
    assert any("pembayaran_ukt" in line for line in outputs)
    with log_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    assert rows[0]["intent"] == "pembayaran_ukt"
