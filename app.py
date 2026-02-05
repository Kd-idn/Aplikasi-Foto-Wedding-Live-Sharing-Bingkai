import streamlit as st
from PIL import Image, ImageOps
import io
import urllib.parse

# 1. Konfigurasi Awal
st.set_page_config(page_title="Wedding Gallery", layout="wide", initial_sidebar_state="collapsed")

# 2. Fungsi Inisialisasi / Reset Data
def reset_data():
    st.session_state.gallery = []
    st.session_state.frame = None
    st.session_state.vendor_logo = None
    st.session_state.wedding_name = "Pengantin Pria & Wanita"
    st.session_state.vendor_name = "Nama Vendor Anda"
    st.toast("Semua data telah di-reset!", icon="🗑️")

# Inisialisasi Session State jika belum ada
if 'gallery' not in st.session_state: st.session_state.gallery = []
if 'frame' not in st.session_state: st.session_state.frame = None
if 'vendor_logo' not in st.session_state: st.session_state.vendor_logo = None
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wedding_name' not in st.session_state: st.session_state.wedding_name = "Pengantin Pria & Wanita"
if 'vendor_name' not in st.session_state: st.session_state.vendor_name = "Nama Vendor Anda"

APP_URL = "https://aplikasi-foto-wedding-live-sharing-bingkai-ko2zzkcx2nhyww9o2dv.streamlit.app/"

# --- CSS ADAPTIF & FLOATING SHARE ---
st.markdown(f"""
    <style>
    .header-text {{ color: var(--text-color); text-align: center; }}
    .wa-float {{
        position: fixed; top: 20px; right: 20px; background-color: #25D366;
        color: white !important; padding: 8px 15px; border-radius: 50px;
        z-index: 1000; text-decoration: none; font-weight: bold; font-size: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2); display: flex; align-items: center; gap: 5px;
    }}
    @media (max-width: 640px) {{ .wa-float {{ top: 10px; right: 10px; }} }}
    </style>
""", unsafe_allow_html=True)

# Tombol Share WA
text_share = urllib.parse.quote(f"Lihat foto {st.session_state.wedding_name} di: {APP_URL}")
st.markdown(f'<a href="https://wa.me/?text={text_share}" class="wa-float" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="15px"> Bagikan</a>', unsafe_allow_html=True)

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.title("🔐 Admin Panel")
    if not st.session_state.logged_in:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "admin" and pwd == "wedding123":
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.success("Akses Diterima")
        st.session_state.wedding_name = st.text_input("Nama Pengantin", st.session_state.wedding_name)
        st.session_state.vendor_name = st.text_input("Nama Vendor", st.session_state.vendor_name)
        
        # LOGO VENDOR: Dengan deteksi perubahan & tombol hapus spesifik
        logo_up = st.file_uploader("Upload Logo Vendor", type=["png"])
        if logo_up: 
            st.session_state.vendor_logo = Image.open(logo_up).convert("RGBA")
        if st.session_state.vendor_logo is not None:
            if st.button("❌ Hapus Logo Saja"):
                st.session_state.vendor_logo = None
                st.rerun()

        st.divider()
        # BINGKAI:
        if st.session_state.frame is not None:
            st.image(st.session_state.frame, caption="Bingkai Aktif")
            if st.button("🗑️ Ganti Bingkai"): st.session_state.frame = None; st.rerun()
        else:
            frame_up = st.file_uploader("Bingkai (PNG)", type=["png"])
            if frame_up: st.session_state.frame = Image.open(frame_up).convert("RGBA"); st.rerun()
        
        st.divider()
        # TOMBOL NUKLIR (RESET SEMUA)
        if st.button("🚨 RESET SEMUA SETELAN", use_container_width=True, type="primary"):
            reset_data()
            st.rerun()

        if st.button("Keluar (Logout)", use_container_width=True): 
            st.session_state.logged_in = False
            st.rerun()

# --- HEADER SECTION ---
st.markdown(f'<h1 class="header-text">✨ Wedding Gallery of {st.session_state.wedding_name}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="header-text" style="font-style:italic; opacity:0.8;">Powered by {st.session_state.vendor_name}</p>', unsafe_allow_html=True)

# Menampilkan logo hanya jika variabel vendor_logo ada isinya (bukan None)
if st.session_state.vendor_logo is not None:
    _, center_col, _ = st.columns([1, 0.3, 1])
    center_col.image(st.session_state.vendor_logo, use_container_width=True)

st.divider()

# --- FUNGSI RENDER GALERI ---
def render_gallery(suffix):
    if not st.session_state.gallery:
        st.info("Belum ada foto yang diunggah.")
        return
    mode = st.radio("Tampilan:", ["Grid", "List"], horizontal=True, key=f"m_{suffix}", label_visibility="collapsed")
    if mode == "Grid":
        cols = st.columns(3)
        for idx, photo in enumerate(st.session_state.gallery):
            with cols[idx % 3]:
                st.image(photo, use_container_width=True)
                buf = io.BytesIO(); photo.save(buf, format="JPEG", quality=95)
                st.download_button("📥 Simpan", buf.getvalue(), f"f_{idx}.jpg", key=f"b_{suffix}_{idx}", use_container_width=True)
    else:
        for idx, photo in enumerate(st.session_state.gallery):
            st.image(photo, use_container_width=True)
            buf = io.BytesIO(); photo.save(buf, format="JPEG", quality=95)
            st.download_button(f"📥 Simpan Foto {idx+1}", buf.getvalue(), f"f_{idx}.jpg", key=f"l_{suffix}_{idx}")
            st.divider()

# --- LOGIKA DASHBOARD ---
if st.session_state.logged_in:
    tab1, tab2 = st.tabs(["📤 Upload", "👁️ Preview"])
    with tab1:
        up = st.file_uploader("Upload", type=["jpg","jpeg","png"], label_visibility="collapsed")
        if up:
            if st.session_state.frame is None: st.warning("Bingkai kosong!")
            else:
                img = ImageOps.exif_transpose(Image.open(up)).convert("RGBA")
                f_res = st.session_state.frame.resize(img.size, Image.Resampling.LANCZOS)
                final = Image.alpha_composite(img, f_res)
                st.session_state.gallery.insert(0, final.convert("RGB"))
                st.toast("Berhasil!")
        render_gallery("adm")
    with tab2: render_gallery("pre")
else:
    render_gallery("gst")
