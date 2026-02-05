import streamlit as st
from PIL import Image, ImageOps
import io
import urllib.parse
from datetime import datetime
import time

# 1. Konfigurasi Dasar
st.set_page_config(page_title="Wedding Gallery Live", layout="wide", initial_sidebar_state="collapsed")

# 2. Inisialisasi Session State yang Kokoh
if 'gallery' not in st.session_state: st.session_state.gallery = []
if 'frame' not in st.session_state: st.session_state.frame = None
if 'vendor_logo' not in st.session_state: st.session_state.vendor_logo = None
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wedding_name' not in st.session_state: st.session_state.wedding_name = "Si A & Si B"
if 'vendor_name' not in st.session_state: st.session_state.vendor_name = "Nama Vendor Anda"
if 'last_processed_file' not in st.session_state: st.session_state.last_processed_file = None

def reset_all_data():
    st.session_state.gallery = []
    st.session_state.frame = None
    st.session_state.vendor_logo = None
    st.session_state.last_processed_file = None
    st.rerun()

# --- CSS ADAPTIF (Mencegah Teks Gelap di HP) ---
st.markdown("""
    <style>
    .stApp h1, .stApp p, .stApp label, .stApp div { color: var(--text-color) !important; }
    .header-text { text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: KENDALI ADMIN (Dipastikan Tombol Muncul) ---
with st.sidebar:
    st.title("🔐 Kendali Admin")
    if not st.session_state.logged_in:
        u = st.text_input("Username", key="login_username")
        p = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="btn_login_submit"):
            if u == "admin" and p == "wedding123":
                st.session_state.logged_in = True; st.rerun()
    else:
        # Branding Acara
        st.session_state.wedding_name = st.text_input("Nama Pengantin", st.session_state.wedding_name, key="input_pengantin")
        st.session_state.vendor_name = st.text_input("Nama Vendor", st.session_state.vendor_name, key="input_vendor")
        
        st.divider()
        # Pengaturan Media
        l_up = st.file_uploader("Upload Logo Vendor", type=["png"], key="up_logo_sidebar")
        if l_up: st.session_state.vendor_logo = Image.open(l_up).convert("RGBA")
        
        f_up = st.file_uploader("Upload Bingkai Story", type=["png"], key="up_frame_sidebar")
        if f_up: st.session_state.frame = Image.open(f_up).convert("RGBA")
        
        if st.session_state.frame:
            st.image(st.session_state.frame, caption="Bingkai Aktif", width=80)
            if st.button("🗑️ Hapus Bingkai", key="btn_del_frame"): st.session_state.frame = None; st.rerun()
        
        st.divider()
        # Tombol Reset & Logout
        if st.button("🚨 RESET TOTAL", type="primary", use_container_width=True, key="main_reset_btn"):
            reset_all_data()
        if st.button("Logout", use_container_width=True, key="main_logout_btn"):
            st.session_state.logged_in = False; st.rerun()

# --- HEADER ---
st.markdown(f'<h1 class="header-text">✨ Wedding Gallery of {st.session_state.wedding_name}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="header-text" style="font-style:italic; opacity:0.8; margin-top:-10px;">Powered by {st.session_state.vendor_name}</p>', unsafe_allow_html=True)

if st.session_state.vendor_logo:
    _, mid, _ = st.columns([1, 0.3, 1])
    mid.image(st.session_state.vendor_logo, use_container_width=True)

st.divider()

# --- FUNGSI RENDER GALERI (Memperbaiki KeyError & Duplicate Key) ---
def render_gallery_content(suffix):
    if not st.session_state.gallery:
        st.info("Galeri belum berisi foto.")
        return

    # Pastikan data berupa dictionary dan urutkan
    valid_data = [i for i in st.session_state.gallery if isinstance(i, dict)]
    valid_data.sort(key=lambda x: x.get('time', datetime.min), reverse=True)

    cols = st.columns(3)
    for idx, item in enumerate(valid_data):
        with cols[idx % 3]:
            st.image(item['image'], use_container_width=True)
            t_str = item['time'].strftime('%H:%M')
            st.caption(f"⏰ {t_str}")
            
            # Tombol Simpan dengan Key unik berbasis timestamp
            # Memastikan 'image_bytes' ada untuk menghindari KeyError
            if 'image_bytes' in item:
                st.download_button(
                    label="📥 Simpan",
                    data=item['image_bytes'],
                    file_name=f"wedding_{idx}.jpg",
                    key=f"dl_btn_{suffix}_{idx}_{item['time'].timestamp()}",
                    use_container_width=True
                )

# --- DASHBOARD UTAMA (Anti-Double Upload) ---
if st.session_state.logged_in:
    t1, t2 = st.tabs(["📤 Panel Fotografer", "👁️ Preview Tampilan Tamu"])
    with t1:
        st.subheader("Kirim Hasil Foto")
        uploaded = st.file_uploader("Drag and drop file here", type=["jpg", "png", "jpeg"], key="main_uploader")
        
        # Logika Mencegah File Double
        if uploaded and uploaded.name != st.session_state.last_processed_file:
            if st.session_state.frame is None:
                st.warning("Silakan upload bingkai potret terlebih dahulu di sidebar!")
            else:
                with st.spinner("Menyesuaikan ke format Story IG..."):
                    img = ImageOps.exif_transpose(Image.open(uploaded)).convert("RGBA")
                    fw, fh = st.session_state.frame.size
                    
                    # Smart Center-Crop (Lanskap ke Story Potret)
                    img_ratio, frame_ratio = img.width / img.height, fw / fh
                    if img_ratio > frame_ratio:
                        new_w = int(frame_ratio * img.height)
                        left = (img.width - new_w) / 2
                        img = img.crop((left, 0, left + new_w, img.height))
                    else:
                        new_h = int(img.width / frame_ratio)
                        top = (img.height - new_h) / 2
                        img = img.crop((0, top, img.width, top + new_h))
                    
                    # Gabungkan Foto dan Bingkai
                    final_img = Image.alpha_composite(img.resize((fw, fh)), st.session_state.frame).convert("RGB")
                    
                    # Konversi ke bytes untuk download stabil
                    img_byte_arr = io.BytesIO()
                    final_img.save(img_byte_arr, format='JPEG')
                    
                    # Simpan ke state
                    st.session_state.gallery.append({
                        "image": final_img,
                        "image_bytes": img_byte_arr.getvalue(),
                        "time": datetime.now()
                    })
                    st.session_state.last_processed_file = uploaded.name
                    st.toast("Foto Terkirim!", icon="📸")
                    time.sleep(1) # Jeda singkat untuk kestabilan state
                    st.rerun()

        render_gallery_content("admin")
    with t2:
        render_gallery_content("preview")
else:
    render_gallery_content("guest")
