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
    st.session_state.wedding_name = "Pengantin Pria & Wanita"
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
    st.sidebar.divider()
    st.sidebar.subheader("✍️ Branding Acara")
    st.session_state.wedding_name = st.sidebar.text_input("Nama Pengantin", st.session_state.wedding_name)
    st.session_state.vendor_name = st.sidebar.text_input("Nama Vendor", st.session_state.vendor_name)
    
    new_logo = st.sidebar.file_uploader("Upload Logo Vendor (PNG)", type=["png"])
    if new_logo:
        st.session_state.vendor_logo = Image.open(new_logo).convert("RGBA")
    
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
                st.download_button(label="📥 Simpan Foto", data=buf.getvalue(), file_name=f"wedding_{idx}.jpg", key=f"dl_{idx}_{'pre' if is_preview else 'pub'}", use_container_width=True)
    else:
        st.info("Galeri belum berisi foto.")

# --- HEADER & TOMBOL WA POJOK KANAN ATAS ---
text_share = urllib.parse.quote(f"Lihat koleksi foto momen indah {st.session_state.wedding_name} di: {APP_URL}")
wa_link = f"https://wa.me/?text={text_share}"

# Struktur Kolom Header
h_col1, h_col2, h_col3 = st.columns([1, 4, 1])

with h_col3: # Pojok Kanan Atas
    st.markdown(f"""
        <div style="text-align: right; padding-top: 10px;">
            <a href="{wa_link}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #25D366; color: white; padding: 8px 15px; border-radius: 50px; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0px 2px 5px rgba(0,0,0,0.1);">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="18px">
                    <span style="font-weight: bold; font-size: 13px;">Bagikan</span>
                </div>
            </a>
        </div>
    """, unsafe_allow_html=True)

with h_col2: # Tengah (Simetris)
    st.markdown(f"""
        <div style="text-align: center;">
            <h1 style="color: #1E1E1E; margin-bottom: 0;">✨ Wedding Gallery of {st.session_state.wedding_name}</h1>
            <p style="color: #666; font-style: italic; margin-top: 5px;">Powered by {st.session_state.vendor_name}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.vendor_logo:
        # Menampilkan logo tepat di tengah bawah nama vendor
        col_logo1, col_logo2, col_logo3 = st.columns([1, 0.4, 1])
        with col_logo2:
            st.image(st.session_state.vendor_logo, use_container_width=True)

# --- LOGIKA DASHBOARD ---
st.divider()
if st.session_state.logged_in:
    tab1, tab2 = st.tabs(["📤 Panel Fotografer", "👁️ Preview Tampilan Tamu"])
    with tab1:
        st.write("### Kirim Hasil Foto")
        uploaded_photo = st.file_uploader("Upload", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if uploaded_photo:
            if st.session_state.frame is None: st.warning("Pasang bingkai di sidebar!")
            else:
                with st.spinner("Menggabungkan foto..."):
                    user_img = ImageOps.exif_transpose(Image.open(uploaded_photo)).convert("RGBA")
                    frame_resized = st.session_state.frame.resize(user_img.size, Image.Resampling.LANCZOS)
                    final = Image.alpha_composite(user_img, frame_resized)
                    st.session_state.gallery.insert(0, final.convert("RGB"))
                    st.toast("Foto terkirim ke galeri!", icon="✅")
        render_gallery(is_preview=True)
    with tab2:
        render_gallery()
else:
    render_gallery()
