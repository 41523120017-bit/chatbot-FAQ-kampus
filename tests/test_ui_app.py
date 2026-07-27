from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def test_ui_starts_without_exception_and_exposes_core_controls(monkeypatch, tmp_path):
    monkeypatch.setenv("CHATBOT_LOG_PATH", str(tmp_path / "ui_log.csv"))

    app = AppTest.from_file(str(ROOT / "ui_app.py"), default_timeout=20).run()

    assert not app.exception
    assert any("SIAKAD Assist" in title.value for title in app.title)
    assert any(button.label == "Reset sesi" for button in app.button)
    assert len(app.chat_input) == 1


def test_ui_chat_uses_dialog_manager_and_writes_log(monkeypatch, tmp_path):
    log_path = tmp_path / "ui_log.csv"
    monkeypatch.setenv("CHATBOT_LOG_PATH", str(log_path))
    app = AppTest.from_file(str(ROOT / "ui_app.py"), default_timeout=20).run()

    app.chat_input[0].set_value("cara bayar ukt melalui bca").run()

    assert not app.exception
    rendered_messages = [message.markdown[0].value for message in app.chat_message]
    assert any("Pembayaran UKT" in message for message in rendered_messages)
    assert log_path.exists()
    assert "pembayaran_ukt" in log_path.read_text(encoding="utf-8")


def test_ui_has_no_remote_visual_dependencies():
    source = (ROOT / "ui_app.py").read_text(encoding="utf-8")

    assert "fonts.googleapis.com" not in source
    assert "img.icons8.com" not in source
    assert "http://" not in source


def test_ui_css_explicitly_controls_light_theme_contrast():
    source = (ROOT / "ui_app.py").read_text(encoding="utf-8")

    assert ".stApp {\n    background: var(--canvas);\n    color: var(--ink);" in source
    assert (
        '[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"]'
        in source
    )
    assert (
        '[data-testid="stChatInput"] {\n    background: var(--surface);'
        in source
    )


def test_ui_uses_main_quick_actions_instead_of_decorative_service_index(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("CHATBOT_LOG_PATH", str(tmp_path / "ui_log.csv"))
    source = (ROOT / "ui_app.py").read_text(encoding="utf-8")
    app = AppTest.from_file(str(ROOT / "ui_app.py"), default_timeout=20).run()

    button_labels = {button.label for button in app.button}
    assert 'class="service-index"' not in source
    assert {"Tanya KRS", "Jadwal ujian", "Bayar UKT", "Syarat beasiswa"} <= button_labels
