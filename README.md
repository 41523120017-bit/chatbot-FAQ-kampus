# SIAKAD Assist — Chatbot FAQ Akademik UMB

Project UAS Natural Language Processing berupa chatbot FAQ akademik Universitas Mercu Buana. Sistem mengenali lima intent menggunakan TF-IDF dan Logistic Regression, mengekstrak slot dengan regex, serta memandu simulasi pengisian KRS secara multi-turn sampai tahap konfirmasi.

> Seluruh nama, NIM, katalog mata kuliah, dan biaya pada `db_krs.json` adalah **data dummy untuk demonstrasi**. Aplikasi tidak terhubung ke SIAKAD produksi.

## Fitur

- 250 utterance yang seimbang: 50 data untuk masing-masing dari lima intent.
- Preprocessing lowercase, cleaning, tokenisasi, dan normalisasi typo/singkatan.
- Representasi gabungan word TF-IDF dan character TF-IDF.
- Intent classification dengan Logistic Regression.
- Slot filling regex untuk NIM dan nomor mata kuliah.
- Dialog KRS multi-turn: NIM → mata kuliah → ringkasan → konfirmasi.
- CLI dan UI Streamlit menggunakan mesin dialog yang sama.
- Log CSV berisi intent, confidence, dan state; NIM disamarkan.
- Artefak accuracy, precision, recall, F1-score, dan confusion matrix.
- Automated tests, laporan, dan slide presentasi.

## Persiapan

Gunakan Python 3.10 atau lebih baru.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Melatih dan Mengevaluasi Model

```bash
python3 train_eval.py
```

Perintah tersebut memperbarui `intent_model.pkl` dan membuat:

```text
artifacts/evaluation/
├── evaluation_summary.json
├── classification_report.csv
├── confusion_matrix.csv
├── confusion_matrix.png
├── dataset_distribution.csv
├── dataset_distribution.png
├── preprocessing_examples.csv
└── misclassified_examples.csv
```

Split data menggunakan komposisi 80:20, stratifikasi label, dan `random_state=42` agar dapat direproduksi.

## Menjalankan CLI

```bash
python3 cli_app.py
```

Perintah CLI:

- `bantuan`: tampilkan contoh pertanyaan;
- `reset`: hapus konteks percakapan;
- `keluar`: tutup aplikasi;
- `batal`: batalkan alur KRS aktif.

## Menjalankan UI

```bash
python3 -m streamlit run ui_app.py
```

Buka `http://localhost:8501` jika browser tidak terbuka otomatis.

## Menjalankan Pengujian

```bash
MPLCONFIGDIR=/tmp/matplotlib-chatbot python3 -m pytest -q
```

## Skenario Demo

### 1. FAQ Pembayaran UKT

```text
Pengguna: bagaimana cara bayar ukt melalui bca
```

Chatbot memberikan prosedur umum pembayaran dan intent `pembayaran_ukt`.

### 2. Jadwal Ujian dan Pertanyaan Lanjutan

```text
Pengguna: jadwal uas dapat dilihat di mana
Pengguna: portalnya di mana
```

Chatbot menjawab jadwal ujian lalu mengarahkan pengguna ke portal SIAKAD.

### 3. KRS Multi-turn

```text
Pengguna: saya ingin mengisi krs
Pengguna: 41523120017
Pengguna: 1, 2
Pengguna: ya
```

NIM demo lain: `41520120027` dan `41521120043`.

## Struktur Proyek

```text
├── artifacts/                 Hasil evaluasi dan verifikasi
├── deliverables/              Laporan dan slide akhir
├── docs/superpowers/          Spesifikasi dan rencana implementasi
├── logs/                      Log percakapan runtime
├── scripts/                   Generator laporan dan slide
├── tests/                     Automated tests
├── chat_logger.py             Logger CSV dan masking NIM
├── cli_app.py                 Aplikasi terminal
├── dataset_faq.json           Dataset 250 utterance
├── db_krs.json                Database dummy simulasi KRS
├── dialog_manager.py          State machine dan slot filling
├── preprocessing.py           Normalisasi teks
├── train_eval.py              Pelatihan dan evaluasi
└── ui_app.py                  Aplikasi Streamlit
```

## Log Percakapan

CLI dan UI menulis ke `logs/chat_history.csv`. Kolomnya meliputi waktu, session ID, kanal, pesan, respons, intent, confidence, state sebelum, dan state sesudah. Rangkaian 10–12 digit disamarkan sebelum disimpan.

## Dokumen Pengumpulan

Berkas siap kumpul berada di `deliverables/`:

- `Laporan_Proyek_Chatbot_FAQ_UMB.docx`
- `Laporan_Proyek_Chatbot_FAQ_UMB.pdf`
- `Presentasi_Chatbot_FAQ_UMB.pptx`
- `Presentasi_Chatbot_FAQ_UMB.pdf`

Ganti label Anggota 1, Anggota 2, dan Anggota 3 pada dokumen sebelum dikumpulkan. Rekam video secara mandiri, unggah ke YouTube Unlisted atau Google Drive, lalu tempel tautannya ke `LINK_VIDEO.txt`.

## Batasan

- Model hanya mencakup lima intent dalam dataset.
- Informasi akademik bersifat demonstrasi dan perlu diverifikasi pada kanal resmi kampus.
- Sistem tidak melakukan transaksi atau perubahan data SIAKAD nyata.
- Evaluasi menggambarkan performa pada dataset proyek, bukan seluruh ragam bahasa mahasiswa.
