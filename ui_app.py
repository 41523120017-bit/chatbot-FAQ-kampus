import streamlit as st
import json
import os
import datetime
import joblib
from dialog_manager import DialogManager

# -------------------------------------------------------------------
# 1. KONFIGURASI HALAMAN
# -------------------------------------------------------------------
st.set_page_config(
    page_title="SIAKAD AI Assistant - Mercu Buana",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CUSTOM CSS STYLE (FIXED TEXT CONTRAST & DARK THEME)
# -------------------------------------------------------------------
st.markdown("""
<style>
    /* 1. Paksa Background Utama & Teks Utama */
    .stApp {
        background-color: #0b0f19 !important;
    }

    /* 2. PAKSA SELURUH TEKS MARKDOWN BERWARNA PUTIH TAJAM */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] div {
        color: #ffffff !important;
        font-size: 1rem !important;
    }

    /* 3. Perbaikan Teks Sidebar */
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {
        color: #f1f5f9 !important;
    }

    /* 4. Chat Bubble User (Biru Slate) */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background-color: #1e293b !important;
        border: 1px solid #3b82f6 !important;
    }

    /* 5. Chat Bubble Bot (Gelap Navy) */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #0f172a !important;
        border: 1px solid #334155 !important;
    }

    /* 6. Perbaikan Input Chat Box (Placeholder & Teks yang Diketik) */
    .stChatInput textarea {
        color: #ffffff !important;
    }
    .stChatInput textarea::placeholder {
        color: #94a3b8 !important;
    }
    .stChatInput > div {
        background-color: #1e293b !important;
        border: 1px solid #475569 !important;
    }

    /* Header Box Custom */
    .header-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 20px 24px;
        border-radius: 16px;
        border: 1px solid #334155;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 3. LOAD MODEL & SESSION STATE
# -------------------------------------------------------------------
MODEL_PATH = 'intent_model.pkl'

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        st.error(f"⚠️ Model '{MODEL_PATH}' tidak ditemukan. Silakan jalankan 'python train_eval.py' dulu.")
        st.stop()
    return joblib.load(MODEL_PATH)

model = load_model()

if 'dialog_manager' not in st.session_state:
    st.session_state.dialog_manager = DialogManager(model)

if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 **Halo! Selamat Datang di SIAKAD AI Assistant.**\nAda yang bisa saya bantu hari ini? Anda bisa menanyakan info **KRS, Jadwal Ujian, UKT, atau Beasiswa**."}
    ]

# -------------------------------------------------------------------
# 4. SIDEBAR DASHBOARD & QUICK ACTIONS
# -------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/graduation-cap.png", width=65)
    st.markdown("## **SIAKAD Bot**")
    st.caption("🟢 **Status:** Active & Ready")
    st.markdown("---")

    st.markdown("### ⚡ **Aksi Cepat**")
    if st.button("📝 Cek KRS & Matkul"):
        st.session_state.quick_input = "bagaimana cara pengisian krs?"
    if st.button("📅 Jadwal Uts & Uas"):
        st.session_state.quick_input = "dimana liat jadwal uts dan uas?"
    if st.button("💳 Cara Bayar UKT"):
        st.session_state.quick_input = "sy mau bayar ukt lewat mandiri gmna"
    if st.button("🎓 Info Beasiswa"):
        st.session_state.quick_input = "apa saja syarat mendaftar beasiswa?"

    st.markdown("---")
    
    # Tombol Reset Percakapan
    st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
    if st.button("🔄 Reset Sesi Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 **Sesi telah diperbarui.** Silakan masukkan NIM Anda atau tanyakan informasi akademik."}
        ]
        st.session_state.dialog_manager = DialogManager(model)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 **Info Sistem**")
    st.markdown("""
    <div class="metric-card">
        <small style="color:#94a3b8;">Engine NLP</small><br>
        <strong>TF-IDF + Logistic Regression</strong>
    </div>
    <div class="metric-card">
        <small style="color:#94a3b8;">Database Target</small><br>
        <strong>SIAKAD Local JSON (Realtime)</strong>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# 5. HEADER UTAMA
# -------------------------------------------------------------------
st.markdown("""
<div class="header-card">
    <div class="header-title">🎓 Pusat Layanan Informasi Akademik</div>
    <div class="header-subtitle">Sistem Asisten Cerdas Terintegrasi SIAKAD & Modul Pengisian KRS Interaktif</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 6. CHAT HISTORY DISPLAY
# -------------------------------------------------------------------
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# -------------------------------------------------------------------
# 7. INPUT & PROCESSING LOGIC
# -------------------------------------------------------------------
user_input = st.chat_input("Ketik pertanyaan Anda di sini (contoh: 'cara isi krs', 'link portal')...")

if hasattr(st.session_state, 'quick_input') and st.session_state.quick_input:
    user_input = st.session_state.quick_input
    st.session_state.quick_input = None

if user_input:
    # Append & Display User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Process via Dialog Manager
    bot_response = st.session_state.dialog_manager.process_message(user_input)

    # Append & Display Bot Response
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(bot_response)

    # Logging ke chat_logs.json
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_input": user_input,
        "bot_response": bot_response
    }
    with open("chat_logs.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    st.rerun()
