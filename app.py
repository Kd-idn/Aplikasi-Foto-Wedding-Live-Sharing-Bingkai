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

def reset_data():
    st.session_state.gallery = []
    st.session_state.frame = None
    st.session_state.vendor_logo = None
    st.rerun()

# --- CSS ADAPTIF (Solusi Teks Gelap di Mobile) ---
st.markdown("""
    <style>
    .stApp h1, .stApp p, .stApp label, .stApp div { color: var(--text-color) !important; }
    .header-text { text-align: center; }
    .wa-float {
        position: fixed; top: 20px; right: 20px; background-color: #25D366;
        color: white !important; padding: 8px 15px; border-radius: 50px;
        z-index: 1000; text-decoration: none; font-weight: bold; font-size: 12px;
        display: flex; align-items: center; gap: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Tombol Share
APP_URL = "https://aplikasi-foto-wedding-live-sharing-bingkai-ko2zzkcx2nhyww9o2dv.streamlit.app/"
text_share = urllib.parse.quote(f"Lihat koleksi foto {st.session_state.wedding_name} di: {APP_URL}")
st.markdown(f'<a href="https://wa.me/?text={text_share}" class="wa-float" target="_blank">Bagikan</a>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔐 Kendali Admin")
    if not st.session_state.logged_in:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u == "admin" and p == "wedding123":
                st.session_state.logged_in = True; st.rerun()
    else:
        st.session_state.wedding_name = st.text_input("Nama Pengantin", st.session_state.wedding_name)
        st.session_state.vendor_name = st.text_input("Nama Vendor", st.session_state.vendor_name)
        
        st.divider()
        l_up = st.file_uploader("Upload Logo", type=["png"])
        if l_up: st.session_state.vendor_logo = Image.open(l_up).convert("RGBA")
        
        st.divider()
        if st.session_state.frame is not None:
            st.image(st.session_state.frame, caption="Bingkai Story Aktif")
            if st.button("🗑️ Ganti Bingkai"): st.session_state.frame = None; st.rerun()
        else:
            f_up = st.file_uploader("Upload Bingkai Potret (Story)", type=["png"])
            if f_up: st.session_state.frame = Image.open(f_up).convert("RGBA"); st.rerun()
        
        if st.button("🚨 RESET", type="primary"): reset_data()
        if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

# --- HEADER ---
st.markdown(f'<h1 class="header-text">✨ Wedding Gallery of {st.session_state.wedding_name}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="header-text" style="font-style:italic; opacity:0.8; margin-top:-10px;">Powered by {st.session_state.vendor_name}</p>', unsafe_allow_html=True)

if st.session_state.vendor_logo:
    _, mid, _ = st.columns([1, 0.3, 1])
    mid.image(st.session_state.vendor_logo, use_container_width=True)

st.divider()

# --- FUNGSI RENDER ---
def render_gallery(suffix):
    if not st.session_state.gallery:
        st.info("Galeri kosong.")
        return

    sort_f = st.selectbox("Urutan:", ["Baru", "Lama"], key=f"s_{suffix}")
    data = [i for i in st.session_state.gallery if isinstance(i, dict)]
    data.sort(key=lambda x: x.get('time', datetime.min), reverse=(sort_f == "Baru"))

    cols = st.columns(3)
    for idx, item in enumerate(data):
        with cols[idx % 3]:
            st.image(item['image'], use_container_width=True)
            t_str = item['time'].strftime('%H:%M') if 'time' in item else "--:--"
            st.caption(f"⏰ {t_str}")
            buf = io.BytesIO(); item['image'].save(buf, format="JPEG")
            st.download_button("📥", buf.getvalue(), f"img_{idx}.jpg", key=f"d_{suffix}_{idx}", use_container_width=True)

# --- PANEL UPLOAD DENGAN AUTO-CROP ---
if st.session_state.logged_in:
    t1, t2 = st.tabs(["📤 Upload", "👁️ Preview"])
    with t1:
        uploaded = st.file_uploader("Upload Foto Kamera (Lanskap)", type=["jpg", "png"])
        if uploaded:
            if st.session_state.frame is None:
                st.warning("Upload bingkai potret dulu di sidebar!")
            else:
                img = ImageOps.exif_transpose(Image.open(uploaded)).convert("RGBA")
                fw, fh = st.session_state.frame.size
                
                # LOGIKA CENTER CROP: Lanskap -> Potret
                img_ratio = img.width / img.height
                frame_ratio = fw / fh
                
                if img_ratio > frame_ratio:
                    new_width = int(frame_ratio * img.height)
                    left = (img.width - new_width) / 2
                    img = img.crop((left, 0, left + new_width, img.height))
                else:
                    new_height = int(img.width / frame_ratio)
                    top = (img.height - new_height) / 2
                    img = img.crop((0, top, img.width, top + new_height))
                
                img_res = img.resize((fw, fh), Image.Resampling.LANCZOS)
                final = Image.alpha_composite(img_res, st.session_state.frame).convert("RGB")
                
                st.session_state.gallery.append({"image": final, "time": datetime.now()})
                st.toast("Berhasil di-crop ke format Story!")
        render_gallery("adm")
    with t2: render_gallery("pre")
else:
    render_gallery("gst")
