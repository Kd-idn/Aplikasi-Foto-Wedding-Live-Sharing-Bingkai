import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="Wedding Gallery", layout="wide")

# Inisialisasi Galeri agar tidak error saat kosong
if 'gallery' not in st.session_state:
    st.session_state.gallery = []

st.title("📸 Live Wedding Gallery")

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.header("⚙️ Admin Panel")
    uploaded_frame = st.file_uploader("1. Upload Bingkai (PNG)", type=["png"])
    if uploaded_frame:
        st.session_state.frame = Image.open(uploaded_frame).convert("RGBA")
        st.success("Bingkai terpasang!")

# --- MAIN UPLOAD ---
st.write("### 2. Upload Foto Kamera")
uploaded_photo = st.file_uploader("Pilih foto hasil jepretan", type=["jpg", "jpeg", "png"])

if uploaded_photo and 'frame' in st.session_state:
    img = Image.open(uploaded_photo).convert("RGBA")
    # Auto-resize ke ukuran bingkai
    img = img.resize(st.session_state.frame.size)
    # Gabungkan
    final = Image.alpha_composite(img, st.session_state.frame)
    
    # Simpan ke memori galeri
    st.session_state.gallery.append(final)
    st.success("Foto berhasil masuk galeri!")

# --- TAMPILAN GALERI ---
st.write("---")
st.write("### 🖼️ Galeri Tamu")
if st.session_state.gallery:
    cols = st.columns(3)
    for idx, photo in enumerate(reversed(st.session_state.gallery)):
        with cols[idx % 3]:
            st.image(photo, use_container_width=True)
            # Tombol Download
            buf = io.BytesIO()
            photo.convert("RGB").save(buf, format="JPEG")
            st.download_button("Download", buf.getvalue(), f"foto_{idx}.jpg", "image/jpeg", key=f"dl_{idx}")
