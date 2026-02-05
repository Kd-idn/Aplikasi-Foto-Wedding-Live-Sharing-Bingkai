import streamlit as st
from PIL import Image, ImageOps
import io

# Konfigurasi halaman agar sidebar bisa ditutup otomatis di HP
st.set_page_config(page_title="Wedding Gallery", layout="wide", initial_sidebar_state="collapsed")

# 1. Inisialisasi Data
if 'gallery' not in st.session_state:
    st.session_state.gallery = []
if 'frame' not in st.session_state:
    st.session_state.frame = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- FUNGSI LOGIN ---
def check_login():
    st.sidebar.title("🔐 Admin Login")
    user = st.sidebar.text_input("Username", key="user_input")
    pwd = st.sidebar.text_input("Password", type="password", key="pwd_input")
    if st.sidebar.button("Login"):
        if user == "admin" and pwd == "wedding123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.sidebar.error("Salah!")

# --- LOGIKA TAMPILAN ---
if not st.session_state.logged_in:
    st.title("✨ Wedding Live Gallery")
    st.write("Selamat datang! Silakan unduh foto Anda di bawah ini.")
    check_login()
else:
    # DASHBOARD ADMIN
    st.sidebar.title("🛠️ Admin Panel")
    if st.sidebar.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.title("📸 Dashboard Admin")

    # PENGATURAN BINGKAI
    with st.sidebar.expander("🖼️ Bingkai Aktif", expanded=(st.session_state.frame is None)):
        if st.session_state.frame is not None:
            st.image(st.session_state.frame, use_container_width=True)
            if st.button("🗑️ Ganti Bingkai"):
                st.session_state.frame = None
                st.rerun()
        else:
            uploaded_frame = st.file_uploader("Upload PNG", type=["png"])
            if uploaded_frame:
                st.session_state.frame = Image.open(uploaded_frame).convert("RGBA")
                st.rerun()

    # UPLOAD FOTO
    if st.session_state.frame:
        st.write("### 📤 Upload Foto Kamera")
        uploaded_photo = st.file_uploader("Pilih file", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if uploaded_photo:
            with st.spinner("Processing..."):
                # Buka foto & perbaiki rotasi otomatis (EXIF)
                user_img = ImageOps.exif_transpose(Image.open(uploaded_photo)).convert("RGBA")
                frame_img = st.session_state.frame
                
                # FIT: Foto dipotong otomatis agar pas dengan ukuran bingkai tanpa dobel
                user_img_resized = ImageOps.fit(user_img, frame_img.size, method=Image.Resampling.LANCZOS)
                
                # GABUNG: Tumpuk foto di bawah bingkai
                final_image = Image.alpha_composite(user_img_resized, frame_img)
                
                # Simpan ke galeri (konversi ke RGB agar file lebih ringan)
                st.session_state.gallery.insert(0, final_image.convert("RGB"))
                st.success("Foto ditambahkan!")
    else:
        st.warning("⚠️ Upload bingkai dulu di sidebar!")

# --- TAMPILAN GALERI (3 KOLOM RAPI) ---
st.write("---")
if st.session_state.gallery:
    # Menggunakan Grid agar tidak ada gambar yang dobel/tumpang tindih
    cols = st.columns(3)
    for idx, photo in enumerate(st.session_state.gallery):
        with cols[idx % 3]:
            st.image(photo, use_container_width=True)
            buf = io.BytesIO()
            photo.save(buf, format="JPEG", quality=90)
            st.download_button(
                label="📥 Download", 
                data=buf.getvalue(), 
                file_name=f"foto_{idx}.jpg", 
                mime="image/jpeg", 
                key=f"dl_{idx}"
            )
else:
    st.info("Galeri kosong.")
