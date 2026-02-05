import streamlit as st
from PIL import Image, ImageOps
import io

# Konfigurasi: Sidebar tertutup agar tamu fokus ke galeri
st.set_page_config(page_title="Wedding Gallery", layout="wide", initial_sidebar_state="collapsed")

# 1. Inisialisasi Data (Session State)
if 'gallery' not in st.session_state:
    st.session_state.gallery = []
if 'frame' not in st.session_state:
    st.session_state.frame = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- AREA PUBLIK: UPLOAD & GALERI ---
st.title("✨ Wedding Live Gallery")

# Bagian Upload (Langsung muncul tanpa login)
st.write("### 📤 Upload Foto Kamera")
uploaded_photo = st.file_uploader("Upload foto", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_photo:
    if st.session_state.frame is None:
        st.error("⚠️ Bingkai belum dipasang! Silakan Admin login di sidebar untuk set bingkai.")
    else:
        with st.spinner("Memproses foto sesuai ukuran asli..."):
            # A. Buka foto & bingkai
            user_img = ImageOps.exif_transpose(Image.open(uploaded_photo)).convert("RGBA")
            frame_img = st.session_state.frame
            
            # B. Logika Centering (Menjaga Proporsi Asli)
            # Resize foto agar masuk ke dalam bingkai secara proporsional
            user_img.thumbnail(frame_img.size, Image.Resampling.LANCZOS)
            
            # Hitung posisi tengah (offset)
            bg_w, bg_h = frame_img.size
            img_w, img_h = user_img.size
            offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
            
            # C. Penggabungan Layer
            final_composite = Image.new("RGBA", frame_img.size, (0, 0, 0, 0))
            final_composite.paste(user_img, offset)
            final_composite.paste(frame_img, (0, 0), mask=frame_img)
            
            # D. Simpan ke galeri (paling atas adalah yang terbaru)
            st.session_state.gallery.insert(0, final_composite.convert("RGB"))
            st.toast("Berhasil masuk galeri!", icon="📸")

# --- AREA ADMIN: LOGIN & BINGKAI (SIDEBAR) ---
st.sidebar.title("🔐 Kendali Admin")
if not st.session_state.logged_in:
    # Form Login
    user = st.sidebar.text_input("Username")
    pwd = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Masuk"):
        if user == "admin" and pwd == "wedding123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.sidebar.error("Akses Ditolak")
else:
    # Menu Setelah Login
    st.sidebar.success("Mode Admin: ON")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.sidebar.divider()
    st.sidebar.subheader("Pengaturan Bingkai")
    
    if st.session_state.frame is not None:
        st.sidebar.image(st.session_state.frame, caption="Bingkai Aktif", use_container_width=True)
        if st.sidebar.button("🗑️ Ganti Bingkai"):
            st.session_state.frame = None
            st.rerun()
    else:
        new_frame = st.sidebar.file_uploader("Upload Bingkai (PNG)", type=["png"])
        if new_frame:
            st.session_state.frame = Image.open(new_frame).convert("RGBA")
            st.rerun()

# --- TAMPILAN GALERI (GRID RAPI) ---
st.write("---")
if st.session_state.gallery:
    st.subheader("🖼️ Galeri Foto")
    cols = st.columns(3) # Tampilan 3 kolom
    for idx, photo in enumerate(st.session_state.gallery):
        with cols[idx % 3]:
            st.image(photo, use_container_width=True)
            # Tombol Download
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
    st.info("Galeri masih kosong.")
