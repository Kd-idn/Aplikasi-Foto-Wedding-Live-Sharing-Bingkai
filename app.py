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
    st.session_state.wedding_name = "Pengantin Pria & Wanita"
    st.session_state.vendor_name = "Nama Vendor Anda"
    st.rerun()

# --- CSS ADAPTIF ---
st.markdown("""
    <style>
    .stApp h1, .stApp p, .stApp label { color: var(--text-color) !important; }
    .header-text { text-align: center; }
    .wa-float {
        position: fixed; top: 20px; right: 20px; background-color: #25D366;
        color: white !important; padding: 8px 15px; border-radius: 50px;
        z-index: 1000; text-decoration: none; font-weight: bold; font-size: 12px;
        display: flex; align-items: center; gap: 5px; box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Tombol Share
APP_URL = "https://aplikasi-foto-wedding-live-sharing-bingkai-ko2zzkcx2nhyww9o2dv.streamlit.app/"
text_share = urllib.parse.quote(f"Lihat foto {st.session_state.wedding_name} di: {APP_URL}")
st.markdown(f'<a href="https://wa.me/?text={text_share}" class="wa-float" target="_blank">Bagikan</a>', unsafe_allow_html=True)

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.title("🔐 Kendali Admin")
    if not st.session_state.logged_in:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u == "admin" and p == "wedding123":
                st.session_state.logged_in = True; st.rerun()
    else:
        # INPUT NAMA PENGANTIN & VENDOR
        st.session_state.wedding_name = st.text_input("Nama Pengantin", st.session_state.wedding_name)
        st.session_state.vendor_name = st.text_input("Nama Vendor", st.session_state.vendor_name)
        
        st.divider()
        l_up = st.file_uploader("Upload Logo Vendor", type=["png"])
        if l_up: st.session_state.vendor_logo = Image.open(l_up).convert("RGBA")
        
        st.divider()
        if st.session_state.frame is not None:
            st.image(st.session_state.frame, caption="Bingkai Aktif")
            if st.button("🗑️ Ganti Bingkai"): st.session_state.frame = None; st.rerun()
        else:
            f_up = st.file_uploader("Bingkai (PNG)", type=["png"])
            if f_up: st.session_state.frame = Image.open(f_up).convert("RGBA"); st.rerun()
        
        st.divider()
        if st.button("🚨 RESET TOTAL", type="primary", use_container_width=True): reset_data()
        if st.button("Logout", use_container_width=True): st.session_state.logged_in = False; st.rerun()

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
        st.info("Galeri belum berisi foto.")
        return

    c1, c2 = st.columns([3, 1])
    with c1: sort_f = st.selectbox("Urutan Waktu:", ["Paling Baru", "Paling Lama"], key=f"srt_{suffix}")
    with c2: mode = st.radio("Tampilan:", ["Grid", "List"], horizontal=True, key=f"vw_{suffix}")

    data = [i for i in st.session_state.gallery if isinstance(i, dict)]
    data.sort(key=lambda x: x.get('time', datetime.min), reverse=(sort_f == "Paling Baru"))

    if mode == "Grid":
        cols = st.columns(3)
        for idx, item in enumerate(data):
            with cols[idx % 3]:
                st.image(item['image'], use_container_width=True)
                t_str = item['time'].strftime('%H:%M') if 'time' in item else "--:--"
                st.markdown(f"<p style='font-size:0.8rem; text-align:center; opacity:0.7;'>⏰ {t_str}</p>", unsafe_allow_html=True)
                buf = io.BytesIO(); item['image'].save(buf, format="JPEG")
                st.download_button("📥 Simpan", buf.getvalue(), f"img_{idx}.jpg", key=f"d_{suffix}_{idx}", use_container_width=True)
    else:
        for idx, item in enumerate(data):
            st.image(item['image'], use_container_width=True)
            t_str = item['time'].strftime('%H:%M') if 'time' in item else "--:--"
            st.write(f"⏰ Jam Unggah: {t_str}")
            buf = io.BytesIO(); item['image'].save(buf, format="JPEG")
            st.download_button(f"📥 Simpan Foto {idx+1}", buf.getvalue(), f"img_{idx}.jpg", key=f"l_{suffix}_{idx}")
            st.divider()

# --- DASHBOARD ---
if uploaded:
            if st.session_state.frame is None: 
                st.warning("Upload bingkai dulu!")
            else:
                with st.spinner("Menyesuaikan orientasi foto..."):
                    # 1. Buka foto dan perbaiki rotasi otomatis (EXIF)
                    img = ImageOps.exif_transpose(Image.open(uploaded)).convert("RGBA")
                    
                    # 2. Ambil ukuran bingkai (Potret/Story)
                    frame = st.session_state.frame
                    fw, fh = frame.size
                    
                    # 3. Proses 'Center Crop' foto lanskap agar mengikuti rasio bingkai
                    # Menghitung rasio aspek
                    img_ratio = img.width / img.height
                    frame_ratio = fw / fh
                    
                    if img_ratio > frame_ratio:
                        # Foto terlalu lebar (Lanskap), potong bagian samping
                        new_width = int(frame_ratio * img.height)
                        left = (img.width - new_width) / 2
                        img = img.crop((left, 0, left + new_width, img.height))
                    else:
                        # Foto terlalu tinggi, potong bagian atas/bawah
                        new_height = int(img.width / frame_ratio)
                        top = (img.height - new_height) / 2
                        img = img.crop((0, top, img.width, top + new_height))
                    
                    # 4. Resize foto yang sudah di-crop agar pas persis dengan bingkai
                    img_resized = img.resize((fw, fh), Image.Resampling.LANCZOS)
                    
                    # 5. Tempelkan bingkai di atas foto
                    final = Image.alpha_composite(img_resized, frame).convert("RGB")
                    
                    # 6. Simpan ke galeri
                    st.session_state.gallery.append({
                        "image": final, 
                        "time": datetime.now()
                    })
                    st.toast("Foto otomatis disesuaikan ke format Story!", icon="📸")
