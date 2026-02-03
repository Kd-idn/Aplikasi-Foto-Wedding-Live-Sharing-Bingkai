import streamlit as st
from PIL import Image, ImageOps
import io

st.set_page_config(page_title="Wedding Gallery", layout="wide")

# Gunakan session state agar data tidak hilang saat interaksi
if 'gallery' not in st.session_state:
    st.session_state.gallery = []
if 'frame' not in st.session_state:
    st.session_state.frame = None

st.title("📸 Live Wedding Gallery")

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.header("⚙️ Admin Panel")
    uploaded_frame = st.file_uploader("1. Upload Bingkai (PNG Transparan)", type=["png"])
    if uploaded_frame:
        st.session_state.frame = Image.open(uploaded_frame).convert("RGBA")
        st.success("Bingkai terpasang!")
        st.image(st.session_state.frame, caption="Preview Bingkai", use_container_width=True)

# --- MAIN UPLOAD ---
st.write("### 2. Upload Foto Kamera")
uploaded_photo = st.file_uploader("Pilih foto hasil jepretan", type=["jpg", "jpeg", "png"])

if uploaded_photo:
    if st.session_state.frame is None:
        st.error("Gagal: Upload bingkai dulu di Admin Panel (samping kiri)!")
    else:
        with st.spinner("Sedang memproses foto..."):
            # 1. Buka foto kamera dan bingkai
            user_img = Image.open(uploaded_photo)
            
            # Perbaiki rotasi otomatis jika foto diambil vertikal (EXIF)
            user_img = ImageOps.exif_transpose(user_img).convert("RGBA")
            
            frame_img = st.session_state.frame
            
            # 2. Resize foto kamera agar menutupi seluruh area bingkai (Fit & Crop)
            # Ini memastikan foto tidak gepeng
            user_img_resized = ImageOps.fit(user_img, frame_img.size, method=Image.Resampling.LANCZOS)
            
            # 3. Gabungkan secara fisik (Alpha Composite)
            # Foto di bawah, Bingkai di atas
            final_image = Image.alpha_composite(user_img_resized, frame_img)
            
            # 4. Simpan ke daftar galeri (Konversi ke RGB untuk hemat memori)
            st.session_state.gallery.insert(0, final_image.convert("RGB"))
            st.success("Foto berhasil diproses!")

# --- TAMPILAN GALERI ---
st.write("---")
st.write("### 🖼️ Galeri Tamu (Klik Download untuk Simpan)")

if st.session_state.gallery:
    cols = st.columns(3)
    for idx, photo in enumerate(st.session_state.gallery):
        with cols[idx % 3]:
            # Tampilkan gambar
            st.image(photo, use_container_width=True)
            
            # Siapkan tombol download
            buf = io.BytesIO()
            photo.save(buf, format="JPEG", quality=85) # Quality 85 untuk hemat storage
            st.download_button(
                label=f"📥 Download Foto {len(st.session_state.gallery) - idx}",
                data=buf.getvalue(),
                file_name=f"wedding_{idx}.jpg",
                mime="image/jpeg",
                key=f"dl_{idx}"
            )
