import os
import json
import re
import numpy as np
from preprocessing import preprocess_text

class DialogManager:
    def __init__(self, model):
        self.model = model
        self.state = "IDLE"  # State: IDLE -> WAITING_FOR_NIM -> SELECTING_MATKUL -> WAITING_CONFIRMATION
        self.context = {}
        self.db_path = os.path.join(os.path.dirname(__file__), "db_krs.json")

    def _load_db(self):
        """Membaca database JSON secara real-time"""
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"mahasiswa": {}, "katalog_matkul": {}, "biaya_pokok_bop": 1500000}

    def reset_state(self):
        """Reset alur percakapan ke kondisi awal"""
        self.state = "IDLE"
        self.context.clear()

    def process_message(self, raw_user_text: str) -> str:
        db = self._load_db()
        clean_text = preprocess_text(raw_user_text)

        # Fitur Pembatalan Sesi
        if raw_user_text.strip().lower() in ["batal", "cancel", "reset", "stop"]:
            self.reset_state()
            return "❌ **Proses dibatalkan.** Ada informasi lain yang bisa saya bantu?"

        # =========================================================
        # STATE 1: WAITING_FOR_NIM (Bot sedang menunggu input NIM)
        # =========================================================
        if self.state == "WAITING_FOR_NIM":
            # Ekstrak seluruh digit angka dari input user
            nim_digits = "".join(re.findall(r'\d+', raw_user_text))
            
            if not nim_digits:
                return "⚠️ Mohon masukkan **NIM** Anda berupa angka (contoh: `41523120017`). Ketik **'batal'** untuk membatalkan."

            mahasiswa_db = db.get("mahasiswa", {})
            
            if nim_digits in mahasiswa_db:
                mhs = mahasiswa_db[nim_digits]
                prodi = mhs["prodi"]
                self.context['nim'] = nim_digits
                self.context['prodi'] = prodi
                
                matkul_list = db.get("katalog_matkul", {}).get(prodi, [])
                if not matkul_list:
                    self.reset_state()
                    return f"❌ Katalog mata kuliah untuk prodi **{prodi}** belum tersedia di `db_krs.json`."

                daftar_text = ""
                for m in matkul_list:
                    daftar_text += f"{m['id']}. **{m['nama']}** ({m['sks']} SKS) - Rp {m['sks']*m['harga_sks']:,.0f}\n"

                self.state = "SELECTING_MATKUL"
                return (
                    f"✅ **Data Mahasiswa Ditemukan!**\n\n"
                    f"• **Nama:** {mhs['nama']}\n"
                    f"• **NIM:** {nim_digits}\n"
                    f"• **Prodi/Semester:** {prodi} - Sem {mhs['semester']}\n\n"
                    f"📚 **Katalog Mata Kuliah Tersedia:**\n{daftar_text}\n"
                    f"Silakan **ketik nomor mata kuliah** yang ingin diambil (pisahkan dengan koma).\n"
                    f"*(Contoh input: **1, 2, 3**)*"
                )
            else:
                return f"❌ **NIM {nim_digits} tidak terdaftar** di database `db_krs.json`.\nSilakan periksa kembali NIM Anda atau ketik **'batal'**."

        # =========================================================
        # STATE 2: SELECTING_MATKUL (Mahasiswa memilih nomor matkul)
        # =========================================================
        if self.state == "SELECTING_MATKUL":
            selected_ids = re.findall(r'\b\d+\b', raw_user_text)
            prodi = self.context.get("prodi", "")
            available_matkul = db.get("katalog_matkul", {}).get(prodi, [])
            
            valid_matkul = [m for m in available_matkul if str(m["id"]) in selected_ids]
            
            if not valid_matkul:
                return "⚠️ Nomor pilihan tidak valid. Silakan ketik angka mata kuliah yang tersedia (contoh: **1, 2**):"
            
            total_sks = sum(m["sks"] for m in valid_matkul)
            total_biaya_sks = sum(m["sks"] * m["harga_sks"] for m in valid_matkul)
            bop = db.get("biaya_pokok_bop", 1500000)
            total_tagihan = total_biaya_sks + bop
            
            self.context["selected_matkul"] = valid_matkul
            self.context["total_tagihan"] = total_tagihan
            self.state = "WAITING_CONFIRMATION"

            matkul_ringkasan = "\n".join([f"  • **{m['nama']}** ({m['sks']} SKS)" for m in valid_matkul])
            return (
                f"📋 **RINGKASAN KRS YANG DIPILIH:**\n\n"
                f"{matkul_ringkasan}\n\n"
                f"📊 **Total SKS:** {total_sks} SKS\n"
                f"💰 **Total Tagihan:** Rp {total_tagihan:,.0f} (Termasuk BOP Pokok)\n\n"
                f"Apakah Anda ingin mengunci rencana studi ini? *(Jawab: **Ya** / **Batal**)*"
            )

        # =========================================================
        # STATE 3: WAITING_CONFIRMATION (Konfirmasi Ya / Batal)
        # =========================================================
        if self.state == "WAITING_CONFIRMATION":
            tokens = clean_text.split()
            if any(w in tokens for w in ["ya", "y", "ok", "setuju", "iya", "benar"]):
                nim = self.context.get('nim', '-')
                total = self.context.get('total_tagihan', 0)
                self.reset_state()
                return f"✅ **KRS Berhasil Dikunci!** NIM **{nim}** telah terdaftar dengan total tagihan **Rp {total:,.0f}**. Silakan lakukan pembayaran via Virtual Account SIAKAD."
            else:
                self.reset_state()
                return "❌ **Pengajuan KRS Dibatalkan.** Ada hal lain yang ingin Anda tanyakan?"

        # =========================================================
        # STATE 0: IDLE (Deteksi Langsung NIM / Klasifikasi Intent ML)
        # =========================================================
        # 1. Jika user langsung mengetik NIM tanpa bertanya terlebih dahulu
        nim_digits = "".join(re.findall(r'\d+', raw_user_text))
        if len(nim_digits) >= 10:
            mahasiswa_db = db.get("mahasiswa", {})
            if nim_digits in mahasiswa_db:
                mhs = mahasiswa_db[nim_digits]
                prodi = mhs["prodi"]
                self.context['nim'] = nim_digits
                self.context['prodi'] = prodi
                
                matkul_list = db.get("katalog_matkul", {}).get(prodi, [])
                daftar_text = ""
                for m in matkul_list:
                    daftar_text += f"{m['id']}. **{m['nama']}** ({m['sks']} SKS) - Rp {m['sks']*m['harga_sks']:,.0f}\n"

                self.state = "SELECTING_MATKUL"
                return (
                    f"✅ **Data Mahasiswa Ditemukan!**\n\n"
                    f"• **Nama:** {mhs['nama']}\n"
                    f"• **NIM:** {nim_digits}\n"
                    f"• **Prodi/Semester:** {prodi} - Sem {mhs['semester']}\n\n"
                    f"📚 **Katalog Mata Kuliah Tersedia:**\n{daftar_text}\n"
                    f"Silakan **ketik nomor mata kuliah** yang ingin diambil (pisahkan dengan koma).\n"
                    f"*(Contoh input: **1, 2, 3**)*"
                )
            else:
                return f"❌ **NIM {nim_digits} tidak terdaftar** di database `db_krs.json`."

        # 2. Prediksi Intent via Model Machine Learning
        probabilities = self.model.predict_proba([clean_text])[0]
        max_prob = np.max(probabilities)
        predicted_intent = self.model.classes_[np.argmax(probabilities)]

        # Penanganan Pertanyaan Lanjutan (Context Follow-up)
        portal_keywords = ["portal", "akses", "link", "dimana", "masuk", "login", "siakad", "web"]
        if any(w in clean_text.split() for w in portal_keywords) and self.context.get("last_intent") in ["jadwal_ujian", "akses_portal"]:
            predicted_intent = "akses_portal"
            max_prob = 1.0

        if max_prob < 0.35:
            return "🤔 Maaf, saya kurang memahami pertanyaan tersebut. Silakan tuliskan pertanyaan seputar KRS, Jadwal Ujian, UKT, atau Beasiswa."

        self.context["last_intent"] = predicted_intent

        if predicted_intent == "pendaftaran_krs":
            self.state = "WAITING_FOR_NIM"  # Pindah ke state menunggu NIM
            return "Tentu! Untuk memulai pengisian KRS, silakan masukkan **NIM** Anda terlebih dahulu (11-12 digit angka):"

        elif predicted_intent == "akses_portal":
            return "🔗 **Akses Portal SIAKAD:** Masuk ke `https://sia.mercubuana.ac.id/akad.php/home` menggunakan Username **NIM** Anda."

        elif predicted_intent == "jadwal_ujian":
            return "📅 **Jadwal Uts/UAS:** Dapat diakses melalui menu *Jadwal Ujian* pada portal SIAKAD."

        elif predicted_intent == "pembayaran_ukt":
            return "💳 **Pembayaran UKT:** Pembayaran via Virtual Account Bank Mandiri/BCA/BNI di SIAKAD."

        elif predicted_intent == "syarat_beasiswa":
            return "🎓 **Syarat Beasiswa:** IPK Minimal 3.25, Scan KTM & KTP, serta Surat Kelakuan Baik dari Fakultas."

        return "Maaf, pertanyaan belum dapat diproses."