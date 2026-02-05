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
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
# Inisialisasi Nama Pengantin & Vendor
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
            st.sidebar.error("Salah!")
else:
    st.sidebar.success("Mode Admin: AKTIF")
    
    # INPUT BRANDING (Hanya Muncul di Admin)
    st.sidebar.divider()
    st.sidebar.subheader("✍️ Branding Acara")
    st.session_state.wedding_name = st.sidebar.text_input("Nama Pengantin", st.session_state.wedding_name)
    st.session_state.vendor_name = st.sidebar.text_input("Nama Vendor", st.session_state.vendor_name)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
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

# --- FUNGSI RENDER GALERI ---
def render_gallery(is_preview=False):
    if st.session_state.gallery:
        cols = st.columns(3)
        for idx, photo in enumerate(st.session_state.gallery):
            with cols[idx % 3]:
                st.image(photo, use_container_width=True)
                buf = io.BytesIO()
                photo.save(buf, format="JPEG", quality=95)
                st.download_button(label="📥 Download", data=buf.getvalue(), file_name=f"wedding_{idx}.jpg", key=f"dl_{idx}_{'pre' if is_preview else 'pub'}")
                
                text_share = urllib.parse.quote(f"Lihat foto {st.session_state.wedding_name} di: {APP_URL}")
                st.markdown(f'''
                    <div style="display: flex; gap: 5px; margin-top: -10px; margin-bottom: 20px;">
                        <a href="https://wa.me/?text={text_share}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; font-size: 11px;">WA</button></a>
                        <button onclick="navigator.clipboard.writeText('{APP_URL}')" style="background-color: #f0f2f6; border: 1px solid #ccc; padding: 5px 10px; border-radius: 5px; cursor: pointer; font-size: 11px;">Salin Link</button>
                    </div>
                ''', unsafe_allow_html=True)
    else:
        st.info("Galeri masih kosong.")

# --- TAMPILAN HEADER (DINAMIS) ---
st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="margin-bottom: 0;">✨ Wedding Gallery of {st.session_state.wedding_name}</h1>
        <p style="color: gray; font-style: italic;">Powered by {st.session_state.vendor_name}</p>
    </div>
""", unsafe_allow_html=True)

# --- LOGIKA HALAMAN ---
if st.session_state.logged_in:
    tab1, tab2 = st.tabs(["📤 Upload Foto", "👁️ Preview Tampilan Tamu"])
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
        st.divider()
        render_gallery(is_preview=True)
    with tab2:
        render_gallery()
else:
    st.write(f"Selamat datang di momen spesial {st.session_state.wedding_name}! Silakan simpan kenangan Anda.")
    st.divider()
    render_gallery()
