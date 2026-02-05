import streamlit as st
from PIL import Image, ImageOps
import io

st.set_page_config(page_title="Wedding Gallery", layout="wide")

# 1. Inisialisasi Database Sementara
if 'gallery' not in st.session_state:
    st.session_state.gallery = []
if 'frame' not in st.session_state:
    st.session_state.frame = None
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False

# --- FUNGSI LOGIN ---
def login():
    st.sidebar.title("🔐 Admin Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        # Silakan ganti username & password sesuai keinginan Anda
        if username == "admin" and password == "wedding123":
            st.session_state.is_logged_in = True
            st.rerun()
        else:
            st.sidebar.error("Username/Password Salah")

def logout():
    st.session_state.is_logged_in = False
    st.rerun()

# --- LOGIKA TAMPILAN ---
if not st.session_state.is_logged_in:
    # TAMPILAN TAMU
    st.title("✨ Wedding Live Gallery")
    st.write("Selamat datang! Silakan lihat dan download foto kenangan Anda di bawah ini.")
    
    # Tombol kecil di pojok bawah untuk admin masuk
    if st.sidebar.button("Admin Area"):
        login()
else:
    # TAMPILAN ADMIN
    st.sidebar.title("🛠️ Admin Panel")
    if st.sidebar.button("Logout"):
        logout()
    
    st.title("📸 Dashboard Admin")
    
    # Input Bingkai di Sidebar
    uploaded_frame = st.sidebar.file_uploader("Upload Bingkai Baru (PNG)", type=["png"])
    if uploaded_frame:
        st.session_state.frame = Image.open(uploaded_frame).convert("RGBA")
        st.sidebar.success("Bingkai diperbarui!")

    # Upload Foto dari Kamera
    st.write("### Upload Hasil Jepretan")
    uploaded_photo = st.file_uploader("Pilih foto kamera", type=["jpg", "jpeg", "png"])
    
    if uploaded_photo:
        if st.session_state.frame is None:
            st.error("Upload bingkai dulu di sidebar!")
        else:
            with st.spinner("Memproses foto..."):
                user_img = ImageOps.exif_transpose(Image.open(uploaded_photo)).convert("RGBA")
                frame_img = st.session_state.frame
                user_img_resized = ImageOps.fit(user_img, frame_img.size, method=Image.Resampling.LANCZOS)
                final_image = Image.alpha_composite(user_img_resized, frame_img)
                st.session_state.gallery.insert(0, final_image.convert("RGB"))
                st.success("Foto berhasil masuk galeri!")

# --- DISPLAY GALERI (Muncul untuk semua) ---
st.write("---")
if st.session_state.gallery:
    cols = st.columns(3)
    for idx, photo in enumerate(st.session_state.gallery):
        with cols[idx % 3]:
            st.image(photo, use_container_width=True)
            buf = io.BytesIO()
            photo.save(buf, format="JPEG", quality=90)
            st.download_button(
                label="📥 Download",
                data=buf.getvalue(),
                file_name=f"wedding_{idx}.jpg",
                mime="image/jpeg",
                key=f"dl_{idx}"
            )
else:
    st.info("Galeri kosong. Foto akan segera muncul setelah fotografer beraksi!")
