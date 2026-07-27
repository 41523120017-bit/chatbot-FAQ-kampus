from pathlib import Path

import joblib
import pytest

import dialog_manager
from dialog_manager import DialogManager


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def manager():
    return DialogManager(joblib.load(ROOT / "intent_model.pkl"))


def advance_to_confirmation(manager):
    manager.process_message("saya ingin mengisi krs")
    manager.process_message("41523120017")
    manager.process_message("1, 2")
    assert manager.state == "WAITING_CONFIRMATION"


def test_regex_slot_helpers_extract_nim_and_unique_course_ids():
    assert dialog_manager.extract_nim("NIM saya 41523-120017") == "41523120017"
    assert dialog_manager.extract_nim("nomor saya 123") is None
    assert dialog_manager.extract_course_ids("pilih 1, 2 dan 2") == ["1", "2"]


def test_complete_krs_flow_requires_confirmation(manager):
    assert "NIM" in manager.process_message("saya ingin mengisi krs")
    assert manager.state == "WAITING_FOR_NIM"

    assert "Data Mahasiswa Ditemukan" in manager.process_message("41523120017")
    assert manager.state == "SELECTING_MATKUL"

    assert "RINGKASAN KRS" in manager.process_message("1, 2")
    assert manager.state == "WAITING_CONFIRMATION"

    assert "KRS Berhasil Dikunci" in manager.process_message("ya")
    assert manager.state == "IDLE"


def test_ambiguous_confirmation_reprompts_instead_of_cancelling(manager):
    advance_to_confirmation(manager)

    response = manager.process_message("mungkin nanti")

    assert "jawab" in response.lower()
    assert "ya" in response.lower()
    assert "batal" in response.lower()
    assert manager.state == "WAITING_CONFIRMATION"


def test_global_cancel_resets_state_and_context(manager):
    manager.process_message("saya ingin mengisi krs")
    assert manager.state == "WAITING_FOR_NIM"

    response = manager.process_message("batal")

    assert "dibatalkan" in response.lower()
    assert manager.state == "IDLE"
    assert manager.context == {}


def test_invalid_course_choice_keeps_selection_state(manager):
    manager.process_message("saya ingin mengisi krs")
    manager.process_message("41523120017")

    response = manager.process_message("99")

    assert "tidak valid" in response.lower()
    assert manager.state == "SELECTING_MATKUL"


def test_empty_input_is_rejected_without_model_prediction(manager):
    response = manager.process_message("   ")

    assert "tuliskan" in response.lower()
    assert manager.state == "IDLE"
    assert manager.last_intent == ""
    assert manager.last_confidence == 0.0


def test_faq_prediction_exposes_metadata(manager):
    response = manager.process_message("bagaimana cara bayar ukt melalui bca")

    assert "Pembayaran UKT" in response
    assert manager.last_intent == "pembayaran_ukt"
    assert manager.last_confidence >= 0.35


def test_exam_follow_up_can_route_to_portal(manager):
    manager.process_message("jadwal uas dapat dilihat di mana")
    response = manager.process_message("portalnya di mana")

    assert "Akses Portal SIAKAD" in response
    assert manager.last_intent == "akses_portal"
