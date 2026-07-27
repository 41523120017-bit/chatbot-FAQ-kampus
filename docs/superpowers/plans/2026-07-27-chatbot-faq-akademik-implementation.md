# Chatbot FAQ Akademik Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Menghasilkan chatbot FAQ Akademik Universitas Mercu Buana yang memenuhi rubrik UAS, berjalan dari CLI dan Streamlit, teruji, serta dilengkapi artefak evaluasi, laporan, dan slide.

**Architecture:** `DialogManager` menjadi mesin percakapan bersama untuk CLI dan UI. Model intent berupa pipeline preprocessing + gabungan TF-IDF kata/karakter + Logistic Regression; pelatihan menyimpan model dan artefak evaluasi. Kanal CLI/UI memanggil mesin yang sama lalu meneruskan metadata interaksi ke logger CSV.

**Tech Stack:** Python 3.10+, scikit-learn, pandas, NumPy, joblib, matplotlib, Streamlit, pytest, python-docx, python-pptx, ReportLab/LibreOffice untuk ekspor PDF.

## Global Constraints

- Dataset tepat 250 utterance: lima intent dengan masing-masing 50 data.
- Gunakan stratified train/test split 80:20 dan `random_state=42`.
- Model produksi harus TF-IDF + Logistic Regression dan menyediakan probabilitas prediksi.
- NIM pada log harus disamarkan.
- UI tidak boleh bergantung pada font, gambar, atau avatar dari internet.
- Laporan PDF maksimal 10 halaman; slide minimal 12.
- Semua data mahasiswa pada demo diberi label sebagai data dummy.
- Workspace bukan repositori Git aktif; setiap checkpoint diverifikasi dengan test dan inspeksi berkas tanpa perintah commit.

---

### Task 1: Dataset dan Preprocessing

**Files:**
- Modify: `dataset_faq.json`
- Modify: `preprocessing.py`
- Create: `tests/test_dataset_preprocessing.py`

**Interfaces:**
- Produces: `preprocess_text(text: str) -> str`
- Produces: JSON records berbentuk `{"text": str, "intent": str}`

- [ ] **Step 1: Tulis test dataset dan preprocessing**

```python
def test_dataset_is_balanced(dataset):
    counts = Counter(row["intent"] for row in dataset)
    assert len(dataset) == 250
    assert counts == {intent: 50 for intent in EXPECTED_INTENTS}
    assert len({row["text"].casefold() for row in dataset}) == 250

def test_preprocess_normalizes_student_language():
    assert preprocess_text("BGmn cra ngisi KRS smstr 5??") == (
        "bagaimana cara isi krs semester 5"
    )
```

- [ ] **Step 2: Jalankan test dan pastikan gagal pada dataset lama**

Run: `python -m pytest tests/test_dataset_preprocessing.py -q`  
Expected: FAIL karena dataset hanya 49 data.

- [ ] **Step 3: Perluas kamus normalisasi dan dataset**

Pertahankan lima label yang ada. Tambahkan variasi formal, informal, singkatan, typo, dan pertanyaan lanjutan sampai setiap intent memiliki 50 teks unik. `preprocess_text` harus aman untuk `None`, lowercase, membersihkan karakter non-alfanumerik, memecah token, dan menerapkan `TYPO_DICT`.

- [ ] **Step 4: Jalankan test dataset dan preprocessing**

Run: `python -m pytest tests/test_dataset_preprocessing.py -q`  
Expected: seluruh test PASS.

### Task 2: Pipeline Pelatihan dan Artefak Evaluasi

**Files:**
- Modify: `train_eval.py`
- Modify: `requirements.txt`
- Create: `tests/test_train_eval.py`
- Generate: `artifacts/evaluation/*`
- Generate: `intent_model.pkl`

**Interfaces:**
- Consumes: `preprocess_text(text: str) -> str`
- Produces: `load_dataset(path: Path) -> pandas.DataFrame`
- Produces: `build_pipeline() -> sklearn.pipeline.Pipeline`
- Produces: `train_and_evaluate(dataset_path: Path, model_path: Path, output_dir: Path) -> dict`

- [ ] **Step 1: Tulis test pipeline dan artefak**

```python
def test_pipeline_contains_tfidf_and_logistic_regression():
    pipeline = build_pipeline()
    assert pipeline.named_steps["classifier"].__class__.__name__ == "LogisticRegression"

def test_training_writes_required_artifacts(tmp_path):
    summary = train_and_evaluate(DATASET, tmp_path / "model.pkl", tmp_path / "evaluation")
    assert 0 <= summary["accuracy"] <= 1
    for name in REQUIRED_ARTIFACTS:
        assert (tmp_path / "evaluation" / name).exists()
```

- [ ] **Step 2: Jalankan test untuk memverifikasi kegagalan awal**

Run: `python -m pytest tests/test_train_eval.py -q`  
Expected: FAIL karena fungsi modular dan artefak belum tersedia.

- [ ] **Step 3: Implementasikan pipeline evaluasi reproducible**

Bangun pipeline dengan `FeatureUnion` dari word TF-IDF `(1, 2)` dan `char_wb` TF-IDF `(2, 5)`, lalu Logistic Regression. Validasi kolom, label, data kosong, dan jumlah data per kelas. Simpan model, ringkasan JSON, report CSV, confusion matrix CSV/PNG, distribusi CSV/PNG, contoh preprocessing, dan salah klasifikasi.

- [ ] **Step 4: Jalankan test dan pelatihan nyata**

Run: `python -m pytest tests/test_train_eval.py -q`  
Expected: PASS.

Run: `python train_eval.py`  
Expected: model tersimpan dan konsol menampilkan accuracy, macro precision/recall/F1, weighted F1, serta lokasi artefak.

### Task 3: Mesin Dialog, Slot Filling, dan Respons

**Files:**
- Modify: `dialog_manager.py`
- Create: `tests/test_dialog_manager.py`

**Interfaces:**
- Consumes: model dengan `predict_proba()` dan `classes_`
- Produces: `DialogManager.process_message(raw_user_text: str) -> str`
- Produces properties: `last_intent: str`, `last_confidence: float`, `state: str`
- Produces helpers: `extract_nim(text: str) -> str | None`, `extract_course_ids(text: str) -> list[str]`

- [ ] **Step 1: Tulis test slot dan state machine**

```python
def test_complete_krs_flow(manager):
    assert "NIM" in manager.process_message("saya ingin mengisi krs")
    assert manager.state == "WAITING_FOR_NIM"
    assert "Data Mahasiswa" in manager.process_message("41523120017")
    assert manager.state == "SELECTING_MATKUL"
    assert "RINGKASAN" in manager.process_message("1, 2")
    assert manager.state == "WAITING_CONFIRMATION"
    assert "Berhasil Dikunci" in manager.process_message("ya")
    assert manager.state == "IDLE"

def test_ambiguous_confirmation_reprompts(manager):
    # Siapkan state WAITING_CONFIRMATION.
    response = manager.process_message("mungkin")
    assert "jawab" in response.lower()
    assert manager.state == "WAITING_CONFIRMATION"
```

- [ ] **Step 2: Jalankan test dan verifikasi kasus konfirmasi ambigu gagal**

Run: `python -m pytest tests/test_dialog_manager.py -q`  
Expected: test konfirmasi ambigu FAIL karena implementasi lama langsung membatalkan.

- [ ] **Step 3: Pisahkan helper slot, katalog, metadata, dan respons**

Tambahkan validasi input kosong, deduplikasi pilihan mata kuliah, jawaban positif/negatif eksplisit, confidence fallback, serta metadata prediksi. Pertahankan respons Bahasa Indonesia dan API `process_message()` berbentuk string.

- [ ] **Step 4: Jalankan test dialog**

Run: `python -m pytest tests/test_dialog_manager.py -q`  
Expected: PASS.

### Task 4: Logger dan Kanal CLI

**Files:**
- Create: `chat_logger.py`
- Create: `cli_app.py`
- Create: `tests/test_chat_logger.py`
- Create: `tests/test_cli_app.py`

**Interfaces:**
- Produces: `mask_sensitive_text(text: str) -> str`
- Produces: `log_interaction(log_path: Path, session_id: str, channel: str, user_message: str, bot_response: str, intent: str, confidence: float, state_before: str, state_after: str) -> None`
- Produces: `build_chatbot(model_path: Path) -> DialogManager`
- Produces: `run_cli(input_fn=input, output_fn=print, model_path=MODEL_PATH, log_path=LOG_PATH) -> int`

- [ ] **Step 1: Tulis test masking, header CSV, dan sesi CLI**

```python
def test_mask_sensitive_text():
    assert "41523120017" not in mask_sensitive_text("NIM 41523120017")
    assert "415******17" in mask_sensitive_text("NIM 41523120017")

def test_cli_can_exit(fake_model, tmp_path):
    answers = iter(["keluar"])
    outputs = []
    code = run_cli(lambda _: next(answers), outputs.append, fake_model, tmp_path / "log.csv")
    assert code == 0
    assert any("sampai jumpa" in line.lower() for line in outputs)
```

- [ ] **Step 2: Jalankan test untuk memastikan modul belum ada**

Run: `python -m pytest tests/test_chat_logger.py tests/test_cli_app.py -q`  
Expected: FAIL saat impor.

- [ ] **Step 3: Implementasikan logger append-safe dan CLI interaktif**

Logger membuat direktori induk dan header hanya sekali. CLI mendukung `bantuan`, `reset`, `keluar`, EOF/KeyboardInterrupt, menampilkan intent/confidence untuk FAQ, dan mencatat semua interaksi.

- [ ] **Step 4: Jalankan test dan smoke test CLI**

Run: `python -m pytest tests/test_chat_logger.py tests/test_cli_app.py -q`  
Expected: PASS.

Run: `printf 'cara bayar ukt\nkeluar\n' | python cli_app.py`  
Expected: respons UKT, metadata intent, dan salam penutup muncul; `logs/chat_history.csv` bertambah.

### Task 5: UI Streamlit

**Files:**
- Modify: `ui_app.py`
- Create: `tests/test_ui_structure.py`

**Interfaces:**
- Consumes: `DialogManager`, `log_interaction`, `intent_model.pkl`
- Produces: aplikasi Streamlit yang dijalankan dengan `streamlit run ui_app.py`

- [ ] **Step 1: Tulis test struktur UI**

```python
def test_ui_source_has_required_features():
    source = Path("ui_app.py").read_text(encoding="utf-8")
    for marker in ["st.chat_input", "log_interaction", "download_button", "Reset sesi"]:
        assert marker in source
    assert "fonts.googleapis.com" not in source
    assert "img.icons8.com" not in source
```

- [ ] **Step 2: Jalankan test untuk memverifikasi aset eksternal dan logging gagal**

Run: `python -m pytest tests/test_ui_structure.py -q`  
Expected: FAIL.

- [ ] **Step 3: Implementasikan UI responsif dan lokal**

Gunakan palet navy/biru UMB dengan aksen amber, tipografi sistem, lebar chat terkontrol, quick actions, state badge, kartu topik, reset, unduh log, dan disclosure data dummy. Hindari unsafe overrides yang memaksa seluruh teks menjadi satu warna sehingga merusak kontras.

- [ ] **Step 4: Jalankan test dan server headless**

Run: `python -m pytest tests/test_ui_structure.py -q`  
Expected: PASS.

Run: `python -m streamlit run ui_app.py --server.headless true --server.port 8501`  
Expected: server siap tanpa traceback dan endpoint lokal dapat diakses.

### Task 6: README dan Berkas Operasional

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- Create: `LINK_VIDEO.txt`
- Modify: `requirements.txt`
- Create: `tests/test_project_files.py`

**Interfaces:**
- Documents commands: environment setup, training, tests, CLI, UI, outputs, demo credentials.

- [ ] **Step 1: Tulis test kelengkapan berkas**

```python
def test_required_documentation_exists():
    for path in ["README.md", "LINK_VIDEO.txt", "requirements.txt"]:
        assert Path(path).exists()
```

- [ ] **Step 2: Implementasikan panduan operasional**

README harus memuat Python 3.10+, instalasi virtual environment, `pip install -r requirements.txt`, `python train_eval.py`, `python cli_app.py`, `streamlit run ui_app.py`, `pytest`, struktur proyek, lima intent, tiga skenario demo, serta pernyataan data dummy.

- [ ] **Step 3: Jalankan test dokumentasi**

Run: `python -m pytest tests/test_project_files.py -q`  
Expected: PASS.

### Task 7: Draft Laporan dan Presentasi

**Files:**
- Create: `scripts/generate_report.py`
- Create: `scripts/generate_slides.py`
- Generate: `deliverables/Laporan_Proyek_Chatbot_FAQ_UMB.docx`
- Generate: `deliverables/Laporan_Proyek_Chatbot_FAQ_UMB.pdf`
- Generate: `deliverables/Presentasi_Chatbot_FAQ_UMB.pptx`
- Generate: `deliverables/Presentasi_Chatbot_FAQ_UMB.pdf`
- Create: `tests/test_deliverables.py`

**Interfaces:**
- Consumes: seluruh CSV/JSON/PNG di `artifacts/evaluation/`
- Produces: laporan maksimal 10 halaman dan presentasi 14 slide.

- [ ] **Step 1: Tulis test isi dan struktur keluaran**

```python
def test_presentation_has_at_least_twelve_slides():
    deck = Presentation(PPTX_PATH)
    assert len(deck.slides) >= 12

def test_report_contains_required_sections():
    doc = Document(DOCX_PATH)
    text = "\n".join(p.text for p in doc.paragraphs)
    for section in ["Pendahuluan", "Teori", "Implementasi", "Evaluasi", "Kesimpulan", "Pembagian Tugas"]:
        assert section in text
```

- [ ] **Step 2: Buat generator laporan berbasis hasil aktual**

Laporan memakai A4, margin ringkas, heading konsisten, tabel distribusi dan metrik aktual, confusion matrix aktual, diagram arsitektur/flow, analisis intent yang salah, keterbatasan, referensi primer, dan tabel Anggota 1–3. Jangan mengarang angka; baca seluruh metrik dari artefak.

- [ ] **Step 3: Buat generator presentasi 14 slide**

Gunakan rasio 16:9, tema visual konsisten dengan UI, maksimal satu pesan utama per slide, grafik aktual, diagram, skenario demo, dan pembagian tugas. Catatan pembicara tidak wajib.

- [ ] **Step 4: Jalankan generator dan test struktur**

Run: `python scripts/generate_report.py`  
Expected: DOCX dan PDF laporan dibuat.

Run: `python scripts/generate_slides.py`  
Expected: PPTX dan PDF presentasi dibuat.

Run: `python -m pytest tests/test_deliverables.py -q`  
Expected: PASS.

- [ ] **Step 5: Render dan inspeksi visual seluruh halaman/slide**

Render PDF laporan dan seluruh slide menjadi PNG. Periksa tidak ada teks terpotong, tabel keluar margin, elemen bertumpuk, font terlalu kecil, atau halaman kosong. Perbaiki generator lalu ulangi render sampai bersih.

### Task 8: Verifikasi Terpadu dan Handoff

**Files:**
- Create: `artifacts/verification/cli_demo.txt`
- Create: `artifacts/verification/test_results.txt`
- Create: `artifacts/verification/deliverables_manifest.txt`

**Interfaces:**
- Consumes: seluruh aplikasi, test, dan deliverable.
- Produces: bukti bahwa hasil dapat direproduksi.

- [ ] **Step 1: Jalankan seluruh test**

Run: `python -m pytest -q`  
Expected: seluruh test PASS tanpa warning fatal.

- [ ] **Step 2: Jalankan ulang pelatihan dari awal**

Run: `python train_eval.py`  
Expected: seluruh artefak diperbarui dan model dapat dimuat kembali.

- [ ] **Step 3: Rekam tiga skenario CLI**

Jalankan FAQ UKT, follow-up jadwal/portal, dan alur KRS lengkap. Simpan output terminal ke `artifacts/verification/cli_demo.txt`.

- [ ] **Step 4: Verifikasi UI**

Jalankan Streamlit headless, pastikan server sehat, lalu uji input FAQ dan KRS melalui browser lokal jika tersedia. Pastikan log CSV bertambah.

- [ ] **Step 5: Buat manifest keluaran**

Daftar harus mencakup dataset, model, artefak evaluasi, source code, README, laporan DOCX/PDF, presentasi PPTX/PDF, `LINK_VIDEO.txt`, serta hasil test.

- [ ] **Step 6: Laporkan hasil aktual**

Sampaikan jumlah test lulus, nilai accuracy/precision/recall/F1, intent paling sering salah, lokasi semua deliverable, cara menjalankan CLI/UI, dan batasan video yang tetap menjadi tanggung jawab kelompok.
