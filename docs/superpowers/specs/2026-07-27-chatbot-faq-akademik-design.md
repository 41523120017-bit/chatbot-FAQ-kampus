# Spesifikasi Desain Chatbot FAQ Akademik Universitas Mercu Buana

Tanggal: 27 Juli 2026  
Status: Disetujui secara konseptual oleh pengguna  
Domain: FAQ akademik kampus

## 1. Tujuan

Menghasilkan paket proyek UAS chatbot NLP yang dapat dijalankan melalui terminal dan antarmuka web Streamlit. Sistem harus memenuhi P1–P6: dataset minimal 200 utterance, preprocessing, representasi TF-IDF, intent classification, slot filling, dialog multi-turn dengan konfirmasi, evaluasi lengkap, UI/CLI, log percakapan, laporan, dan slide.

Video tidak dibuat dalam proyek ini karena akan direkam dan diunggah sendiri oleh kelompok. Proyek hanya menyediakan `LINK_VIDEO.txt` kosong sebagai tempat tautan akhir.

## 2. Ruang Lingkup dan Kriteria Keberhasilan

Sistem dianggap selesai apabila:

1. Dataset berisi 250 utterance berbahasa Indonesia dengan lima intent dan distribusi 50 data per intent.
2. Model menggunakan preprocessing eksplisit, TF-IDF, dan Logistic Regression.
3. Skrip pelatihan menghasilkan model serta accuracy, precision, recall, macro/weighted F1, classification report, confusion matrix, distribusi intent, dan contoh preprocessing.
4. Chatbot mendukung FAQ satu putaran dan proses KRS multi-turn dengan satu tahap konfirmasi eksplisit.
5. Slot NIM dan pilihan mata kuliah diekstrak menggunakan regex/pattern.
6. Mesin dialog yang sama digunakan oleh CLI dan UI.
7. Setiap interaksi disimpan ke CSV dengan data sensitif NIM disamarkan.
8. UI dapat dijalankan secara lokal tanpa aset visual eksternal.
9. Automated test utama lulus.
10. Tersedia draft laporan DOCX/PDF maksimal 10 halaman dan presentasi PPTX/PDF minimal 12 slide.

## 3. Pendekatan yang Dipilih

Pendekatan yang dipilih adalah penyempurnaan arsitektur yang sudah ada. TF-IDF dan Logistic Regression dipertahankan karena sederhana, dapat dijelaskan, cepat, memiliki probabilitas prediksi, dan sesuai contoh metode pada soal. Pendekatan perbandingan banyak classifier dan model transformer tidak digunakan agar proyek tetap reproduktif, ringan, dan fokus pada rubrik.

## 4. Dataset dan NLP

Lima intent:

- `pendaftaran_krs`
- `pembayaran_ukt`
- `jadwal_ujian`
- `syarat_beasiswa`
- `akses_portal`

Setiap intent memiliki 50 utterance. Variasi meliputi bahasa formal, bahasa percakapan mahasiswa, singkatan, typo ringan, pertanyaan langsung, dan susunan kalimat berbeda. Duplikasi teks lintas intent tidak diizinkan.

Preprocessing menjalankan:

1. lowercase;
2. penghapusan tanda baca/karakter khusus;
3. tokenisasi berbasis regex/spasi;
4. normalisasi singkatan dan typo umum;
5. penyatuan token kembali untuk masukan vectorizer.

Representasi teks memakai TF-IDF gabungan fitur kata dan karakter melalui `FeatureUnion`. Fitur kata menangkap topik, sedangkan character n-gram meningkatkan ketahanan terhadap typo. Classifier produksi menggunakan Logistic Regression dengan `class_weight="balanced"` dan random seed tetap.

Evaluasi memakai stratified train/test split 80:20 dengan seed tetap. Artefak yang disimpan:

- `evaluation_summary.json`
- `classification_report.csv`
- `confusion_matrix.csv`
- `confusion_matrix.png`
- `dataset_distribution.csv`
- `dataset_distribution.png`
- `preprocessing_examples.csv`
- `misclassified_examples.csv`

## 5. Arsitektur

Komponen utama:

- `preprocessing.py`: normalisasi teks.
- `train_eval.py`: validasi dataset, pelatihan, evaluasi, dan penyimpanan artefak.
- `dialog_manager.py`: intent prediction, state machine, slot filling, dan respons.
- `chat_logger.py`: pencatatan CSV dan penyamaran NIM.
- `cli_app.py`: kanal terminal interaktif.
- `ui_app.py`: kanal Streamlit.
- `dataset_faq.json`: korpus intent.
- `db_krs.json`: data dummy mahasiswa dan katalog mata kuliah.

Aliran data:

`Input pengguna -> preprocessing -> pemeriksaan state dialog -> prediksi intent -> slot filling/respons -> logging -> CLI atau UI`

DialogManager mempertahankan kompatibilitas dengan pemanggilan sederhana: `process_message()` mengembalikan teks respons, sementara metadata prediksi terakhir tersedia untuk logging dan indikator UI.

## 6. State Dialog KRS

State yang digunakan:

1. `IDLE`: FAQ biasa dan deteksi intent.
2. `WAITING_FOR_NIM`: meminta serta memvalidasi NIM.
3. `SELECTING_MATKUL`: mengekstrak nomor mata kuliah dan menolak pilihan tidak valid/duplikat.
4. `WAITING_CONFIRMATION`: menerima jawaban positif atau pembatalan. Input lain tidak langsung dianggap batal, tetapi meminta pengguna menjawab kembali.

Perintah global `batal`, `cancel`, `reset`, atau `stop` menghapus konteks dan mengembalikan state ke `IDLE`.

## 7. Penanganan Kesalahan dan Privasi

- Input kosong ditolak dengan pesan yang jelas.
- Confidence di bawah ambang menghasilkan fallback dengan daftar topik yang didukung.
- NIM tidak valid atau tidak terdaftar tidak memutus sesi secara diam-diam.
- Pilihan mata kuliah di luar katalog diberi umpan balik.
- Jawaban konfirmasi ambigu meminta pengguna menjawab `ya` atau `batal`.
- Kegagalan model/dataset ditampilkan sebagai petunjuk pemulihan yang dapat dilakukan pengguna.
- Nomor 10–12 digit disamarkan pada log CSV.
- Semua identitas mahasiswa di `db_krs.json` diperlakukan sebagai data dummy demo.

## 8. CLI dan UI

CLI menyediakan sapaan, prompt berulang, perintah bantuan, reset, keluar, respons chatbot, serta ringkasan intent/confidence saat relevan.

UI Streamlit menggunakan tata letak terpusat dan responsif dengan:

- header identitas layanan akademik;
- kartu cakupan layanan;
- quick actions;
- chat bubbles yang mudah dibaca;
- indikator state dialog dan status model;
- reset sesi;
- unduh log;
- instruksi demo NIM dummy;
- CSS lokal tanpa font atau avatar dari internet.

## 9. Logging

Log CSV menyimpan:

- timestamp ISO;
- session ID;
- kanal (`cli`/`ui`);
- pesan pengguna yang telah disamarkan;
- respons chatbot yang telah disamarkan;
- intent terakhir;
- confidence;
- state sebelum dan sesudah interaksi.

Direktori log dibuat saat aplikasi dijalankan dan tidak wajib sudah berisi data.

## 10. Pengujian

Pengujian mencakup:

- preprocessing lowercase, cleaning, dan koreksi typo;
- validitas serta keseimbangan dataset;
- model dapat dilatih dan memprediksi kelima intent;
- ekstraksi NIM dan nomor mata kuliah;
- alur KRS lengkap sampai konfirmasi;
- pembatalan dan konfirmasi ambigu;
- fallback confidence rendah;
- penyamaran NIM dan format log;
- sesi CLI noninteraktif melalui fungsi yang dapat diuji;
- impor/smoke test modul UI.

Verifikasi manual menjalankan minimal tiga skenario:

1. FAQ pembayaran UKT;
2. FAQ jadwal ujian diikuti pertanyaan akses portal;
3. pengisian KRS lengkap dengan NIM dummy, pilihan mata kuliah, dan konfirmasi.

## 11. Dokumen Luaran

Draft laporan memuat pendahuluan, teori NLP, metode, desain, implementasi, evaluasi, analisis kesalahan, keterbatasan, kesimpulan, referensi, dan pembagian tugas. Identitas anggota serta mata kuliah yang belum diberikan ditulis sebagai placeholder yang jelas.

Presentasi berisi 14 slide: judul, masalah, tujuan, kebutuhan, arsitektur, flow dialog, dataset, preprocessing, model, implementasi, evaluasi, analisis kesalahan, demo, dan kesimpulan/pembagian tugas.

`LINK_VIDEO.txt` hanya berisi instruksi singkat agar kelompok menempelkan tautan YouTube Unlisted atau Google Drive setelah merekam video.

## 12. Batasan

- Informasi akademik bersifat data demo dan bukan integrasi langsung dengan SIAKAD produksi.
- Model hanya mengenali lima intent yang dilatih.
- Slot filling difokuskan pada NIM dan pilihan mata kuliah.
- Tanggal, biaya, syarat, dan tautan harus diverifikasi oleh pengelola kampus sebelum penggunaan nyata.
- Kualitas evaluasi menggambarkan dataset proyek, bukan seluruh ragam bahasa mahasiswa di dunia nyata.
