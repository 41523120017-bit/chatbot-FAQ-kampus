"""Antarmuka terminal untuk chatbot FAQ Akademik UMB."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Callable

import joblib

from chat_logger import log_interaction
from dialog_manager import DialogManager


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "intent_model.pkl"
LOG_PATH = BASE_DIR / "logs" / "chat_history.csv"


def build_chatbot(model_path: Path | str = MODEL_PATH) -> DialogManager:
    """Muat model terlatih dan buat mesin dialog."""
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Model tidak ditemukan di {path}. Jalankan `python3 train_eval.py` dahulu."
        )
    return DialogManager(joblib.load(path))


def run_cli(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    model_path: Path | str = MODEL_PATH,
    log_path: Path | str = LOG_PATH,
) -> int:
    """Jalankan loop CLI; dependency injection membuat alur dapat diuji."""
    try:
        manager = build_chatbot(model_path)
    except (FileNotFoundError, OSError, ValueError) as error:
        output_fn(f"Gagal memulai chatbot: {error}")
        return 1

    session_id = uuid.uuid4().hex[:12]
    output_fn("=" * 64)
    output_fn("SIAKAD ASSIST — Chatbot FAQ Akademik Universitas Mercu Buana")
    output_fn("Topik: KRS, UKT, jadwal ujian, beasiswa, dan portal SIAKAD")
    output_fn("Perintah: bantuan | reset | keluar")
    output_fn("=" * 64)

    while True:
        try:
            user_message = input_fn("\nAnda: ").strip()
        except (EOFError, KeyboardInterrupt, StopIteration):
            output_fn("\nSampai jumpa. Sesi chatbot telah ditutup.")
            return 0

        command = user_message.casefold()
        if command in {"keluar", "exit", "quit"}:
            output_fn("Sampai jumpa. Semoga urusan akademik Anda lancar!")
            return 0
        if command in {"bantuan", "help"}:
            output_fn(
                "Contoh: `cara bayar UKT`, `jadwal UAS di mana`, atau "
                "`saya ingin mengisi KRS`. Ketik reset untuk memulai ulang."
            )
            continue
        if command == "reset":
            manager.reset_state()
            output_fn("Sesi dialog telah direset.")
            continue

        state_before = manager.state
        bot_response = manager.process_message(user_message)
        output_fn(f"\nBot: {bot_response}")
        if manager.last_intent:
            output_fn(
                f"[intent: {manager.last_intent} | confidence: "
                f"{manager.last_confidence:.1%} | state: {manager.state}]"
            )
        log_interaction(
            log_path=log_path,
            session_id=session_id,
            channel="cli",
            user_message=user_message,
            bot_response=bot_response,
            intent=manager.last_intent,
            confidence=manager.last_confidence,
            state_before=state_before,
            state_after=manager.state,
        )


if __name__ == "__main__":
    raise SystemExit(run_cli())
