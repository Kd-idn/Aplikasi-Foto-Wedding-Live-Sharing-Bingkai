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
            st.sidebar.error("Username atau Password salah!")

# --- LOGIKA TAMPILAN ---
if not st.session_state.logged_in:
    st.title("✨ Wedding Live Gallery")
    st.write("Selamat datang! Silakan unduh foto kenangan Anda di bawah ini.")
    check_login()
else:
    # 2. DASHBOARD ADMIN
    st.sidebar.title("🛠️ Admin Panel")
    if st.sidebar.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.title("📸 Dashboard Admin")

    # --- BAGIAN PENGATURAN BINGKAI (SMART HIDE) ---
    with st.sidebar.expander("🖼️ Pengaturan Bingkai", expanded=(st.session_state.frame is None)):
        if st.session_state.frame is not None:
            st.image(st.session_state.frame, caption="Bingkai Aktif", use_container_width=True)
            if st.button("🗑️ Hapus / Ganti Bingkai"):
                st.session_state.frame = None
                st.rerun()
        else:
            uploaded_frame = st.file_uploader("Upload Bingkai Baru (PNG)", type=["png"])
            if uploaded_frame:
                st.session_state.frame = Image.open(uploaded_frame).convert("RGBA")
                st.success("Bingkai Berhasil Disimpan!")
                st.rerun()

    # --- BAGIAN UPLOAD FOTO ---
    st.write("### 📤 Upload Foto Hasil Jepretan")
    if st.session_state.frame is None:
        st.warning("⚠️ Silakan upload bingkai terlebih dahulu di sidebar!")
    else:
        uploaded_photo = st.file_uploader("Pilih foto dari folder laptop", type=["jpg", "jpeg", "png"])
        if uploaded_photo:
            with st.spinner("Memproses..."):
                user_img = ImageOps.exif_transpose(Image.open(uploaded_photo)).convert("RGBA")
                frame_img = st.session_state.frame
                user_img_resized = ImageOps.fit(user_img, frame_img.size, method=Image.Resampling.LANCZOS)
                final_image = Image.alpha_composite(user_img_resized, frame_img)
                st.session_state.gallery.insert(0, final_image.convert("RGB"))
                st.success("Foto berhasil masuk galeri tamu!")

# --- GALERI (Tamu & Admin) ---
st.write("---")
if st.session_state.gallery:
    cols = st.columns(3)
    for idx, photo in enumerate(st.session_state.gallery):
        with cols[idx % 3]:
            st.image(photo, use_container_width=True)
            buf = io.BytesIO()
            photo.save(buf, format="JPEG", quality=90)
            st.download_button(label="📥 Download", data=buf.getvalue(), file_name=f"wedding_{idx}.jpg", mime="image/jpeg", key=f"dl_{idx}")
