import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "/Users/koala/Kuliah/UAS_NLP/chatbot-FAQ-kampus-main";
const OUT = path.join(ROOT, "deliverables");
const QA = path.join(ROOT, "artifacts/qa/slides_build/rendered");

const C = {
  navy: "#071F3D",
  blue: "#0B4DA2",
  sky: "#DDEBFA",
  gold: "#F2B84B",
  paper: "#F3F6FA",
  white: "#FFFFFF",
  ink: "#142232",
  muted: "#5D6A78",
  line: "#C9D4DF",
  green: "#1B7F5C",
  red: "#B64747",
};

const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });

function addShape(slide, geometry, position, fill = "none", lineFill = "none", lineWidth = 0, radius = undefined) {
  return slide.shapes.add({
    geometry,
    position,
    fill,
    line: { style: "solid", fill: lineFill, width: lineWidth },
    ...(radius ? { borderRadius: radius } : {}),
  });
}

function addText(slide, text, left, top, width, height, opts = {}) {
  const shape = addShape(slide, "textbox", { left, top, width, height });
  shape.text = text;
  shape.text.style = {
    fontFamily: opts.fontFamily || "Arial",
    fontSize: opts.fontSize || 22,
    bold: opts.bold || false,
    italic: opts.italic || false,
    color: opts.color || C.ink,
    alignment: opts.align || "left",
    verticalAlignment: opts.valign || "top",
    lineSpacing: opts.lineSpacing || 1.05,
  };
  if (opts.rotation) shape.position.rotation = opts.rotation;
  return shape;
}

function addLine(slide, left, top, width, height, color = C.line, weight = 2) {
  return addShape(slide, "line", { left, top, width, height }, "none", color, weight);
}

function addHeader(slide, number, title, kicker = "CHATBOT FAQ AKADEMIK") {
  slide.background.fill = C.paper;
  addText(slide, kicker, 64, 36, 500, 24, { fontSize: 12, bold: true, color: C.blue });
  addText(slide, String(number).padStart(2, "0"), 1150, 30, 64, 32, { fontSize: 14, bold: true, color: C.muted, align: "right" });
  addText(slide, title, 64, 78, 1030, 64, { fontSize: 36, bold: true, color: C.navy, fontFamily: "Georgia" });
  addLine(slide, 64, 148, 1152, 0, C.gold, 4);
}

function addFooter(slide, label = "Universitas Mercu Buana • UAS NLP") {
  addLine(slide, 64, 678, 1152, 0, C.line, 1);
  addText(slide, label, 64, 688, 700, 18, { fontSize: 10, color: C.muted });
  addText(slide, "KELOMPOK 3 ORANG", 990, 688, 226, 18, { fontSize: 10, bold: true, color: C.muted, align: "right" });
}

function pill(slide, text, left, top, width, fill = C.sky, color = C.blue) {
  const s = addShape(slide, "roundRect", { left, top, width, height: 34 }, fill, fill, 0, "rounded-full");
  s.text = text;
  s.text.style = { fontFamily: "Arial", fontSize: 12, bold: true, color, alignment: "center", verticalAlignment: "middle" };
  return s;
}

function panel(slide, left, top, width, height, opts = {}) {
  return addShape(slide, "roundRect", { left, top, width, height }, opts.fill || C.white, opts.line || C.line, opts.lineWidth ?? 1, opts.radius || "rounded-xl");
}

function bulletList(slide, items, left, top, width, lineHeight = 54, fontSize = 20, color = C.ink) {
  items.forEach((item, i) => {
    addShape(slide, "ellipse", { left, top: top + i * lineHeight + 8, width: 12, height: 12 }, C.gold, C.gold, 0);
    addText(slide, item, left + 28, top + i * lineHeight, width - 28, lineHeight - 4, { fontSize, color });
  });
}

function addNotes(slide, sources, presenter = "") {
  const lines = [];
  if (presenter) lines.push(presenter, "");
  lines.push("[Sources]", ...sources.map((s) => `- ${s}`));
  slide.speakerNotes.textFrame.setText(lines.join("\n"));
  slide.speakerNotes.setVisible(true);
}

function metric(slide, value, label, left, top, width, accent = C.blue) {
  panel(slide, left, top, width, 134, { fill: C.white, line: C.line });
  addShape(slide, "rect", { left, top, width: 8, height: 134 }, accent, accent, 0);
  addText(slide, value, left + 28, top + 18, width - 48, 58, { fontSize: 42, bold: true, color: accent, fontFamily: "Georgia" });
  addText(slide, label, left + 28, top + 84, width - 48, 28, { fontSize: 15, bold: true, color: C.muted });
}

async function imageBytes(file) {
  const b = await fs.readFile(file);
  return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);
}

// 01 — Cover
{
  const s = deck.slides.add();
  s.background.fill = C.navy;
  addShape(s, "rect", { left: 0, top: 0, width: 20, height: 720 }, C.gold, C.gold, 0);
  addText(s, "PROJECT AKHIR • NATURAL LANGUAGE PROCESSING", 72, 56, 650, 28, { fontSize: 13, bold: true, color: C.gold });
  addText(s, "Chatbot FAQ\nAkademik Kampus", 72, 138, 790, 188, { fontSize: 56, bold: true, color: C.white, fontFamily: "Georgia", lineSpacing: 0.94 });
  addText(s, "Klasifikasi intent, slot filling, dan dialog multi-turn untuk layanan akademik Universitas Mercu Buana.", 76, 356, 650, 84, { fontSize: 21, color: "#D8E3EF", lineSpacing: 1.15 });
  pill(s, "TF-IDF", 76, 480, 114, "#173C66", C.white);
  pill(s, "LOGISTIC REGRESSION", 202, 480, 218, "#173C66", C.white);
  pill(s, "STREAMLIT", 432, 480, 126, C.gold, C.navy);
  panel(s, 872, 112, 300, 446, { fill: "#0B2B50", line: "#31567C", radius: "rounded-2xl" });
  addText(s, "UMB\nACADEMIC\nASSISTANT", 914, 170, 220, 172, { fontSize: 31, bold: true, color: C.white, align: "center", valign: "middle", fontFamily: "Georgia", lineSpacing: 0.92 });
  addLine(s, 930, 372, 188, 0, C.gold, 4);
  addText(s, "250 utterances\n5 intents\n98% accuracy", 922, 398, 204, 116, { fontSize: 20, color: "#D8E3EF", align: "center", lineSpacing: 1.3 });
  addText(s, "Anggota 1 • Anggota 2 • Anggota 3", 76, 638, 620, 24, { fontSize: 15, color: "#AFC2D6" });
  addNotes(s, ["Internal project specification and evaluation artifacts (accessed 2026-07-27)."], "Pembuka: jelaskan bahwa sistem tersedia melalui CLI dan web.");
}

// 02 — Problem
{
  const s = deck.slides.add();
  addHeader(s, 2, "Masalah yang ingin diselesaikan");
  addText(s, "Pertanyaan akademik berulang membutuhkan jawaban yang cepat, konsisten, dan tersedia di luar jam layanan.", 64, 182, 684, 86, { fontSize: 27, bold: true, color: C.navy, fontFamily: "Georgia" });
  const problems = [
    ["01", "Informasi tersebar", "Mahasiswa harus mencari sumber berbeda untuk KRS, UKT, ujian, beasiswa, dan portal."],
    ["02", "Respons tidak selalu instan", "Pertanyaan sederhana tetap menunggu petugas atau jam kerja layanan."],
    ["03", "Bahasa pengguna bervariasi", "Kalimat singkat, typo, dan istilah berbeda perlu dipetakan ke maksud yang sama."],
  ];
  problems.forEach((p, i) => {
    const x = 64 + i * 384;
    panel(s, x, 310, 352, 266, { fill: C.white, line: C.line });
    addText(s, p[0], x + 26, 334, 62, 42, { fontSize: 30, bold: true, color: C.gold, fontFamily: "Georgia" });
    addText(s, p[1], x + 26, 392, 292, 42, { fontSize: 21, bold: true, color: C.navy });
    addText(s, p[2], x + 26, 452, 292, 84, { fontSize: 17, color: C.muted, lineSpacing: 1.15 });
  });
  addFooter(s);
  addNotes(s, ["Project problem statement in docs/superpowers/specs/2026-07-27-chatbot-faq-akademik-design.md (accessed 2026-07-27)."]);
}

// 03 — Objective and requirements
{
  const s = deck.slides.add();
  addHeader(s, 3, "Solusi dan kebutuhan fungsional");
  panel(s, 64, 184, 466, 428, { fill: C.navy, line: C.navy });
  addText(s, "TUJUAN", 96, 214, 120, 24, { fontSize: 12, bold: true, color: C.gold });
  addText(s, "Asisten akademik sederhana yang memahami intent dan memandu proses secara bertahap.", 96, 266, 370, 148, { fontSize: 29, bold: true, color: C.white, fontFamily: "Georgia", lineSpacing: 1.02 });
  addText(s, "Dua kanal", 96, 466, 120, 24, { fontSize: 13, bold: true, color: "#B9CBDE" });
  pill(s, "CLI PYTHON", 96, 510, 132, "#173C66", C.white);
  pill(s, "WEB STREAMLIT", 240, 510, 172, C.gold, C.navy);
  panel(s, 566, 184, 650, 428, { fill: C.white, line: C.line });
  bulletList(s, [
    "Menerima input teks dan memprediksi 1 dari 5 intent.",
    "Mengekstrak NIM serta kode mata kuliah dengan regex.",
    "Menjalankan percakapan multi-turn dengan tahap konfirmasi.",
    "Menyimpan log CSV dengan penyamaran NIM.",
    "Menampilkan confidence dan menyediakan reset percakapan.",
  ], 604, 220, 566, 67, 18);
  addFooter(s);
  addNotes(s, ["Internal requirements derived from the UAS rubric and project implementation (accessed 2026-07-27)."]);
}

// 04 — Architecture
{
  const s = deck.slides.add();
  addHeader(s, 4, "Arsitektur chatbot — dari input ke respons");
  const nodes = [];
  const data = [
    ["01", "Input", "CLI / Web"],
    ["02", "Preprocessing", "clean + tokenize"],
    ["03", "Intent", "TF-IDF + LR"],
    ["04", "Dialog", "state + slots"],
    ["05", "Output", "response + log"],
  ];
  // Connectors first so they remain behind the nodes.
  for (let i = 0; i < 4; i++) {
    addLine(s, 272 + i * 232, 356, 58, 0, C.gold, 5);
  }
  data.forEach((d, i) => {
    const x = 64 + i * 232;
    const n = panel(s, x, 250, 208, 214, { fill: i === 2 ? C.navy : C.white, line: i === 2 ? C.navy : C.line });
    nodes.push(n);
    addText(s, d[0], x + 24, 272, 42, 28, { fontSize: 17, bold: true, color: i === 2 ? C.gold : C.blue });
    addText(s, d[1], x + 24, 324, 160, 38, { fontSize: i === 1 ? 17 : 22, bold: true, color: i === 2 ? C.white : C.navy });
    addText(s, d[2], x + 24, 380, 160, 42, { fontSize: 16, color: i === 2 ? "#D8E3EF" : C.muted });
  });
  panel(s, 64, 500, 1152, 112, { fill: C.sky, line: C.sky });
  addText(s, "Prinsip desain", 94, 530, 170, 28, { fontSize: 14, bold: true, color: C.blue });
  addText(s, "Model menentukan maksud; dialog manager menjaga konteks; logger menyediakan jejak evaluasi.", 270, 524, 882, 46, { fontSize: 22, bold: true, color: C.navy });
  addFooter(s);
  addNotes(s, ["Internal architecture implemented in preprocessing.py, train_eval.py, dialog_manager.py, cli_app.py, ui_app.py, and chat_logger.py (accessed 2026-07-27)."]);
}

// 05 — Dialogue state
{
  const s = deck.slides.add();
  addHeader(s, 5, "Flow dialog dan state conversation");
  const states = [
    ["IDLE", 82, 245, C.white],
    ["WAIT NIM", 334, 245, C.sky],
    ["WAIT MK", 586, 245, C.white],
    ["KONFIRMASI", 838, 245, C.gold],
  ];
  states.forEach((st, i) => {
    if (i < states.length - 1) addLine(s, st[1] + 188, 302, 64, 0, C.blue, 4);
  });
  states.forEach((st, i) => {
    panel(s, st[1], st[2], 188, 114, { fill: st[3], line: i === 3 ? C.gold : C.line });
    addText(s, String(i + 1).padStart(2, "0"), st[1] + 18, st[2] + 16, 36, 22, { fontSize: 12, bold: true, color: i === 3 ? C.navy : C.blue });
    addText(s, st[0], st[1] + 18, st[2] + 56, 152, 30, { fontSize: 18, bold: true, color: C.navy, align: "center" });
  });
  addText(s, "Ya", 1039, 271, 44, 22, { fontSize: 13, bold: true, color: C.green });
  addLine(s, 1026, 359, 0, 106, C.green, 4);
  panel(s, 898, 466, 256, 78, { fill: "#E4F3ED", line: "#B7DACD" });
  addText(s, "Selesai → kembali IDLE", 918, 490, 216, 28, { fontSize: 17, bold: true, color: C.green, align: "center" });
  panel(s, 732, 390, 230, 48, { fill: "#F8E4E4", line: "#E8BDBD" });
  addText(s, "Tidak → ulangi input", 748, 404, 198, 22, { fontSize: 13, bold: true, color: C.red, align: "center" });
  addText(s, "Chatbot meminta konfirmasi ulang sebelum mengeksekusi respons akhir.", 270, 536, 560, 44, { fontSize: 17, color: C.muted, align: "center" });
  addFooter(s);
  addNotes(s, ["Internal state machine implemented in dialog_manager.py (accessed 2026-07-27)."]);
}

// 06 — Dataset
{
  const s = deck.slides.add();
  addHeader(s, 6, "Dataset: 250 utterances yang seimbang");
  metric(s, "250", "TOTAL DATA TEKS", 64, 190, 240, C.blue);
  metric(s, "5", "INTENT", 324, 190, 240, C.navy);
  metric(s, "50", "DATA / INTENT", 584, 190, 240, C.gold);
  metric(s, "100%", "UTTERANCE UNIK", 844, 190, 240, C.green);
  const labels = ["KRS", "UKT", "Ujian", "Beasiswa", "Portal"];
  labels.forEach((label, i) => {
    const y = 388 + i * 47;
    addText(s, label, 80, y, 118, 26, { fontSize: 15, bold: true, color: C.ink });
    addShape(s, "roundRect", { left: 205, top: y + 3, width: 860, height: 20 }, C.sky, C.sky, 0, "rounded-full");
    addShape(s, "roundRect", { left: 205, top: y + 3, width: 860, height: 20 }, i === 2 ? C.gold : C.blue, i === 2 ? C.gold : C.blue, 0, "rounded-full");
    addText(s, "50", 1082, y, 56, 26, { fontSize: 15, bold: true, color: C.navy, align: "right" });
  });
  addFooter(s);
  addNotes(s, ["Internal dataset distribution from dataset_faq.json and artifacts/evaluation/dataset_distribution.csv (accessed 2026-07-27)."]);
}

// 07 — Preprocessing
{
  const s = deck.slides.add();
  addHeader(s, 7, "Preprocessing: teks mentah menjadi fitur");
  const steps = ["lowercase", "cleaning", "tokenization", "normalisasi typo"];
  steps.forEach((step, i) => pill(s, `${i + 1}. ${step.toUpperCase()}`, 64 + i * 286, 184, 262, i === 3 ? C.gold : C.sky, C.navy));
  panel(s, 64, 258, 548, 298, { fill: C.white, line: C.line });
  addText(s, "SEBELUM", 96, 290, 96, 22, { fontSize: 12, bold: true, color: C.red });
  addText(s, "\"Gimana cara isi KRS???\"", 96, 346, 450, 54, { fontSize: 27, bold: true, color: C.navy, fontFamily: "Georgia" });
  addText(s, "Tanda baca, kapitalisasi, dan variasi bentuk kata masih ada.", 96, 430, 430, 58, { fontSize: 17, color: C.muted });
  panel(s, 668, 258, 548, 298, { fill: C.navy, line: C.navy });
  addText(s, "SESUDAH", 700, 290, 96, 22, { fontSize: 12, bold: true, color: C.gold });
  addText(s, "gimana cara isi krs", 700, 346, 450, 54, { fontSize: 27, bold: true, color: C.white, fontFamily: "Georgia" });
  addText(s, "Token: [gimana, cara, isi, krs]", 700, 430, 430, 58, { fontSize: 17, color: "#D8E3EF" });
  addText(s, "Catatan: preprocessing dipakai konsisten saat training dan inference.", 64, 590, 1152, 32, { fontSize: 17, bold: true, color: C.blue, align: "center" });
  addFooter(s);
  addNotes(s, ["Internal preprocessing examples from artifacts/evaluation/preprocessing_examples.csv and preprocessing.py (accessed 2026-07-27)."]);
}

// 08 — Model
{
  const s = deck.slides.add();
  addHeader(s, 8, "Model intent classification");
  panel(s, 64, 188, 1152, 126, { fill: C.navy, line: C.navy });
  addText(s, "TEKS", 104, 229, 124, 38, { fontSize: 22, bold: true, color: C.white, align: "center" });
  addLine(s, 244, 248, 96, 0, C.gold, 4);
  addText(s, "WORD + CHAR\nTF-IDF", 356, 214, 230, 70, { fontSize: 21, bold: true, color: C.gold, align: "center", valign: "middle" });
  addLine(s, 602, 248, 96, 0, C.gold, 4);
  addText(s, "LOGISTIC\nREGRESSION", 714, 214, 230, 70, { fontSize: 21, bold: true, color: C.white, align: "center", valign: "middle" });
  addLine(s, 960, 248, 72, 0, C.gold, 4);
  addText(s, "INTENT", 1048, 229, 124, 38, { fontSize: 22, bold: true, color: C.gold, align: "center" });
  const facts = [
    ["Word n-gram", "(1, 2)", "menangkap kata dan frasa pendek"],
    ["Character n-gram", "(2, 5)", "lebih tahan pada variasi ejaan"],
    ["Split", "80 : 20", "200 train dan 50 test, stratified"],
    ["Reproducible", "seed 42", "hasil dapat diuji ulang"],
  ];
  facts.forEach((f, i) => {
    const x = 64 + i * 286;
    panel(s, x, 360, 262, 214, { fill: C.white, line: C.line });
    addText(s, f[0].toUpperCase(), x + 24, 388, 210, 22, { fontSize: 11, bold: true, color: C.blue });
    addText(s, f[1], x + 24, 430, 210, 44, { fontSize: 28, bold: true, color: C.navy, fontFamily: "Georgia" });
    addText(s, f[2], x + 24, 500, 210, 48, { fontSize: 15, color: C.muted });
  });
  addFooter(s);
  addNotes(s, [
    "Scikit-learn TfidfVectorizer documentation: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html (accessed 2026-07-27).",
    "Scikit-learn LogisticRegression documentation: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html (accessed 2026-07-27).",
    "Internal implementation in train_eval.py (accessed 2026-07-27).",
  ]);
}

// 09 — Slots and multi-turn
{
  const s = deck.slides.add();
  addHeader(s, 9, "Slot filling dan konfirmasi multi-turn");
  panel(s, 64, 184, 498, 424, { fill: C.white, line: C.line });
  addText(s, "RULE-BASED SLOT", 96, 216, 180, 22, { fontSize: 12, bold: true, color: C.blue });
  addText(s, "Regex mengekstrak informasi yang terstruktur.", 96, 260, 402, 62, { fontSize: 24, bold: true, color: C.navy, fontFamily: "Georgia" });
  pill(s, "NIM 10–12 DIGIT", 96, 350, 196, C.sky, C.blue);
  pill(s, "KODE MK", 304, 350, 126, C.gold, C.navy);
  addText(s, "Contoh", 96, 426, 92, 24, { fontSize: 13, bold: true, color: C.muted });
  addText(s, "41523120017 → 415******17", 96, 464, 380, 40, { fontSize: 20, bold: true, color: C.ink });
  addText(s, "Log menyimpan versi NIM yang disamarkan.", 96, 522, 390, 36, { fontSize: 15, color: C.muted });
  panel(s, 596, 184, 620, 424, { fill: C.navy, line: C.navy });
  addText(s, "CONTOH DIALOG", 628, 216, 180, 22, { fontSize: 12, bold: true, color: C.gold });
  const turns = [
    ["Mahasiswa", "Saya ingin mengisi KRS"],
    ["Bot", "Masukkan NIM Anda."],
    ["Mahasiswa", "41523120017, pilih MK: 1, 2"],
    ["Bot", "Konfirmasi data KRS tersebut? (ya/tidak)"],
    ["Mahasiswa", "ya"],
  ];
  turns.forEach((t, i) => {
    const y = 264 + i * 61;
    addText(s, t[0], 628, y, 100, 20, { fontSize: 11, bold: true, color: t[0] === "Bot" ? C.gold : "#AAC4E0" });
    addText(s, t[1], 738, y - 2, 424, 42, { fontSize: 16, color: C.white });
  });
  addFooter(s);
  addNotes(s, ["Internal slot and conversation-state implementation in dialog_manager.py and chat_logger.py (accessed 2026-07-27)."]);
}

// 10 — Delivery channels
{
  const s = deck.slides.add();
  addHeader(s, 10, "Implementasi: CLI dan UI web");
  panel(s, 64, 184, 548, 414, { fill: C.navy, line: C.navy });
  addText(s, "CLI", 96, 216, 120, 42, { fontSize: 34, bold: true, color: C.gold, fontFamily: "Georgia" });
  panel(s, 96, 286, 484, 238, { fill: "#031426", line: "#294766" });
  addText(s, "$ python cli_app.py\nBot: Halo, saya UMB Academic Assistant.\nAnda: kapan jadwal ujian?\nBot: Jadwal ujian dapat dilihat di portal...\n[intent=jadwal_ujian | confidence=0.94]", 120, 310, 432, 190, { fontFamily: "Courier New", fontSize: 14, color: "#DDEBFA", lineSpacing: 1.25 });
  addText(s, "Ringan • dapat diuji lewat terminal • cocok untuk demonstrasi logika", 96, 550, 464, 28, { fontSize: 14, color: "#B9CBDE" });
  panel(s, 668, 184, 548, 414, { fill: C.white, line: C.line });
  addText(s, "WEB UI", 700, 216, 160, 42, { fontSize: 34, bold: true, color: C.navy, fontFamily: "Georgia" });
  addShape(s, "roundRect", { left: 700, top: 286, width: 484, height: 238 }, C.paper, C.line, 1, "rounded-xl");
  pill(s, "UMB ACADEMIC ASSISTANT", 724, 306, 224, C.navy, C.white);
  panel(s, 738, 362, 324, 56, { fill: C.white, line: C.line });
  addText(s, "Bagaimana cara isi KRS?", 758, 378, 280, 24, { fontSize: 15, color: C.ink });
  panel(s, 824, 436, 336, 64, { fill: C.sky, line: C.sky });
  addText(s, "Silakan masukkan NIM Anda.", 844, 456, 292, 24, { fontSize: 15, bold: true, color: C.blue });
  addText(s, "Quick actions • download log • state & confidence", 700, 550, 464, 28, { fontSize: 14, color: C.muted });
  addFooter(s);
  addNotes(s, [
    "Streamlit chat elements documentation: https://docs.streamlit.io/develop/api-reference/chat (accessed 2026-07-27).",
    "Internal implementation in cli_app.py and ui_app.py (accessed 2026-07-27).",
  ]);
}

// 11 — Evaluation headline
{
  const s = deck.slides.add();
  addHeader(s, 11, "Hasil Evaluasi Model");
  addText(s, "98%", 64, 190, 442, 170, { fontSize: 112, bold: true, color: C.blue, fontFamily: "Georgia" });
  addText(s, "accuracy pada 50 data uji", 74, 356, 400, 38, { fontSize: 20, bold: true, color: C.navy });
  addText(s, "Dataset dibagi secara stratified: 200 train dan 50 test.", 74, 412, 400, 58, { fontSize: 17, color: C.muted });
  metric(s, "98.18%", "MACRO PRECISION", 540, 194, 308, C.navy);
  metric(s, "98.00%", "MACRO RECALL", 868, 194, 308, C.gold);
  metric(s, "97.99%", "MACRO F1-SCORE", 540, 358, 308, C.green);
  metric(s, "49/50", "PREDIKSI BENAR", 868, 358, 308, C.blue);
  panel(s, 540, 522, 636, 82, { fill: C.sky, line: C.sky });
  addText(s, "Interpretasi: performa tinggi pada data uji internal, tetapi belum menjamin generalisasi pada bahasa mahasiswa di dunia nyata.", 568, 544, 580, 42, { fontSize: 16, bold: true, color: C.navy, align: "center" });
  addFooter(s);
  addNotes(s, [
    "Internal metrics from artifacts/evaluation/evaluation_summary.json and classification_report.csv (accessed 2026-07-27).",
    "Scikit-learn model evaluation guide: https://scikit-learn.org/stable/modules/model_evaluation.html (accessed 2026-07-27).",
  ]);
}

// 12 — Confusion matrix and analysis
{
  const s = deck.slides.add();
  addHeader(s, 12, "Confusion matrix dan analisis kesalahan");
  const img = await imageBytes(path.join(ROOT, "artifacts/evaluation/confusion_matrix.png"));
  s.images.add({
    blob: img,
    contentType: "image/png",
    alt: "Confusion matrix lima intent pada data uji",
    fit: "contain",
    position: { left: 64, top: 184, width: 590, height: 430 },
  });
  panel(s, 690, 184, 526, 430, { fill: C.white, line: C.line });
  pill(s, "1 KESALAHAN", 722, 214, 142, "#F8E4E4", C.red);
  addText(s, "Aktual", 722, 280, 78, 24, { fontSize: 12, bold: true, color: C.muted });
  addText(s, "pendaftaran_krs", 816, 278, 344, 26, { fontSize: 17, bold: true, color: C.navy });
  addText(s, "Prediksi", 722, 326, 78, 24, { fontSize: 12, bold: true, color: C.muted });
  addText(s, "syarat_beasiswa", 816, 324, 344, 26, { fontSize: 17, bold: true, color: C.red });
  addText(s, "Kalimat", 722, 376, 78, 24, { fontSize: 12, bold: true, color: C.muted });
  addText(s, "\"saya ingin daftar mata kuliah semester depan\"", 816, 370, 344, 56, { fontSize: 16, italic: true, color: C.ink });
  addLine(s, 722, 452, 442, 0, C.line, 1);
  addText(s, "Penyebab", 722, 476, 92, 24, { fontSize: 12, bold: true, color: C.blue });
  addText(s, "Kata “daftar” dan konteks “semester depan” muncul pada beberapa domain sehingga batas intent berdekatan.", 722, 512, 442, 74, { fontSize: 16, color: C.muted });
  addFooter(s);
  addNotes(s, ["Internal confusion matrix and misclassification record from artifacts/evaluation/confusion_matrix.png and misclassified_examples.csv (accessed 2026-07-27)."]);
}

// 13 — Demo scenarios
{
  const s = deck.slides.add();
  addHeader(s, 13, "Rencana Demo — tiga skenario");
  const scenarios = [
    ["01", "FAQ langsung", "Tanya jadwal ujian → model memberi respons dan confidence.", "jadwal_ujian"],
    ["02", "KRS multi-turn", "Intent KRS → NIM → kode MK → konfirmasi ya/tidak.", "pendaftaran_krs"],
    ["03", "Portal & log", "Tanya akses portal → tampilkan jawaban → unduh log CSV.", "akses_portal"],
  ];
  scenarios.forEach((d, i) => {
    const y = 184 + i * 146;
    panel(s, 64, y, 1152, 118, { fill: i === 1 ? C.navy : C.white, line: i === 1 ? C.navy : C.line });
    addText(s, d[0], 92, y + 31, 64, 40, { fontSize: 29, bold: true, color: i === 1 ? C.gold : C.blue, fontFamily: "Georgia" });
    addText(s, d[1], 184, y + 24, 250, 34, { fontSize: 22, bold: true, color: i === 1 ? C.white : C.navy });
    addText(s, d[2], 458, y + 25, 514, 52, { fontSize: 16, color: i === 1 ? "#D8E3EF" : C.muted });
    pill(s, d[3], 990, y + 39, 190, i === 1 ? C.gold : C.sky, C.navy);
  });
  addText(s, "Tunjukkan CLI terlebih dahulu, lalu UI agar logika sistem dan pengalaman pengguna sama-sama terlihat.", 64, 630, 1152, 30, { fontSize: 17, bold: true, color: C.blue, align: "center" });
  addFooter(s);
  addNotes(s, ["Internal demo plan derived from the UAS requirement and implemented flows (accessed 2026-07-27)."], "Durasi demo yang disarankan: 3–4 menit dari total video 5–10 menit.");
}

// 14 — Conclusion
{
  const s = deck.slides.add();
  addHeader(s, 14, "Kesimpulan dan pengembangan berikutnya");
  panel(s, 64, 184, 548, 278, { fill: C.navy, line: C.navy });
  addText(s, "KESIMPULAN", 96, 216, 160, 24, { fontSize: 12, bold: true, color: C.gold });
  addText(s, "Chatbot memenuhi seluruh komponen minimum UAS: data, NLP, dialog multi-turn, evaluasi, CLI, UI, dan logging.", 96, 268, 444, 132, { fontSize: 27, bold: true, color: C.white, fontFamily: "Georgia", lineSpacing: 1.03 });
  panel(s, 668, 184, 548, 278, { fill: C.white, line: C.line });
  addText(s, "KETERBATASAN", 700, 216, 160, 24, { fontSize: 12, bold: true, color: C.red });
  bulletList(s, [
    "Dataset masih sintetis dan domain terbatas.",
    "Regex belum mencakup semua variasi slot.",
    "Belum terhubung ke sistem akademik resmi.",
  ], 700, 266, 462, 58, 17);
  panel(s, 64, 492, 1152, 118, { fill: C.sky, line: C.sky });
  addText(s, "PEMBAGIAN TUGAS", 94, 520, 150, 22, { fontSize: 12, bold: true, color: C.blue });
  addText(s, "Anggota 1 — dataset & NLP", 270, 516, 276, 30, { fontSize: 16, bold: true, color: C.navy });
  addText(s, "Anggota 2 — dialog & pengujian", 552, 516, 310, 30, { fontSize: 16, bold: true, color: C.navy });
  addText(s, "Anggota 3 — UI & dokumentasi", 872, 516, 292, 30, { fontSize: 16, bold: true, color: C.navy });
  addText(s, "Ganti placeholder nama anggota sebelum pengumpulan.", 270, 560, 894, 24, { fontSize: 13, italic: true, color: C.muted });
  addFooter(s, "Terima kasih • Tanya jawab");
  addNotes(s, ["Internal conclusion based on project implementation and test artifacts (accessed 2026-07-27)."], "Penutup: tekankan bahwa 98% adalah hasil data uji internal, bukan klaim produksi.");
}

async function writeBlob(file, blob) {
  await fs.writeFile(file, new Uint8Array(await blob.arrayBuffer()));
}

await fs.mkdir(OUT, { recursive: true });
await fs.mkdir(QA, { recursive: true });

for (const [i, slide] of deck.slides.items.entries()) {
  const stem = `slide-${String(i + 1).padStart(2, "0")}`;
  await writeBlob(path.join(QA, `${stem}.png`), await deck.export({ slide, format: "png", scale: 1 }));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(QA, `${stem}.layout.json`), await layout.text());
}

await writeBlob(path.join(QA, "deck-montage.webp"), await deck.export({ format: "webp", montage: true, scale: 0.6 }));
const pptx = await PresentationFile.exportPptx(deck);
await pptx.save(path.join(OUT, "Presentasi_Chatbot_FAQ_UMB.pptx"));
console.log(`Generated ${deck.slides.items.length} slides.`);
