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
# 2. ULTRA HIGH-CONTRAST LIGHT THEME (CSS)
# -------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Latar Belakang Utama & Font */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    /* Paksa Semua Teks Markdown Berwarna Hitam/Charcoal Tajam */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] div {
        color: #0f172a !important;
        font-weight: 400 !important;
        line-height: 1.6 !important;
    }

    /* Header Banner Custom (Gradient Biru Kampus) */
    .header-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        padding: 24px 30px;
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2);
    }
    
    .header-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #ffffff !important;
        margin: 0 0 6px 0;
    }
    
    .header-subtitle {
        color: #e0f2fe !important;
        font-size: 0.95rem;
        margin: 0;
    }

    /* Sidebar Custom */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }

    /* Chat Bubble User (Biru Muda Segar) */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background-color: #e0f2fe !important;
        border: 1px solid #bae6fd !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
    }

    /* Chat Bubble Assistant (Putih Bersih dengan Border Shadow) */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03) !important;
    }

    /* Input Chat Box Fix (Teks Hitam Tajam) */
    .stChatInput textarea {
        color: #0f172a !important;
        background-color: #ffffff !important;
    }
    
    .stChatInput > div {
        background-color: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 12px !important;
    }

    /* Button Custom */
    .stButton > button {
        width: 100%;
        border-radius: 10px !important;
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 10px 16px !important;
        transition: all 0.2s !important;
    }

    .stButton > button:hover {
        background-color: #1d4ed8 !important;
        transform: translateY(-1px) !important;
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
        st.error(f"⚠️ Model '{MODEL_PATH}' tidak ditemukan. Jalankan 'python train_eval.py' terlebih dahulu.")
        st.stop()
    return joblib.load(MODEL_PATH)

model = load_model()

if 'dialog_manager' not in st.session_state:
    st.session_state.dialog_manager = DialogManager(model)

if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 **Selamat Datang di SIAKAD AI Assistant!**\nAda yang bisa saya bantu hari ini seputar **KRS, Jadwal Ujian, UKT, atau Beasiswa**?"}
    ]

# -------------------------------------------------------------------
# 4. SIDEBAR
# -------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/graduation-cap.png", width=65)
    st.markdown("<h2 style='color:#0f172a; margin-top:0;'>SIAKAD Bot</h2>", unsafe_allow_html=True)
    st.caption("🟢 **Status:** Active & Ready")
    st.markdown("---")

    st.markdown("<h4 style='color:#0f172a;'>⚡ Pertanyaan Cepat</h4>", unsafe_allow_html=True)
    if st.button("Cek KRS & Matkul"):
        st.session_state.quick_input = "bagaimana cara pengisian krs?"
    if st.button("Jadwal UTS & UAS"):
        st.session_state.quick_input = "dimana liat jadwal uts dan uas?"
    if st.button("Cara Bayar UKT"):
        st.session_state.quick_input = "sy mau bayar ukt lewat mandiri gmna"
    if st.button("Info Beasiswa"):
        st.session_state.quick_input = "apa saja syarat mendaftar beasiswa?"

    st.markdown("---")
    if st.button("🔄 Reset Sesi Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 **Sesi telah diperbarui.** Silakan tanyakan informasi akademik Anda."}
        ]
        st.session_state.dialog_manager = DialogManager(model)
        st.rerun()

# -------------------------------------------------------------------
# 5. HEADER UTAMA
# -------------------------------------------------------------------
st.markdown("""
<div class="header-card">
    <div class="header-title">🎓 Pusat Layanan Informasi Akademik</div>
    <div class="header-subtitle">Sistem Asisten Cerdas Terintegrasi SIAKAD & Modul Informasi Mahasiswa</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 6. DISPLAY CHAT MESSAGES
# -------------------------------------------------------------------
for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# -------------------------------------------------------------------
# 7. INPUT USER & LOGIC
# -------------------------------------------------------------------
user_input = st.chat_input("Ketik pertanyaan Anda di sini...")

if hasattr(st.session_state, 'quick_input') and st.session_state.quick_input:
    user_input = st.session_state.quick_input
    st.session_state.quick_input = None

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    bot_response = st.session_state.dialog_manager.process_message(user_input)

    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(bot_response)

    st.rerun()
