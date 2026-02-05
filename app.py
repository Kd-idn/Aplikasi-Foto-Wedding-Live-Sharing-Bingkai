import streamlit as st
from PIL import Image, ImageOps
import io

# Konfigurasi: Sidebar tertutup secara default agar galeri luas
st.set_page_config(page_title="Wedding Gallery", layout="wide", initial_sidebar_state="collapsed")

# 1. Inisialisasi Data
if 'gallery' not in st.session_state:
    st.session_state.gallery = []
if 'frame' not in st.session_state:
    st.session_state.frame = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- AREA PUBLIK (BISA DIAKSES SIAPAPUN) ---
st.title("✨ Wedding Live Gallery")

# Bagian Upload: Terbuka untuk Fotografer (Tanpa Login)
st.write("### 📤 Upload Foto Kamera")
uploaded_photo = st.file_uploader("Seret foto ke sini untuk dipasang bingkai", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_photo:
    if st.session_state.frame is None:
        st.error("⚠️ Bingkai belum di-set oleh Admin! Silakan login di sidebar untuk upload bingkai.")
    else:
        with st.spinner("Memasang bingkai..."):
            user_img = ImageOps.exif_transpose(Image.open(uploaded_photo)).convert("RGBA")
            frame_img = st.session_state.frame
            # Sesuaikan foto dengan ukuran asli bingkai agar tidak dobel/kecil
            user_img_resized = ImageOps.fit(user_img, frame_img.size, method=Image.Resampling.LANCZOS)
            final_image = Image.alpha_composite(user_img_resized, frame_img)
            st.session_state.gallery.insert(0, final_image.convert("RGB"))
            st.toast("Foto berhasil masuk galeri!", icon="✅")

# --- AREA ADMIN (DI SIDEBAR) ---
st.sidebar.title("🔐 Kendali Admin")
if not st.session_state.logged_in:
    # Form Login Sederhana
    user = st.sidebar.text_input("Username")
    pwd = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Masuk"):
        if user == "admin" and pwd == "wedding123":
            st.session_state.logged_in = True
            st.rerun()
else:
    # Jika sudah login, Admin bisa ganti bingkai
    st.sidebar.success("Mode Admin Aktif")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.sidebar.divider()
    st.sidebar.subheader("Pengaturan Bingkai")
    if st.session_state.frame is not None:
        st.sidebar.image(st.session_state.frame, caption="Bingkai saat ini", use_container_width=True)
        if st.sidebar.button("🗑️ Ganti Bingkai"):
            st.session_state.frame = None
            st.rerun()
    else:
        new_frame = st.sidebar.file_uploader("Upload Bingkai PNG", type=["png"])
        if new_frame:
            st.session_state.frame = Image.open(new_frame).convert("RGBA")
            st.rerun()

# --- TAMPILAN GALERI (GRID 3 KOLOM) ---
st.write("---")
if st.session_state.gallery:
    cols = st.columns(3)
    for idx, photo in enumerate(st.session_state.gallery):
        with cols[idx % 3]:
            st.image(photo, use_container_width=True)
            buf = io.BytesIO()
            photo.save(buf, format="JPEG", quality=90)
            st.download_button(label="📥 Simpan", data=buf.getvalue(), file_name=f"wedding_{idx}.jpg", mime="image/jpeg", key=f"dl_{idx}")

with st.spinner("Memproses sesuai ukuran asli..."):
            # 1. Buka foto & bingkai
            user_img = ImageOps.exif_transpose(Image.open(uploaded_photo)).convert("RGBA")
            frame_img = st.session_state.frame
            
            # 2. Tentukan ukuran kanvas (berdasarkan mana yang lebih besar: foto atau bingkai)
            # Ini memastikan file asli tidak menciut
            canvas_width = max(user_img.width, frame_img.width)
            canvas_height = max(user_img.height, frame_img.height)
            
            # 3. Buat kanvas transparan baru
            canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
            
            # 4. Resize bingkai agar mengikuti ukuran foto (agar bingkai tidak menutupi semua)
            # Atau sebaliknya, resize foto agar masuk ke dalam bingkai dengan tetap proporsional
            user_img.thumbnail(frame_img.size, Image.Resampling.LANCZOS)
            
            # 5. Letakkan foto di tengah bingkai
            bg_w, bg_h = frame_img.size
            img_w, img_h = user_img.size
            offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
            
            # 6. Tumpuk: Bingkai sebagai dasar, foto di tengah
            final_composite = Image.new("RGBA", frame_img.size)
            final_composite.paste(user_img, offset)
            final_composite.paste(frame_img, (0, 0), mask=frame_img)
            
            st.session_state.gallery.insert(0, final_composite.convert("RGB"))
            st.success("Foto asli berhasil digabungkan!")
