from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_operational_files_exist():
    for relative_path in ["README.md", "LINK_VIDEO.txt", ".gitignore"]:
        assert (ROOT / relative_path).is_file()


def test_requirements_cover_runtime_testing_and_document_outputs():
    requirements = {
        line.strip().casefold()
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    assert {
        "streamlit",
        "joblib",
        "numpy",
        "scikit-learn",
        "pandas",
        "matplotlib",
        "pytest",
        "python-docx",
        "python-pptx",
        "reportlab",
    } <= requirements
