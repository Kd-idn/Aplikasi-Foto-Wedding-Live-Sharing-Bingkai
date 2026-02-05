import streamlit as st
from PIL import Image, ImageOps
import io
import urllib.parse

st.set_page_config(page_title="Wedding Gallery", layout="wide", initial_sidebar_state="collapsed")

# 1. Inisialisasi Data
if 'gallery' not in st.session_state: st.session_state.gallery = []
if 'frame' not in st.session_state: st.session_state.frame = None
if 'vendor_logo' not in st.session_state: st.session_state.vendor_logo = None
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'view_mode' not in st.session_state: st.session_state.view_mode = "Kotak"

# Inisialisasi Branding
if 'wedding_name' not in st.session_state: st.session_state.wedding_name = "Pengantin Pria & Wanita"
if 'vendor_name' not in st.session_state: st.session_state.vendor_name = "Nama Vendor Anda"

APP_URL = "https://aplikasi-foto-wedding-live-sharing-bingkai-ko2zzkcx2nhyww9o2dv.streamlit.app/"

# --- CSS ADAPTIF (Terang/Malam) & RESPONSIVE ---
st.markdown("""
    <style>
    /* Mengikuti variabel warna tema Streamlit */
    .stApp h1, .stApp p { color: inherit !important; }
    
    /* Tombol Share Adaptif */
    .share-container {
        display: flex; justify-content: flex-end; padding: 10px 0;
    }
    .wa-btn {
        background-color: #25D366; color: white !important;
        padding: 8px 16px; border-radius: 50px; text-decoration: none;
        display: inline-flex; align-items: center; gap: 8px; font-weight: bold; font-size: 14px;
    }

    @media (max-width: 640px) {
        .header-title { font-size: 1.6rem !important; text-align: center; }
        .header-subtitle { text-align: center; }
        .share-container { justify-content: center; }
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.title("🔐 Kendali Admin")
    if not st.session_state.logged_in:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "admin" and pwd == "wedding123":
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.success("Admin Aktif")
        st.session_state.wedding_name = st.text_input("Nama Pengantin", st.session_state.wedding_name)
        st.session_state.vendor_name = st.text_input("Nama Vendor", st.session_state.vendor_name)
        new_logo = st.file_uploader("Upload Logo Vendor", type=["png"])
        if new_logo: st.session_state.vendor_logo = Image.open(new_logo).convert("RGBA")
        
        st.divider()
        if st.session_state.frame is not None:
            st.image(st.session_state.frame, caption="Bingkai Aktif")
            if st.button("🗑️ Ganti Bingkai"): st.session_state.frame = None; st.rerun()
        else:
            new_frame = st.file_uploader("Upload Bingkai PNG", type=["png"])
            if new_frame: st.session_state.frame = Image.open(new_frame).convert("RGBA"); st.rerun()
        
        if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

# --- HEADER SECTION ---
text_share = urllib.parse.quote(f"Lihat foto {st.session_state.wedding_name} di: {APP_URL}")
wa_link = f"https://wa.me/?text={text_share}"

# Baris 1: Share di Pojok Kanan
st.markdown(f'<div class="share-container"><a class="wa-btn" href="{wa_link}" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="18px"> Bagikan</a></div>', unsafe_allow_html=True)

# Baris 2: Judul & Branding
st.markdown(f'<h1 class="header-title" style="text-align:center;">✨ Wedding Gallery of {st.session_state.wedding_name}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="header-subtitle" style="text-align:center; font-style:italic;">Powered by {st.session_state.vendor_name}</p>', unsafe_allow_html=True)

if st.session_state.vendor_logo:
    _, center_col, _ = st.columns([1, 0.4, 1])
    center_col.image(st.session_state.vendor_logo, use_container_width=True)

st.divider()

# --- LAYOUT SWITCHER (Kotak vs List) ---
col_mode1, col_mode2 = st.columns([0.8, 0.2])
with col_mode2:
    st.session_state.view_mode = st.radio("Tampilan:", ["Kotak", "List"], horizontal=True, label_visibility="collapsed")

# --- FUNGSI RENDER FOTO ---
def render_content():
    if not st.session_state.gallery:
        st.info("Galeri belum berisi foto.")
        return

    if st.session_state.view_mode == "Kotak":
        cols = st.columns(3) # Otomatis jadi 1 kolom di mobile
        for idx, photo in enumerate(st.session_state.gallery):
            with cols[idx % 3]:
                st.image(photo, use_container_width=True)
                buf = io.BytesIO(); photo.save(buf, format="JPEG", quality=95)
                st.download_button("📥 Simpan", buf.getvalue(), f"foto_{idx}.jpg", key=f"dl_k_{idx}", use_container_width=True)
    else: # Mode List
        for idx, photo in enumerate(st.session_state.gallery):
            st.image(photo, use_container_width=True)
            buf = io.BytesIO(); photo.save(buf, format="JPEG", quality=95)
            st.download_button(f"📥 Simpan Foto {idx+1}", buf.getvalue(), f"foto_{idx}.jpg", key=f"dl_l_{idx}")
            st.divider()

# --- DASHBOARD LOGIC ---
if st.session_state.logged_in:
    tab1, tab2 = st.tabs(["📤 Panel Fotografer", "👁️ Preview Tamu"])
    with tab1:
        uploaded = st.file_uploader("Upload Foto Baru", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if uploaded:
            if st.session_state.frame is None: st.warning("Pasang bingkai!")
            else:
                with st.spinner("Processing..."):
                    img = ImageOps.exif_transpose(Image.open(uploaded)).convert("RGBA")
                    f_res = st.session_state.frame.resize(img.size, Image.Resampling.LANCZOS)
                    final = Image.alpha_composite(img, f_res)
                    st.session_state.gallery.insert(0, final.convert("RGB"))
                    st.toast("Terkirim!")
        render_content()
    with tab2: render_content()
else:
    render_content()
