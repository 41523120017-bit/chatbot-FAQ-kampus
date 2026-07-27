"""Pencatatan percakapan chatbot ke CSV dengan penyamaran NIM."""

from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path


LOG_FIELDS = [
    "timestamp",
    "session_id",
    "channel",
    "user_message",
    "bot_response",
    "intent",
    "confidence",
    "state_before",
    "state_after",
]


def mask_sensitive_text(text: str) -> str:
    """Samarkan rangkaian 10–12 digit yang berpotensi berupa NIM."""
    def replace(match: re.Match) -> str:
        digits = match.group(0)
        return f"{digits[:3]}{'*' * (len(digits) - 5)}{digits[-2:]}"

    return re.sub(r"(?<!\d)\d{10,12}(?!\d)", replace, text or "")


def log_interaction(
    log_path: Path | str,
    session_id: str,
    channel: str,
    user_message: str,
    bot_response: str,
    intent: str,
    confidence: float,
    state_before: str,
    state_after: str,
) -> None:
    """Tambahkan satu interaksi ke file CSV dan buat header jika diperlukan."""
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not path.exists() or path.stat().st_size == 0
    row = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "session_id": session_id,
        "channel": channel,
        "user_message": mask_sensitive_text(user_message),
        "bot_response": mask_sensitive_text(bot_response),
        "intent": intent,
        "confidence": f"{float(confidence):.4f}",
        "state_before": state_before,
        "state_after": state_after,
    }
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LOG_FIELDS)
        if needs_header:
            writer.writeheader()
        writer.writerow(row)

