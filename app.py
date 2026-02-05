import streamlit as st
from PIL import Image, ImageOps
import io
import urllib.parse

st.set_page_config(page_title="Wedding Gallery", layout="wide", initial_sidebar_state="collapsed")

# 1. Inisialisasi Data
if 'gallery' not in st.session_state:
    st.session_state.gallery = []
if 'frame' not in st.session_state:
    st.session_state.frame = None
if 'vendor_logo' not in st.session_state:
    st.session_state.vendor_logo = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'wedding_name' not in st.session_state:
    st.session_state.wedding_name = "Si A & Si B"
if 'vendor_name' not in st.session_state:
    st.session_state.vendor_name = "Nama Vendor Anda"

APP_URL = "https://aplikasi-foto-wedding-live-sharing-bingkai-ko2zzkcx2nhyww9o2dv.streamlit.app/"

# --- SIDEBAR ADMIN ---
st.sidebar.title("🔐 Kendali Admin")
if not st.session_state.logged_in:
    user = st.sidebar.text_input("Username")
    pwd = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if user == "admin" and pwd == "wedding123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.sidebar.error("Akses Ditolak")
else:
    st.sidebar.success("Mode Admin: AKTIF")
    
    # BRANDING SETTINGS
    st.sidebar.divider()
    st.sidebar.subheader("✍️ Branding Acara")
    st.session_state.wedding_name = st.sidebar.text_input("Nama Pengantin", st.session_state.wedding_name)
    st.session_state.vendor_name = st.sidebar.text_input("Nama Vendor (Teks)", st.session_state.vendor_name)
    
    # UPLOAD LOGO VENDOR
    new_logo = st.sidebar.file_uploader("Upload Logo Vendor (PNG)", type=["png"])
    if new_logo:
        st.session_state.vendor_logo = Image.open(new_logo).convert("RGBA")
    if st.session_state.vendor_logo and st.sidebar.button("🗑️ Hapus Logo"):
        st.session_state.vendor_logo = None
        st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    # BINGKAI SETTINGS
    st.sidebar.divider()
    st.sidebar.subheader("🖼️ Pengaturan Bingkai")
    if st.session_state.frame is not None:
        st.sidebar.image(st.session_state.frame, use_container_width=True)
        if st.sidebar.button("🗑️ Ganti Bingkai"):
            st.session_state.frame = None
            st.rerun()
    else:
        new_frame = st.sidebar.file_uploader("Upload Bingkai PNG", type=["png"])
        if new_frame:
            st.session_state.frame = Image.open(new_frame).convert("RGBA")
            st.rerun()

# --- FUNGSI RENDER GALERI (BERSIH) ---
def render_gallery(is_preview=False):
    if st.session_state.gallery:
        cols = st.columns(3)
        for idx, photo in enumerate(st.session_state.gallery):
            with cols[idx % 3]:
                st.image(photo, use_container_width=True)
                # Hanya tombol Download yang tersisa di sini
                buf = io.BytesIO()
                photo.save(buf, format="JPEG", quality=95)
                st.download_button(label="📥 Download", data=buf.getvalue(), file_name=f"wedding_{idx}.jpg", key=f"dl_{idx}_{'pre' if is_preview else 'pub'}")
    else:
        st.info("Galeri masih kosong.")

# --- TAMPILAN HEADER & TOMBOL SHARE POJOK ATAS ---
text_share = urllib.parse.quote(f"Lihat koleksi foto Wedding {st.session_state.wedding_name} di: {APP_URL}")
wa_link = f"https://wa.me/?text={text_share}"

# Layout Header: Judul di tengah, Share di kanan
h_col1, h_col2 = st.columns([0.8, 0.2])

with h_col1:
    st.markdown(f"<h1 style='margin-bottom:0;'>✨ Wedding Gallery of {st.session_state.wedding_name}</h1>", unsafe_allow_html=True)
    # Tampilkan Logo Vendor jika ada
    if st.session_state.vendor_logo:
        st.image(st.session_state.vendor_logo, width=150)
    st.markdown(f"<p style='color: gray; font-style: italic; margin-top:-10px;'>Powered by {st.session_state.vendor_name}</p>", unsafe_allow_html=True)

with h_col2:
    st.markdown(f"""
        <div style="text-align: right; margin-top: 20px;">
            <a href="{wa_link}" target="_blank">
                <button style="background-color: #25D366; color: white; border: none; padding: 10px 15px; border-radius: 8px; cursor: pointer; font-weight: bold;">
                    🟢 Bagikan Galeri
                </button>
            </a>
        </div>
    """, unsafe_allow_html=True)

# --- LOGIKA HALAMAN ---
st.divider()
if st.session_state.logged_in:
    tab1, tab2 = st.tabs(["📤 Upload Foto", "👁️ Preview Tamu"])
    with tab1:
        uploaded_photo = st.file_uploader("Pilih foto", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if uploaded_photo:
            if st.session_state.frame is None: st.warning("Upload bingkai dulu!")
            else:
                with st.spinner("Processing..."):
                    user_img = ImageOps.exif_transpose(Image.open(uploaded_photo)).convert("RGBA")
                    frame_resized = st.session_state.frame.resize(user_img.size, Image.Resampling.LANCZOS)
                    final = Image.alpha_composite(user_img, frame_resized)
                    st.session_state.gallery.insert(0, final.convert("RGB"))
                    st.success("Terkirim!")
        render_gallery(is_preview=True)
    with tab2:
        render_gallery()
else:
    st.write(f"Selamat datang! Nikmati momen indah {st.session_state.wedding_name}.")
    render_gallery()
