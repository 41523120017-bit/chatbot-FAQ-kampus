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
# 2. ADVANCED CUSTOM CSS (GLASSMORPHISM & MODERN DARK THEME)
# -------------------------------------------------------------------
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Main Container Background */
    .stApp {
        background: #090d16;
        color: #f1f5f9;
    }

    /* Header Banner Styling */
    .header-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 24px 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
    }
    
    .header-title {
        font-size: 1.75rem;
        font-weight: 700;
        background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 6px 0;
    }
    
    .header-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* Chat Message Bubble Customization */
    [data-testid="stChatMessage"] {
        border-radius: 16px !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* User Chat Bubble */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background-color: #1e293b !important;
        border-left: 4px solid #3b82f6 !important;
    }

    /* Assistant Chat Bubble */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #0f172a !important;
        border-left: 4px solid #10b981 !important;
    }

    /* Quick Action Button Styling */
    .stButton > button {
        border-radius: 12px !important;
        padding: 10px 16px !important;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: all 0.25s ease-in-out !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 15px rgba(37, 99, 235, 0.35) !important;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    }

    /* Reset Button Styling */
    .reset-btn > button {
        background: rgba(239, 68, 68, 0.15) !important;
        color: #f87171 !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
    }
    
    .reset-btn > button:hover {
        background: rgba(239, 68, 68, 0.3) !important;
        box-shadow: 0 8px 15px rgba(239, 68, 68, 0.2) !important;
    }

    /* Input Chat Styling */
    .stChatInput > div {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        background-color: #1e293b !important;
    }

    /* Metric Cards in Sidebar */
    .metric-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 8px;
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