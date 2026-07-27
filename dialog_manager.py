"""State machine dan respons chatbot FAQ akademik."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

from preprocessing import preprocess_text


IDLE = "IDLE"
WAITING_FOR_NIM = "WAITING_FOR_NIM"
SELECTING_MATKUL = "SELECTING_MATKUL"
WAITING_CONFIRMATION = "WAITING_CONFIRMATION"


def extract_nim(text: str) -> str | None:
    """Ekstrak NIM 10–12 digit, termasuk jika ditulis dengan spasi/tanda hubung."""
    for candidate in re.findall(r"(?:\d[\s-]*){10,12}", text or ""):
        digits = re.sub(r"\D", "", candidate)
        if 10 <= len(digits) <= 12:
            return digits
    return None


def extract_course_ids(text: str) -> list[str]:
    """Ekstrak nomor mata kuliah unik dengan urutan sesuai masukan pengguna."""
    seen: set[str] = set()
    result: list[str] = []
    for course_id in re.findall(r"\b\d+\b", text or ""):
        if course_id not in seen:
            seen.add(course_id)
            result.append(course_id)
    return result


class DialogManager:
    """Mengelola intent FAQ dan alur multi-turn pengisian KRS demo."""

    def __init__(self, model, db_path: Path | str | None = None, threshold: float = 0.35):
        self.model = model
        self.state = IDLE
        self.context: dict = {}
        self.db_path = Path(db_path) if db_path else Path(__file__).with_name("db_krs.json")
        self.threshold = threshold
        self.last_intent = ""
        self.last_confidence = 0.0

    def _load_db(self) -> dict:
        """Membaca database demo JSON secara real-time."""
        if not self.db_path.exists():
            return {"mahasiswa": {}, "katalog_matkul": {}, "biaya_pokok_bop": 1_500_000}
        return json.loads(self.db_path.read_text(encoding="utf-8"))

    def reset_state(self) -> None:
        """Mengembalikan alur percakapan ke kondisi awal."""
        self.state = IDLE
        self.context.clear()

    def _set_metadata(self, intent: str = "", confidence: float = 0.0) -> None:
        self.last_intent = intent
        self.last_confidence = float(confidence)

    @staticmethod
    def _format_currency(value: int | float) -> str:
        return f"Rp {value:,.0f}".replace(",", ".")

    def _student_and_catalog_response(self, nim: str, db: dict) -> str:
        student = db.get("mahasiswa", {}).get(nim)
        if not student:
            return (
                f"❌ **NIM {nim} tidak terdaftar** pada database demo. "
                "Periksa kembali NIM atau ketik **batal**."
            )

        program = student["prodi"]
        catalog = db.get("katalog_matkul", {}).get(program, [])
        if not catalog:
            self.reset_state()
            return f"❌ Katalog mata kuliah untuk **{program}** belum tersedia."

        self.context.update({"nim": nim, "prodi": program})
        self.state = SELECTING_MATKUL
        rows = [
            (
                f"{item['id']}. **{item['nama']}** ({item['sks']} SKS) — "
                f"{self._format_currency(item['sks'] * item['harga_sks'])}"
            )
            for item in catalog
        ]
        return (
            "✅ **Data Mahasiswa Ditemukan** *(data dummy)*\n\n"
            f"- **Nama:** {student['nama']}\n"
            f"- **NIM:** {nim}\n"
            f"- **Program/Semester:** {program} — Semester {student['semester']}\n\n"
            "📚 **Katalog Mata Kuliah**\n"
            + "\n".join(rows)
            + "\n\nKetik nomor mata kuliah, dipisahkan koma. Contoh: **1, 2, 3**."
        )

    def _handle_waiting_for_nim(self, raw_text: str, db: dict) -> str:
        nim = extract_nim(raw_text)
        if not nim:
            return (
                "⚠️ Masukkan **NIM 10–12 digit**. Contoh: `41523120017`. "
                "Ketik **batal** untuk menghentikan proses."
            )
        return self._student_and_catalog_response(nim, db)

    def _handle_course_selection(self, raw_text: str, db: dict) -> str:
        selected_ids = extract_course_ids(raw_text)
        program = self.context.get("prodi", "")
        catalog = db.get("katalog_matkul", {}).get(program, [])
        by_id = {str(item["id"]): item for item in catalog}
        invalid_ids = [course_id for course_id in selected_ids if course_id not in by_id]
        if not selected_ids or invalid_ids:
            suffix = f" Nomor tidak tersedia: {', '.join(invalid_ids)}." if invalid_ids else ""
            return (
                "⚠️ Pilihan mata kuliah tidak valid. Masukkan nomor yang tersedia, "
                f"misalnya **1, 2**.{suffix}"
            )

        selected = [by_id[course_id] for course_id in selected_ids]
        total_sks = sum(item["sks"] for item in selected)
        course_cost = sum(item["sks"] * item["harga_sks"] for item in selected)
        total = course_cost + db.get("biaya_pokok_bop", 1_500_000)
        self.context.update({"selected_matkul": selected, "total_tagihan": total})
        self.state = WAITING_CONFIRMATION

        rows = "\n".join(
            f"- **{item['nama']}** ({item['sks']} SKS)" for item in selected
        )
        return (
            "📋 **RINGKASAN KRS**\n\n"
            f"{rows}\n\n"
            f"- **Total SKS:** {total_sks}\n"
            f"- **Estimasi tagihan demo:** {self._format_currency(total)}\n\n"
            "Konfirmasi penguncian rencana studi ini. Jawab **ya** atau **batal**."
        )

    def _handle_confirmation(self, clean_text: str) -> str:
        tokens = set(clean_text.split())
        positive = {"ya", "y", "ok", "oke", "setuju", "iya", "benar"}
        negative = {"tidak", "nggak", "enggak", "jangan", "batal", "cancel"}
        if tokens & positive:
            nim = self.context.get("nim", "-")
            total = self.context.get("total_tagihan", 0)
            self.reset_state()
            return (
                f"✅ **KRS Berhasil Dikunci!** NIM **{nim}** tercatat pada simulasi "
                f"dengan estimasi tagihan **{self._format_currency(total)}**."
            )
        if tokens & negative:
            self.reset_state()
            return "❌ **Pengajuan KRS dibatalkan.** Ada informasi lain yang dibutuhkan?"
        return "⚠️ Jawaban belum dikenali. Mohon jawab **ya** atau **batal**."

    def _predict_intent(self, clean_text: str) -> tuple[str, float]:
        probabilities = self.model.predict_proba([clean_text])[0]
        best_index = int(np.argmax(probabilities))
        return str(self.model.classes_[best_index]), float(probabilities[best_index])

    def _faq_response(self, intent: str) -> str:
        responses = {
            "akses_portal": (
                "🔗 **Akses Portal SIAKAD:** buka "
                "[sia.mercubuana.ac.id](https://sia.mercubuana.ac.id/akad.php/home) "
                "dan masuk menggunakan NIM. Jika akun bermasalah, hubungi admin akademik."
            ),
            "jadwal_ujian": (
                "📅 **Jadwal UTS/UAS:** lihat menu **Jadwal Ujian** pada portal "
                "SIAKAD untuk tanggal, jam, ruang, dan kartu ujian terbaru."
            ),
            "pembayaran_ukt": (
                "💳 **Pembayaran UKT:** periksa rincian tagihan dan nomor Virtual "
                "Account pada SIAKAD, lalu bayar melalui kanal bank yang tercantum. "
                "Simpan bukti transaksi untuk verifikasi."
            ),
            "syarat_beasiswa": (
                "🎓 **Informasi Beasiswa:** persyaratan umumnya meliputi prestasi/IPK "
                "dan dokumen identitas, tetapi ketentuan tiap program berbeda. Periksa "
                "pengumuman resmi Bagian Kemahasiswaan sebelum mendaftar."
            ),
        }
        return responses.get(intent, "Maaf, pertanyaan belum dapat diproses.")

    def process_message(self, raw_user_text: str) -> str:
        """Proses satu pesan dan kembalikan respons Markdown."""
        raw_user_text = raw_user_text or ""
        clean_text = preprocess_text(raw_user_text)
        self._set_metadata()
        if not clean_text:
            return "⚠️ Silakan tuliskan pertanyaan atau kebutuhan akademik Anda."

        if clean_text in {"batal", "cancel", "reset", "stop"}:
            self._set_metadata("pendaftaran_krs", 1.0)
            self.reset_state()
            return "❌ **Proses dibatalkan.** Ada informasi lain yang bisa saya bantu?"

        db = self._load_db()
        if self.state == WAITING_FOR_NIM:
            self._set_metadata("pendaftaran_krs", 1.0)
            return self._handle_waiting_for_nim(raw_user_text, db)
        if self.state == SELECTING_MATKUL:
            self._set_metadata("pendaftaran_krs", 1.0)
            return self._handle_course_selection(raw_user_text, db)
        if self.state == WAITING_CONFIRMATION:
            self._set_metadata("pendaftaran_krs", 1.0)
            return self._handle_confirmation(clean_text)

        direct_nim = extract_nim(raw_user_text)
        if direct_nim:
            self._set_metadata("pendaftaran_krs", 1.0)
            return self._student_and_catalog_response(direct_nim, db)

        intent, confidence = self._predict_intent(clean_text)
        previous_intent = self.context.get("last_intent", "")
        portal_keywords = {
            "portal",
            "portalnya",
            "akses",
            "link",
            "dimana",
            "masuk",
            "login",
            "siakad",
            "web",
        }
        if set(clean_text.split()) & portal_keywords and previous_intent == "jadwal_ujian":
            intent, confidence = "akses_portal", 1.0

        self._set_metadata(intent, confidence)
        if confidence < self.threshold:
            return (
                "🤔 Saya belum yakin memahami pertanyaan itu. Coba tanyakan tentang "
                "**KRS, pembayaran UKT, jadwal ujian, beasiswa, atau akses SIAKAD**."
            )

        self.context["last_intent"] = intent
        if intent == "pendaftaran_krs":
            self.state = WAITING_FOR_NIM
            return (
                "Tentu. Untuk memulai simulasi pengisian KRS, masukkan **NIM "
                "10–12 digit**. Contoh data demo: `41523120017`."
            )
        return self._faq_response(intent)
