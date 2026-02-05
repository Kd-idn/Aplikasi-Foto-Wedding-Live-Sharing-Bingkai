import streamlit as st
from PIL import Image, ImageOps
import io
import urllib.parse
from datetime import datetime

# 1. Konfigurasi Dasar
st.set_page_config(page_title="Wedding Gallery Live", layout="wide", initial_sidebar_state="collapsed")

# 2. Inisialisasi Session State
if 'gallery' not in st.session_state: st.session_state.gallery = []
if 'frame' not in st.session_state: st.session_state.frame = None
if 'vendor_logo' not in st.session_state: st.session_state.vendor_logo = None
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wedding_name' not in st.session_state: st.session_state.wedding_name = "Pengantin Pria & Wanita"
if 'vendor_name' not in st.session_state: st.session_state.vendor_name = "Nama Vendor Anda"
if 'last_processed' not in st.session_state: st.session_state.last_processed = None

def reset_data():
    st.session_state.gallery = []
    st.session_state.frame = None
    st.session_state.vendor_logo = None
    st.session_state.last_processed = None
    st.rerun()

# --- CSS ADAPTIF ---
st.markdown("""
    <style>
    .stApp h1, .stApp p, .stApp label { color: var(--text-color) !important; }
    .header-text { text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ADMIN (Memastikan Tombol Muncul Kembali) ---
with st.sidebar:
    st.title("🔐 Kendali Admin")
    if not st.session_state.logged_in:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Login", use_container_width=True):
            if u == "admin" and p == "wedding123":
                st.session_state.logged_in = True; st.rerun()
    else:
        # Input Branding
        st.session_state.wedding_name = st.text_input("Nama Pengantin", st.session_state.wedding_name, key="in_wed")
        st.session_state.vendor_name = st.text_input("Nama Vendor", st.session_state.vendor_name, key="in_vend")
        
        st.divider()
        # Upload Logo & Bingkai
        l_up = st.file_uploader("Upload Logo (PNG)", type=["png"], key="up_logo")
        if l_up: st.session_state.vendor_logo = Image.open(l_up).convert("RGBA")
        
        f_up = st.file_uploader("Upload Bingkai Story (PNG)", type=["png"], key="up_frame")
        if f_up: st.session_state.frame = Image.open(f_up).convert("RGBA")
        
        if st.session_state.frame:
            st.image(st.session_state.frame, caption="Bingkai Aktif", width=100)
            if st.button("🗑️ Hapus Bingkai", key="del_frame"): st.session_state.frame = None; st.rerun()
        
        st.divider()
        # Tombol Reset yang Sempat Hilang
        if st.button("🚨 RESET TOTAL", type="primary", use_container_width=True, key="btn_reset"):
            reset_data()
        if st.button("Keluar (Logout)", use_container_width=True, key="btn_logout"):
            st.session_state.logged_in = False; st.rerun()

# --- HEADER ---
st.markdown(f'<h1 class="header-text">✨ Wedding Gallery of {st.session_state.wedding_name}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="header-text" style="font-style:italic; opacity:0.8; margin-top:-10px;">Powered by {st.session_state.vendor_name}</p>', unsafe_allow_html=True)

if st.session_state.vendor_logo:
    _, mid, _ = st.columns([1, 0.3, 1])
    mid.image(st.session_state.vendor_logo, use_container_width=True)

st.divider()

# --- FUNGSI RENDER (Anti-Duplicate Key) ---
def render_gallery(suffix):
    if not st.session_state.gallery:
        st.info("Galeri belum berisi foto.")
        return

    # Data Protection
    data = [i for i in st.session_state.gallery if isinstance(i, dict)]
    data.sort(key=lambda x: x.get('time', datetime.min), reverse=True)

    cols = st.columns(3)
    for idx, item in enumerate(data):
        with cols[idx % 3]:
            st.image(item['image'], use_container_width=True)
            t_str = item['time'].strftime('%H:%M:%S')
            # Key unik menggunakan index, suffix, dan timestamp milidetik agar tidak error
            st.download_button(
                label="📥 Simpan",
                data=io.BytesIO(item['image_bytes']).getvalue(),
                file_name=f"wedding_{t_str}.jpg",
                key=f"dl_{suffix}_{idx}_{item['time'].timestamp()}",
                use_container_width=True
            )

# --- DASHBOARD UTAMA ---
if st.session_state.logged_in:
    t1, t2 = st.tabs(["📤 Panel Fotografer", "👁️ Preview Tamu"])
    with t1:
        uploaded = st.file_uploader("Upload Foto Kamera", type=["jpg", "png"], key="uploader_main")
        
        # Mencegah double upload
        if uploaded and uploaded.name != st.session_state.last_processed:
            if st.session_state.frame is None:
                st.warning("Upload bingkai dulu di sidebar!")
            else:
                with st.spinner("Mengolah foto..."):
                    img = ImageOps.exif_transpose(Image.open(uploaded)).convert("RGBA")
                    fw, fh = st.session_state.frame.size
                    
                    # Smart Center-Crop untuk Story IG
                    img_ratio, frame_ratio = img.width / img.height, fw / fh
                    if img_ratio > frame_ratio:
                        new_w = int(frame_ratio * img.height)
                        left = (img.width - new_w) / 2
                        img = img.crop((left, 0, left + new_w, img.height))
                    else:
                        new_h = int(img.width / frame_ratio)
                        top = (img.height - new_h) / 2
                        img = img.crop((0, top, img.width, top + new_h))
                    
                    final = Image.alpha_composite(img.resize((fw, fh)), st.session_state.frame).convert("RGB")
                    
                    # Simpan bytes agar download button lebih cepat
                    buf = io.BytesIO(); final.save(buf, format="JPEG")
                    
                    st.session_state.gallery.append({
                        "image": final,
                        "image_bytes": buf.getvalue(),
                        "time": datetime.now()
                    })
                    st.session_state.last_processed = uploaded.name
                    st.rerun()
        
        render_gallery("admin")
    with t2:
        render_gallery("preview")
else:
    render_gallery("guest")
