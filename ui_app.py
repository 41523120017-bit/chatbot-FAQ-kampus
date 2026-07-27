"""Antarmuka Streamlit untuk SIAKAD Assist."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

import joblib
import streamlit as st

from chat_logger import log_interaction
from dialog_manager import DialogManager


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "intent_model.pkl"
LOG_PATH = Path(
    os.environ.get("CHATBOT_LOG_PATH", str(BASE_DIR / "logs" / "chat_history.csv"))
)

st.set_page_config(
    page_title="SIAKAD Assist — Universitas Mercu Buana",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="auto",
)


THEME_CSS = """
<style>
:root {
    --navy: #0b1f3a;
    --blue: #0f5cbd;
    --blue-soft: #eaf3ff;
    --gold: #f4b942;
    --canvas: #f6f8fb;
    --surface: #ffffff;
    --ink: #182230;
    --muted: #526071;
    --line: #d6dee8;
    --success: #16794e;
    --danger: #b42318;
}

html, body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    color: var(--ink);
}

.stApp {
    background: var(--canvas);
    color: var(--ink);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"] {
    max-width: 920px;
    padding-top: 1.5rem;
    padding-bottom: 8rem;
}

h1, h2, h3 {
    color: var(--ink) !important;
    letter-spacing: -0.03em;
}
h1 {
    font-size: clamp(2.25rem, 5vw, 3.35rem) !important;
    line-height: 1.02 !important;
    margin: .2rem 0 .45rem !important;
}

.service-kicker {
    color: var(--blue);
    font-size: .74rem;
    font-weight: 800;
    letter-spacing: .14em;
    text-transform: uppercase;
    border-top: 3px solid var(--gold);
    padding-top: .85rem;
}
.hero-copy {
    color: var(--muted);
    font-size: 1rem;
    max-width: 650px;
    line-height: 1.6;
    margin-bottom: 1rem;
}
.quick-label {
    color: var(--ink);
    font-size: .84rem;
    font-weight: 750;
    margin: .15rem 0 .25rem;
}

.state-strip {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    border: 1px solid var(--line);
    background: var(--surface);
    padding: .68rem .85rem;
    border-radius: 10px;
    margin: .7rem 0 1rem;
}
.state-label {
    color: var(--muted);
    font-size: .8rem;
    font-weight: 650;
}
.state-value {
    color: var(--ink);
    font-size: .82rem;
    font-weight: 750;
}
.state-value::before {
    content: "";
    display: inline-block;
    width: 8px;
    height: 8px;
    margin-right: .45rem;
    border-radius: 50%;
    background: var(--success);
}

[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] h3 { color: var(--navy) !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: var(--muted) !important;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: var(--muted) !important;
    opacity: 1 !important;
}
.sidebar-mark {
    width: 52px;
    height: 52px;
    display: grid;
    place-items: center;
    background: var(--navy);
    color: var(--gold);
    border-radius: 12px;
    font-family: Georgia, serif;
    font-size: 1.35rem;
    font-weight: 700;
    margin: .4rem 0 .8rem;
}
.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: var(--success);
    border-radius: 50%;
    margin-right: .4rem;
}

.stButton > button, .stDownloadButton > button {
    width: 100%;
    border-radius: 9px;
    border: 1px solid var(--line);
    color: var(--ink);
    background: var(--surface);
    font-weight: 700;
    min-height: 2.7rem;
    transition: border-color .15s ease, background .15s ease, color .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--blue);
    color: var(--blue);
    background: var(--blue-soft);
}
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible {
    outline: 3px solid rgba(15,92,189,.28);
    outline-offset: 2px;
}

[data-testid="stChatMessage"] {
    color: var(--ink) !important;
    border-radius: 12px;
    border: 1px solid var(--line);
    border-left: 4px solid var(--blue);
    padding: .85rem 1rem;
    margin-bottom: .75rem;
    background: var(--surface);
    box-shadow: 0 2px 8px rgba(11,31,58,.045);
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] strong,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] span {
    color: var(--ink) !important;
    opacity: 1 !important;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
    line-height: 1.58;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    border-color: #b9d3f4;
    border-left: 1px solid #b9d3f4;
    background: var(--blue-soft);
}
[data-testid="stChatMessage"] code {
    color: var(--navy) !important;
    background: #e9eef5 !important;
    border-radius: 4px;
    padding: .12rem .3rem;
}
[data-testid="stBottomBlockContainer"] {
    background: linear-gradient(180deg, rgba(246,248,251,0), var(--canvas) 28%);
    padding-top: 1.4rem;
}
[data-testid="stBottom"] > div {
    background: var(--canvas) !important;
}
[data-testid="stChatInput"] {
    background: var(--surface);
    border: 1px solid #aebccd;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(11,31,58,.10);
}
[data-testid="stChatInput"] div {
    background: var(--surface) !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
    caret-color: var(--blue) !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #667588 !important;
    -webkit-text-fill-color: #667588 !important;
    opacity: 1 !important;
}
[data-testid="stChatInput"] button {
    color: var(--blue) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--blue);
    box-shadow: 0 0 0 3px rgba(15,92,189,.14), 0 8px 24px rgba(11,31,58,.10);
}
.stChatInput textarea {
    color: var(--ink) !important;
}

.demo-note {
    background: #fff8e7;
    border: 1px solid #edcf88;
    border-radius: 9px;
    padding: .8rem .9rem;
    color: #61470d;
    font-size: .84rem;
    line-height: 1.5;
}
.demo-note strong, .demo-note code {
    color: #533b08 !important;
}
.sidebar-meta {
    color: var(--muted);
    font-size: .78rem;
    line-height: 1.5;
}

@media (max-width: 720px) {
    [data-testid="stMainBlockContainer"] {
        padding-top: .85rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    h1 { font-size: 2.35rem !important; }
    .hero-copy { font-size: .95rem; }
    [data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: .55rem !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        width: auto !important;
        min-width: 0 !important;
        flex: none !important;
    }
    .state-strip { align-items: flex-start; flex-direction: column; gap: .25rem; }
    [data-testid="stChatMessage"] { padding: .75rem .8rem; }
}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { transition: none !important; }
}
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)


@st.cache_resource
def load_model(model_path: str):
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Model tidak ditemukan di {path}. Jalankan `python3 train_eval.py`."
        )
    return joblib.load(path)


try:
    model = load_model(str(MODEL_PATH))
except (FileNotFoundError, OSError, ValueError) as error:
    st.error(str(error))
    st.stop()

if "dialog_manager" not in st.session_state:
    st.session_state.dialog_manager = DialogManager(model)
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:12]
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Halo! Saya siap membantu informasi **KRS, pembayaran UKT, "
                "jadwal ujian, beasiswa, dan akses portal SIAKAD**."
            ),
        }
    ]

selected_prompt = None

with st.sidebar:
    st.markdown('<div class="sidebar-mark">UM</div>', unsafe_allow_html=True)
    st.subheader("Bantuan Akademik")
    st.markdown(
        '<span class="status-dot"></span>Model siap digunakan',
        unsafe_allow_html=True,
    )
    st.divider()
    if st.button("Reset sesi", type="secondary"):
        st.session_state.dialog_manager = DialogManager(model)
        st.session_state.messages = [
            {"role": "assistant", "content": "Sesi baru siap. Apa yang ingin ditanyakan?"}
        ]
        st.session_state.session_id = uuid.uuid4().hex[:12]
        st.rerun()

    if LOG_PATH.exists():
        st.download_button(
            "Unduh log CSV",
            data=LOG_PATH.read_bytes(),
            file_name="chat_history.csv",
            mime="text/csv",
        )
    st.markdown(
        '<div class="demo-note"><strong>Data demo</strong><br>'
        'Gunakan NIM <code>41523120017</code> untuk mencoba alur KRS. '
        'Tidak terhubung ke SIAKAD produksi.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-meta">Model: TF-IDF + Logistic Regression<br>'
        'Cakupan: 5 intent akademik</div>',
        unsafe_allow_html=True,
    )


st.markdown('<div class="service-kicker">Universitas Mercu Buana · Layanan akademik</div>', unsafe_allow_html=True)
st.title("SIAKAD Assist")
st.markdown(
    '<div class="hero-copy">Tanyakan kebutuhan akademik dengan bahasa sehari-hari. '
    'Untuk KRS, asisten akan memandu Anda langkah demi langkah.</div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="quick-label">Pilih topik atau tulis pertanyaan Anda</div>', unsafe_allow_html=True)
quick_prompts = {
    "Tanya KRS": "saya ingin mengisi krs",
    "Jadwal ujian": "jadwal uas dapat dilihat di mana",
    "Bayar UKT": "bagaimana cara bayar ukt",
    "Syarat beasiswa": "apa syarat mendaftar beasiswa",
}
quick_columns = st.columns(4)
for column, (label, prompt) in zip(quick_columns, quick_prompts.items()):
    with column:
        if st.button(label, key=f"quick_{label}", use_container_width=True):
            selected_prompt = prompt

manager = st.session_state.dialog_manager
state_names = {
    "IDLE": "Siap membantu",
    "WAITING_FOR_NIM": "Silakan masukkan NIM",
    "SELECTING_MATKUL": "Silakan pilih mata kuliah",
    "WAITING_CONFIRMATION": "Periksa dan konfirmasi KRS",
}
st.markdown(
    '<div class="state-strip"><span class="state-label">Status layanan</span>'
    f'<span class="state-value">{state_names.get(manager.state, manager.state)}</span></div>',
    unsafe_allow_html=True,
)

for message in st.session_state.messages:
    avatar = ":material/school:" if message["role"] == "assistant" else ":material/person:"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

typed_prompt = st.chat_input("Tulis pertanyaan akademik Anda…")
user_input = selected_prompt or typed_prompt
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    state_before = manager.state
    response = manager.process_message(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    log_interaction(
        log_path=LOG_PATH,
        session_id=st.session_state.session_id,
        channel="ui",
        user_message=user_input,
        bot_response=response,
        intent=manager.last_intent,
        confidence=manager.last_confidence,
        state_before=state_before,
        state_after=manager.state,
    )
    st.rerun()
