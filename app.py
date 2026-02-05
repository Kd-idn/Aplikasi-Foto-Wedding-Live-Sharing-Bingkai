import streamlit as st
from PIL import Image, ImageOps
import io
import urllib.parse
from datetime import datetime

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Wedding Gallery Pro", layout="wide", initial_sidebar_state="collapsed")

# 2. Fungsi Reset
def reset_data():
    st.session_state.gallery = []
    st.session_state.frame = None
    st.session_state.vendor_logo = None
    st.session_state.wedding_name = "Pengantin Pria & Wanita"
    st.session_state.vendor_name = "Nama Vendor Anda"
    st.session_state.categories = ["All", "Akad", "Resepsi", "Photobooth"]
    st.rerun()

# Inisialisasi Session State
if 'gallery' not in st.session_state: st.session_state.gallery = []
if 'categories' not in st.session_state: st.session_state.categories = ["All", "Akad", "Resepsi", "Photobooth"]
if 'frame' not in st.session_state: st.session_state.frame = None
if 'vendor_logo' not in st.session_state: st.session_state.vendor_logo = None
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wedding_name' not in st.session_state: st.session_state.wedding_name = "Pengantin Pria & Wanita"
if 'vendor_name' not in st.session_state: st.session_state.vendor_name = "Nama Vendor Anda"

APP_URL = "https://aplikasi-foto-wedding-live-sharing-bingkai-ko2zzkcx2nhyww9o2dv.streamlit.app/"

# --- CSS ADAPTIF & WA FLOAT ---
st.markdown(f"""
    <style>
    .stApp h1, .stApp p, .stApp label {{ color: var(--text-color) !important; }}
    .header-text {{ text-align: center; }}
    .wa-float {{
        position: fixed; top: 20px; right: 20px; background-color: #25D366;
        color: white !important; padding: 8px 15px; border-radius: 50px;
        z-index: 1000; text-decoration: none; font-weight: bold; font-size: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2); display: flex; align-items: center; gap: 5px;
    }}
    @media (max-width: 640px) {{ .wa-float {{ top: 10px; right: 10px; }} }}
    </style>
""", unsafe_allow_html=True)

# Tombol Bagikan
text_share = urllib.parse.quote(f"Lihat momen {st.session_state.wedding_name} di: {APP_URL}")
st.markdown(f'<a href="https://wa.me/?text={text_share}" class="wa-float" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="15px"> Bagikan</a>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔐 Admin Panel")
    if not st.session_state.logged_in:
        user = st.text_input("User")
        pwd = st.text_input("Pass", type="password")
        if st.button("Login"):
            if user == "admin" and pwd == "wedding123":
                st.session_state.logged_in = True; st.rerun()
    else:
        st.session_state.wedding_name = st.text_input("Pengantin", st.session_state.wedding_name)
        st.session_state.vendor_name = st.text_input("Vendor", st.session_state.vendor_name)
        
        st.divider()
        new_cat = st.text_input("Kategori Baru")
        if st.button("Tambah"):
            if new_cat and new_cat not in st.session_state.categories:
                st.session_state.categories.append(new_cat); st.rerun()
        
        st.divider()
        logo_up = st.file_uploader("Logo", type=["png"])
        if logo_up: st.session_state.vendor_logo = Image.open(logo_up).convert("RGBA")
        if st.session_state.vendor_logo and st.button("❌ Hapus Logo"):
            st.session_state.vendor_logo = None; st.rerun()

        st.divider()
        if st.session_state.frame is not None:
            st.image(st.session_state.frame)
            if st.button("🗑️ Ganti Bingkai"): st.session_state.frame = None; st.rerun()
        else:
            frame_up = st.file_uploader("Bingkai (PNG)", type=["png"])
            if frame_up: st.session_state.frame = Image.open(frame_up).convert("RGBA"); st.rerun()
        
        st.divider()
        if st.button("🚨 RESET SEMUA", use_container_width=True, type="primary"): reset_data()
        if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

# --- HEADER ---
st.markdown(f'<h1 class="header-text">✨ Wedding Gallery of {st.session_state.wedding_name}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="header-text" style="font-style:italic; opacity:0.8;">Powered by {st.session_state.vendor_name}</p>', unsafe_allow_html=True)

if st.session_state.vendor_logo:
    _, center_col, _ = st.columns([1, 0.3, 1])
    center_col.image(st.session_state.vendor_logo, use_container_width=True)

st.divider()

# --- RENDER FUNGSI ---
def render_gallery(suffix):
    if not st.session_state.gallery:
        st.info("Galeri kosong.")
        return

    f_col1, f_col2, f_col3 = st.columns([2, 2, 1])
    with f_col1: cat_f = st.selectbox("Kategori:", st.session_state.categories, key=f"c_{suffix}")
    with f_col2: sort_f = st.selectbox("Urutan:", ["Terbaru", "Terlama"], key=f"s_{suffix}")
    with f_col3: mode = st.radio("View:", ["Grid", "List"], horizontal=True, key=f"v_{suffix}")

    # Proteksi Sorting (Gunakan .get untuk menghindari TypeError)
    data = st.session_state.gallery
    if cat_f != "All":
        data = [i for i in data if i.get('category') == cat_f]
    
    data = sorted(data, key=lambda x: x.get('time', datetime.min), reverse=(sort_f == "Terbaru"))

    if mode == "Grid":
        cols = st.columns(3)
        for idx, item in enumerate(data):
            with cols[idx % 3]:
                st.image(item['image'], use_container_width=True)
                t_str = item['time'].strftime('%H:%M') if 'time' in item else "--:--"
                st.caption(f"⏰ {t_str} | {item.get('category','-')}")
                buf = io.BytesIO(); item['image'].save(buf, format="JPEG")
                st.download_button("📥", buf.getvalue(), f"f_{idx}.jpg", key=f"d_{suffix}_{idx}", use_container_width=True)
    else:
        for idx, item in enumerate(data):
            st.image(item['image'], use_container_width=True)
            t_str = item['time'].strftime('%H:%M') if 'time' in item else "--:--"
            st.write(f"⏰ {t_str} | {item.get('category','-')}")
            buf = io.BytesIO(); item['image'].save(buf, format="JPEG")
            st.download_button(f"Simpan Foto {idx+1}", buf.getvalue(), f"f_{idx}.jpg", key=f"l_{suffix}_{idx}")
            st.divider()

# --- MAIN ---
if st.session_state.logged_in:
    t1, t2 = st.tabs(["📤 Upload", "👁️ Preview"])
    with t1:
        u_col1, u_col2 = st.columns(2)
        with u_col1: sel_cat = st.selectbox("Pilih Kategori:", st.session_state.categories[1:])
        with u_col2: up = st.file_uploader("Upload", type=["jpg","png"], label_visibility="collapsed")
        
        if up:
            if st.session_state.frame is None: st.warning("Upload bingkai!")
            else:
                # PERBAIKAN SYNTAX DISINI: Tanda kurung ditutup dengan benar
                img = ImageOps.exif_transpose(Image.open(up)).convert("RGBA")
                f_res = st.session_state.frame.resize(img.size, Image.Resampling.LANCZOS)
                final = Image.alpha_composite(img, f_res).convert("RGB")
                st.session_state.gallery.append({
                    "image": final, "time": datetime.now(), "category": sel_cat
                })
                st.toast("Terkirim!")
        render_gallery("adm")
    with t2: render_gallery("pre")
else:
    render_gallery("gst")
