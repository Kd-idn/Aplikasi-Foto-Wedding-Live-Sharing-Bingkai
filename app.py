import streamlit as st
from PIL import Image, ImageOps
import io

st.set_page_config(page_title="Wedding Gallery", layout="wide", initial_sidebar_state="collapsed")

if 'gallery' not in st.session_state:
    st.session_state.gallery = []
if 'frame' not in st.session_state:
    st.session_state.frame = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- AREA PUBLIK ---
st.title("✨ Wedding Live Gallery")

st.write("### 📤 Upload Foto Kamera")
uploaded_photo = st.file_uploader("Upload foto", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_photo:
    if st.session_state.frame is None:
        st.error("⚠️ Admin belum upload bingkai di sidebar!")
    else:
        with st.spinner("Menyesuaikan bingkai ke foto asli..."):
            # 1. Buka foto asli & perbaiki rotasi EXIF
            user_img = ImageOps.exif_transpose(Image.open(uploaded_photo)).convert("RGBA")
            frame_img = st.session_state.frame
            
            # 2. RESIZE BINGKAI mengikuti lebar/tinggi foto asli
            # Ini kuncinya agar tidak ada area hitam/kosong
            frame_resized = frame_img.resize(user_img.size, Image.Resampling.LANCZOS)
            
            # 3. GABUNGKAN (Foto sebagai dasar, bingkai di atasnya)
            final_composite = Image.alpha_composite(user_img, frame_resized)
            
            # 4. SIMPAN (Ke Galeri)
            st.session_state.gallery.insert(0, final_composite.convert("RGB"))
            st.toast("Foto berhasil diproses!", icon="📸")

# --- AREA ADMIN (SIDEBAR) ---
st.sidebar.title("🔐 Kendali Admin")
if not st.session_state.logged_in:
    user = st.sidebar.text_input("Username")
    pwd = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Masuk"):
        if user == "admin" and pwd == "wedding123":
            st.session_state.logged_in = True
            st.rerun()
else:
    st.sidebar.success("Mode Admin Aktif")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.sidebar.divider()
    if st.session_state.frame is not None:
        st.sidebar.image(st.session_state.frame, caption="Bingkai Aktif", use_container_width=True)
        if st.sidebar.button("🗑️ Ganti Bingkai"):
            st.session_state.frame = None
            st.rerun()
    else:
        new_frame = st.sidebar.file_uploader("Upload Bingkai PNG", type=["png"])
        if new_frame:
            st.session_state.frame = Image.open(new_frame).convert("RGBA")
            st.rerun()

# --- GALERI ---
st.write("---")
if st.session_state.gallery:
    cols = st.columns(3)
    for idx, photo in enumerate(st.session_state.gallery):
        with cols[idx % 3]:
            st.image(photo, use_container_width=True)
            buf = io.BytesIO()
            photo.save(buf, format="JPEG", quality=95) # High Quality
            st.download_button(label="📥 Download", data=buf.getvalue(), file_name=f"wedding_{idx}.jpg", mime="image/jpeg", key=f"dl_{idx}")
