import csv
import importlib


def test_mask_sensitive_text_hides_full_nim():
    chat_logger = importlib.import_module("chat_logger")

    masked = chat_logger.mask_sensitive_text("NIM saya 41523120017")

    assert "41523120017" not in masked
    assert "415******17" in masked


def test_log_interaction_creates_csv_and_masks_messages(tmp_path):
    chat_logger = importlib.import_module("chat_logger")
    log_path = tmp_path / "nested" / "chat.csv"

    chat_logger.log_interaction(
        log_path=log_path,
        session_id="session-test",
        channel="cli",
        user_message="NIM 41523120017",
        bot_response="Data 41523120017 ditemukan",
        intent="pendaftaran_krs",
        confidence=1.0,
        state_before="WAITING_FOR_NIM",
        state_after="SELECTING_MATKUL",
    )

    with log_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    assert rows[0]["channel"] == "cli"
    assert rows[0]["user_message"] == "NIM 415******17"
    assert rows[0]["bot_response"] == "Data 415******17 ditemukan"
    assert rows[0]["state_after"] == "SELECTING_MATKUL"

