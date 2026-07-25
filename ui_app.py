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
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* 1. Global Background & Universal Text Color Force */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #0b0f19 !important;
        color: #f8fafc !important;
    }

    /* Paksa seluruh paragraf, teks, dan header berwarna terang */
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp div {
        color: #f8fafc !important;
    }

    /* 2. Header Box Styling */
    .header-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 24px 30px;
        border-radius: 16px;
        border: 1px solid #334155;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    
    .header-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #60a5fa !important;
        margin: 0 0 6px 0;
    }
    
    .header-subtitle {
        color: #cbd5e1 !important;
        font-size: 0.95rem;
        margin: 0;
    }

    /* 3. Sidebar Styling & Text */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }

    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* 4. Chat Bubble Container & Text Contrast Fix */
    [data-testid="stChatMessage"] {
        border-radius: 14px !important;
        padding: 16px 20px !important;
        margin-bottom: 12px !important;
        border: 1px solid #334155 !important;
    }

    /* Memastikan teks isi chat berwarna putih terang */
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] span, 
    [data-testid="stChatMessage"] div {
        color: #ffffff !important;
        font-size: 0.98rem !important;
        line-height: 1.6 !important;
    }

    /* User Chat Bubble (Biru Slate) */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background-color: #1e293b !important;
        border-left: 4px solid #3b82f6 !important;
    }

    /* Assistant Chat Bubble (Navy Dark) */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #0f172a !important;
        border-left: 4px solid #10b981 !important;
    }

    /* 5. Input Text Chat Fix */
    .stChatInput textarea {
        color: #ffffff !important;
        background-color: #1e293b !important;
    }
    
    .stChatInput > div {
        border: 1px solid #475569 !important;
        background-color: #1e293b !important;
    }

    /* 6. Button Styling */
    .stButton > button {
        width: 100%;
        border-radius: 10px !important;
        background: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 10px 16px !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background: #3b82f6 !important;
        transform: translateY(-2px) !important;
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
