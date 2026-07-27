import re
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DELIVERABLES = ROOT / "deliverables"
REPORT_DOCX = DELIVERABLES / "Laporan_Proyek_Chatbot_FAQ_UMB.docx"
REPORT_PDF = DELIVERABLES / "Laporan_Proyek_Chatbot_FAQ_UMB.pdf"
DECK_PPTX = DELIVERABLES / "Presentasi_Chatbot_FAQ_UMB.pptx"
DECK_PDF = DELIVERABLES / "Presentasi_Chatbot_FAQ_UMB.pdf"
BUNDLED_PYTHON = Path(
    "/Users/koala/.cache/codex-runtimes/codex-primary-runtime/"
    "dependencies/python/bin/python3"
)


def office_xml_text(path: Path, member_pattern: str) -> str:
    with zipfile.ZipFile(path) as archive:
        members = sorted(name for name in archive.namelist() if re.fullmatch(member_pattern, name))
        return "\n".join(
            re.sub(r"<[^>]+>", " ", archive.read(name).decode("utf-8"))
            for name in members
        )


def pdf_page_count(path: Path) -> int:
    command = [
        str(BUNDLED_PYTHON),
        "-c",
        "from pypdf import PdfReader; import sys; print(len(PdfReader(sys.argv[1]).pages))",
        str(path),
    ]
    return int(subprocess.check_output(command, text=True).strip())


def test_report_contains_required_sections_and_stays_within_page_limit():
    text = office_xml_text(REPORT_DOCX, r"word/document\.xml")

    for section in [
        "Pendahuluan",
        "Teori Singkat NLP",
        "Desain dan Implementasi",
        "Evaluasi dan Analisis",
        "Kesimpulan",
        "Pembagian Tugas",
        "Daftar Pustaka",
    ]:
        assert section in text
    assert pdf_page_count(REPORT_PDF) <= 10


def test_presentation_has_at_least_twelve_slides_and_required_topics():
    with zipfile.ZipFile(DECK_PPTX) as archive:
        slide_members = [
            name
            for name in archive.namelist()
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
        ]
    visible_text = office_xml_text(DECK_PPTX, r"ppt/slides/slide\d+\.xml")

    assert len(slide_members) >= 12
    for topic in ["Masalah", "Arsitektur", "Dataset", "Evaluasi", "Demo"]:
        assert topic in visible_text
    assert pdf_page_count(DECK_PDF) == len(slide_members)
