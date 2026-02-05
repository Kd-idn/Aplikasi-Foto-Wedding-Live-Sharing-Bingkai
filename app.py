import streamlit as st
from PIL import Image, ImageOps
import io

st.set_page_config(page_title="Wedding Gallery", layout="wide")

# 1. Inisialisasi Data
if 'gallery' not in st.session_state:
    st.session_state.gallery = []
if 'frame' not in st.session_state:
    st.session_state.frame = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- FUNGSI LOGIN (Sederhana & Rapi) ---
def check_login():
    st.sidebar.title("🔐 Admin Login")
    user = st.sidebar.text_input("Username", key="user_input")
    pwd = st.sidebar.text_input("Password", type="password", key="pwd_input")
    
    if st.sidebar.button("Login"):
        # Ganti dengan username & password pilihan Anda
        if user == "admin" and pwd == "wedding123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.sidebar.error("Username atau Password salah!")

# --- LOGIKA TAMPILAN ---
if not st.session_state.logged_in:
    # 1. TAMPILAN TAMU (Hanya Galeri)
    st.title("✨ Wedding Live Gallery")
    st.write("Selamat datang! Silakan unduh foto kenangan Anda di bawah ini.")
    
    # Form login tetap ada di sidebar tapi tidak mengganggu
    st.divider()
    check_login()
else:
    # 2. TAMPILAN ADMIN (Panel Kontrol Muncul)
    st.sidebar.title("🛠️ Admin Panel")
    if st.sidebar.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.title("📸 Dashboard Admin")
    
    # Upload Bingkai di Sidebar
    st.sidebar.subheader("Pengaturan Bingkai")
    uploaded_frame = st.sidebar.file_uploader("Upload Bingkai (PNG Transparan)", type=["png"])
    if uploaded_frame:
        st.session_state.frame = Image.open(uploaded_frame).convert("RGBA")
        st.sidebar.success("Bingkai berhasil dipasang!")

    # Upload Foto Manual
    st.write("### 📤 Upload Foto Hasil Jepretan")
    uploaded_photo = st.file_uploader("Pilih foto dari folder laptop", type=["jpg", "jpeg", "png"])
    
    if uploaded_photo:
        if st.session_state.frame is None:
            st.warning("Silakan upload bingkai terlebih dahulu di sidebar kiri!")
        else:
            with st.spinner("Memasang bingkai secara otomatis..."):
                user_img = ImageOps.exif_transpose(Image.open(uploaded_photo)).convert("RGBA")
                frame_img = st.session_state.frame
                user_img_resized = ImageOps.fit(user_img, frame_img.size, method=Image.Resampling.LANCZOS)
                final_image = Image.alpha_composite(user_img_resized, frame_img)
                st.session_state.gallery.insert(0, final_image.convert("RGB"))
                st.success("Foto berhasil masuk galeri tamu!")

# --- GALERI (Muncul untuk Tamu & Admin) ---
st.write("---")
if st.session_state.gallery:
    st.subheader("🖼️ Galeri Foto")
    cols = st.columns(3)
    for idx, photo in enumerate(st.session_state.gallery):
        with cols[idx % 3]:
            st.image(photo, use_container_width=True)
            buf = io.BytesIO()
            photo.save(buf, format="JPEG", quality=90)
            st.download_button(
                label="📥 Download",
                data=buf.getvalue(),
                file_name=f"wedding_photo_{idx}.jpg",
                mime="image/jpeg",
                key=f"dl_{idx}"
            )
else:
    st.info("Galeri kosong. Foto akan segera muncul setelah fotografer beraksi!")
