import streamlit as st
from PIL import Image
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
        with st.spinner("Memasang bingkai..."):
            # 1. Buka foto kamera dan bingkai
            user_img = Image.open(uploaded_photo).convert("RGBA")
            frame_img = st.session_state.frame
            
            # 2. Resize foto kamera agar SAMA PERSIS dengan ukuran bingkai
            user_img_resized = user_img.resize(frame_img.size, Image.Resampling.LANCZOS)
            
            # 3. Gabungkan: Foto di bawah, Bingkai di atas
            # Kita buat kanvas kosong seukuran bingkai
            combined = Image.new("RGBA", frame_img.size)
            combined.paste(user_img_resized, (0, 0))
            combined.paste(frame_img, (0, 0), mask=frame_img)
            
            # 4. Simpan ke daftar galeri (paling atas adalah yang terbaru)
            st.session_state.gallery.insert(0, combined.convert("RGB"))
            st.success("Foto berhasil masuk galeri!")

# --- TAMPILAN GALERI ---
st.write("---")
st.write("### 🖼️ Galeri Tamu (Scan QR untuk Download)")

if st.session_state.gallery:
    # Buat grid 3 kolom
    cols = st.columns(3)
    for idx, photo in enumerate(st.session_state.gallery):
        with cols[idx % 3]:
            st.image(photo, use_container_width=True)
            # Tombol Download
            buf = io.BytesIO()
            photo.save(buf, format="JPEG")
            st.download_button(
                label=f"📥 Download Foto {len(st.session_state.gallery) - idx}",
                data=buf.getvalue(),
                file_name=f"wedding_photo_{idx}.jpg",
                mime="image/jpeg",
                key=f"btn_{idx}"
            )
else:
    st.info("Belum ada foto di galeri. Silakan upload foto pertama!")
