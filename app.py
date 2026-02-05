import streamlit as st
from PIL import Image, ImageOps
import io
import urllib.parse
from datetime import datetime

# 1. Konfigurasi Dasar
st.set_page_config(page_title="Wedding Gallery Live", layout="wide", initial_sidebar_state="collapsed")

# 2. Inisialisasi Session State
if 'gallery' not in st.session_state: st.session_state.gallery = []
if 'frame' not in st.session_state: st.session_state.frame = None
if 'vendor_logo' not in st.session_state: st.session_state.vendor_logo = None
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wedding_name' not in st.session_state: st.session_state.wedding_name = "Pengantin Pria & Wanita"
if 'vendor_name' not in st.session_state: st.session_state.vendor_name = "Nama Vendor Anda"

def reset_data():
    st.session_state.gallery = []
    st.session_state.frame = None
    st.session_state.vendor_logo = None
    st.session_state.wedding_name = "Pengantin Pria & Wanita"
    st.session_state.vendor_name = "Nama Vendor Anda"
    st.rerun()

# --- CSS ADAPTIF ---
st.markdown("""
    <style>
    .stApp h1, .stApp p, .stApp label { color: var(--text-color) !important; }
    .header-text { text-align: center; }
    .wa-float {
        position: fixed; top: 20px; right: 20px; background-color: #25D366;
        color: white !important; padding: 8px 15px; border-radius: 50px;
        z-index: 1000; text-decoration: none; font-weight: bold; font-size: 12px;
        display: flex; align-items: center; gap: 5px; box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Tombol Share
APP_URL = "https://aplikasi-foto-wedding-live-sharing-bingkai-ko2zzkcx2nhyww9o2dv.streamlit.app/"
text_share = urllib.parse.quote(f"Lihat foto {st.session_state.wedding_name} di: {APP_URL}")
st.markdown(f'<a href="https://wa.me/?text={text_share}" class="wa-float" target="_blank">Bagikan</a>', unsafe_allow_html=True)

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.title("🔐 Kendali Admin")
    if not st.session_state.logged_in:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u == "admin" and p == "wedding123":
                st.session_state.logged_in = True; st.rerun()
    else:
        # INPUT NAMA PENGANTIN & VENDOR
        st.session_state.wedding_name = st.text_input("Nama Pengantin", st.session_state.wedding_name)
        st.session_state.vendor_name = st.text_input("Nama Vendor", st.session_state.vendor_name)
        
        st.divider()
        l_up = st.file_uploader("Upload Logo Vendor", type=["png"])
        if l_up: st.session_state.vendor_logo = Image.open(l_up).convert("RGBA")
        
        st.divider()
        if st.session_state.frame is not None:
            st.image(st.session_state.frame, caption="Bingkai Aktif")
            if st.button("🗑️ Ganti Bingkai"): st.session_state.frame = None; st.rerun()
        else:
            f_up = st.file_uploader("Bingkai (PNG)", type=["png"])
            if f_up: st.session_state.frame = Image.open(f_up).convert("RGBA"); st.rerun()
        
        st.divider()
        if st.button("🚨 RESET TOTAL", type="primary", use_container_width=True): reset_data()
        if st.button("Logout", use_container_width=True): st.session_state.logged_in = False; st.rerun()

# --- HEADER ---
st.markdown(f'<h1 class="header-text">✨ Wedding Gallery of {st.session_state.wedding_name}</h1>', unsafe_
