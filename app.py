import streamlit as st
from PIL import Image, ImageOps
import io
import urllib.parse
from datetime import datetime

# 1. Konfigurasi Dasar
st.set_page_config(page_title="Wedding Gallery Live", layout="wide", initial_sidebar_state="collapsed")

# 2. Fungsi Reset & Inisialisasi
def reset_data():
    st.session_state.gallery = []
    st.session_state.frame = None
    st.session_state.vendor_logo = None
    st.session_state.wedding_name = "Pengantin Pria & Wanita"
    st.rerun()

if 'gallery' not in st.session_state: st.session_state.gallery = []
if 'frame' not in st.session_state: st.session_state.frame = None
if 'vendor_logo' not in st.session_state: st.session_state.vendor_logo = None
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wedding_name' not in st.session_state: st.session_state.wedding_name = "Pengantin Pria & Wanita"

# --- CSS ADAPTIF (Terang/Gelap) ---
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
    @media (max-width: 640px) { .wa-float { top: 10px; right: 10px; padding: 5px 10px; } }
    </style>
""", unsafe_allow_html=True)

# Tombol Share WA
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
        st.session_state.wedding_name = st.text_input("Nama Pengantin", st.session_state.wedding_name)
        
        st.divider()
        l_up = st.file_uploader("Upload Logo Vendor", type=["png"])
        if l_up: st.session_state.vendor_logo = Image.open(l_up).convert("RGBA")
        if st.session_state.vendor_logo and st.button("❌ Hapus Logo"):
            st.session_state.vendor_logo = None; st.rerun()

        st.divider()
        if st.session_state.frame is not None:
            st.image(st.session_state.frame, caption="Bingkai Aktif")
            if st.button("🗑️ Ganti Bingkai"): st.session_state.frame = None; st.rerun()
        else:
            f_up = st.file_uploader("Bingkai (PNG Transparan)", type=["png"])
            if f_up: st.session_state.frame = Image.open(f_up).convert("RGBA"); st.rerun()
        
        st.divider()
        if st.button("🚨 RESET TOTAL", type="primary", use_container_width=True): reset_data()
        if st.button("Logout", use_container_width=True): st.session_state.logged_in = False; st.rerun()

# --- HEADER ---
st.markdown(f'<h1 class="header-text">✨ Wedding Gallery of {st.session_state.wedding_name}</h1>', unsafe_allow_html=True)

# Menampilkan kembali teks Powered by Vendor
st.markdown(f'<p class="header-text" style="font-style:italic; opacity:0.8; margin-top:-10px;">Powered by {st.session_state.vendor_name}</p>', unsafe_allow_html=True)

if st.session_state.vendor_logo:
    _, mid, _ = st.columns([1, 0.3, 1])
    mid.image(st.session_state.vendor_logo, use_container_width=True)

st.divider()

# --- FUNGSI RENDER (FILTER JAM OTOMATIS) ---
def render_gallery(suffix):
    if not st.session_state.gallery:
        st.info("Galeri belum berisi foto.")
        return

    # Filter Waktu Sederhana
    c1, c2 = st.columns([3, 1])
    with c1:
        sort_f = st.selectbox("Urutan Waktu Unggah:", ["Paling Baru", "Paling Lama"], key=f"srt_{suffix}")
    with c2:
        mode = st.radio("Tampilan:", ["Grid", "List"], horizontal=True, key=f"vw_{suffix}")

    # Logika Pengurutan & Filter Data Rusak
    data = [i for i in st.session_state.gallery if isinstance(i, dict)]
    data.sort(key=lambda x: x.get('time', datetime.min), reverse=(sort_f == "Paling Baru"))

    if mode == "Grid":
        cols = st.columns(3)
        for idx, item in enumerate(data):
            with cols[idx % 3]:
                st.image(item['image'], use_container_width=True)
                t_str = item['time'].strftime('%H:%M') if 'time' in item else "--:--"
                st.markdown(f"<p style='font-size:0.8rem; text-align:center; opacity:0.7;'>⏰ Diunggah jam {t_str}</p>", unsafe_allow_html=True)
                buf = io.BytesIO(); item['image'].save(buf, format="JPEG")
                st.download_button("📥 Simpan", buf.getvalue(), f"wedding_{idx}.jpg", key=f"d_{suffix}_{idx}", use_container_width=True)
    else:
        for idx, item in enumerate(data):
            st.image(item['image'], use_container_width=True)
            t_str = item['time'].strftime('%H:%M') if 'time' in item else "--:--"
            st.write(f"⏰ Jam Unggah: {t_str}")
            buf = io.BytesIO(); item['image'].save(buf, format="JPEG")
            st.download_button(f"📥 Simpan Foto {idx+1}", buf.getvalue(), f"wedding_{idx}.jpg", key=f"l_{suffix}_{idx}")
            st.divider()

# --- DASHBOARD ---
if st.session_state.logged_in:
    t1, t2 = st.tabs(["📤 Panel Fotografer", "👁️ Preview Tamu"])
    with t1:
        uploaded = st.file_uploader("Pilih foto hasil jepretan Anda", type=["jpg", "png"], label_visibility="collapsed")
        if uploaded:
            if st.session_state.frame is None: 
                st.warning("Mohon upload bingkai di sidebar terlebih dahulu!")
            else:
                with st.spinner("Menempelkan bingkai..."):
                    # Fix Syntax & Proses Gambar
                    img = ImageOps.exif_transpose(Image.open(uploaded)).convert("RGBA")
                    f_res = st.session_state.frame.resize(img.size, Image.Resampling.LANCZOS)
                    final = Image.alpha_composite(img, f_res).convert("RGB")
                    
                    # Simpan Metadata Otomatis
                    st.session_state.gallery.append({
                        "image": final,
                        "time": datetime.now() # Waktu dicatat otomatis saat upload
                    })
                    st.toast("Foto berhasil masuk ke galeri!", icon="✅")
        render_gallery("admin")
    with t2: render_gallery("pre")
else:
    render_gallery("gst")
