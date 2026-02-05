import streamlit as st
from PIL import Image, ImageOps
import io
import urllib.parse
from datetime import datetime

# 1. Konfigurasi Awal
st.set_page_config(page_title="Wedding Gallery Pro", layout="wide", initial_sidebar_state="collapsed")

# 2. Fungsi Reset & Inisialisasi
def reset_data():
    st.session_state.gallery = []
    st.session_state.frame = None
    st.session_state.vendor_logo = None
    st.session_state.wedding_name = "Pengantin Pria & Wanita"
    st.session_state.vendor_name = "Nama Vendor Anda"
    st.session_state.categories = ["All", "Akad", "Resepsi", "Photobooth"]
    st.toast("Semua data telah di-reset!", icon="🗑️")

if 'gallery' not in st.session_state: st.session_state.gallery = []
if 'categories' not in st.session_state: st.session_state.categories = ["All", "Akad", "Resepsi", "Photobooth"]
if 'frame' not in st.session_state: st.session_state.frame = None
if 'vendor_logo' not in st.session_state: st.session_state.vendor_logo = None
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wedding_name' not in st.session_state: st.session_state.wedding_name = "Pengantin Pria & Wanita"
if 'vendor_name' not in st.session_state: st.session_state.vendor_name = "Nama Vendor Anda"

APP_URL = "https://aplikasi-foto-wedding-live-sharing-bingkai-ko2zzkcx2nhyww9o2dv.streamlit.app/"

# --- CSS ADAPTIF ---
st.markdown(f"""
    <style>
    .header-text {{ color: var(--text-color); text-align: center; }}
    .wa-float {{
        position: fixed; top: 20px; right: 20px; background-color: #25D366;
        color: white !important; padding: 8px 15px; border-radius: 50px;
        z-index: 1000; text-decoration: none; font-weight: bold; font-size: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2); display: flex; align-items: center; gap: 5px;
    }}
    .timestamp {{ font-size: 0.8rem; color: gray; margin-bottom: 5px; }}
    </style>
""", unsafe_allow_html=True)

# Tombol Share WA
text_share = urllib.parse.quote(f"Lihat foto {st.session_state.wedding_name} di: {APP_URL}")
st.markdown(f'<a href="https://wa.me/?text={text_share}" class="wa-float" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="15px"> Bagikan</a>', unsafe_allow_html=True)

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.title("🔐 Admin Panel")
    if not st.session_state.logged_in:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "admin" and pwd == "wedding123":
                st.session_state.logged_in = True; st.rerun()
    else:
        st.success("Admin Aktif")
        st.session_state.wedding_name = st.text_input("Nama Pengantin", st.session_state.wedding_name)
        st.session_state.vendor_name = st.text_input("Nama Vendor", st.session_state.vendor_name)
        
        # Kelola Kategori
        st.divider()
        st.subheader("📁 Kelola Kategori")
        new_cat = st.text_input("Tambah Kategori Baru")
        if st.button("Tambah"):
            if new_cat and new_cat not in st.session_state.categories:
                st.session_state.categories.append(new_cat); st.rerun()
        
        st.divider()
        logo_up = st.file_uploader("Upload Logo Vendor", type=["png"])
        if logo_up: st.session_state.vendor_logo = Image.open(logo_up).convert("RGBA")
        if st.session_state.vendor_logo and st.button("❌ Hapus Logo"):
            st.session_state.vendor_logo = None; st.rerun()

        st.divider()
        if st.session_state.frame is not None:
            st.image(st.session_state.frame, caption="Bingkai Aktif")
            if st.button("🗑️ Ganti Bingkai"): st.session_state.frame = None; st.rerun()
        else:
            frame_up = st.file_uploader("Bingkai (PNG)", type=["png"])
            if frame_up: st.session_state.frame = Image.open(frame_up).convert("RGBA"); st.rerun()
        
        if st.button("🚨 RESET SEMUA", use_container_width=True, type="primary"):
            reset_data(); st.rerun()
        if st.button("Logout", use_container_width=True): 
            st.session_state.logged_in = False; st.rerun()

# --- HEADER ---
st.markdown(f'<h1 class="header-text">✨ Wedding Gallery of {st.session_state.wedding_name}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="header-text" style="font-style:italic; opacity:0.8;">Powered by {st.session_state.vendor_name}</p>', unsafe_allow_html=True)
if st.session_state.vendor_logo:
    _, center_col, _ = st.columns([1, 0.3, 1])
    center_col.image(st.session_state.vendor_logo, use_container_width=True)

st.divider()

# --- FUNGSI RENDER DENGAN FILTER ---
def render_gallery(suffix):
    if not st.session_state.gallery:
        st.info("Belum ada foto.")
        return

    # Filter UI
    f_col1, f_col2, f_col3 = st.columns([2, 2, 1])
    with f_col1:
        cat_filter = st.selectbox("Filter Kategori:", st.session_state.categories, key=f"cat_{suffix}")
    with f_col2:
        sort_order = st.selectbox("Urutan Waktu:", ["Terbaru", "Terlama"], key=f"sort_{suffix}")
    with f_col3:
        mode = st.radio("View:", ["Grid", "List"], horizontal=True, key=f"m_{suffix}")

    # Logika Filtering
    filtered_data = st.session_state.gallery
    if cat_filter != "All":
        filtered_data = [f for f in filtered_data if f['category'] == cat_filter]
    
    if sort_order == "Terlama":
        filtered_data = sorted(filtered_data, key=lambda x: x['time'])
    else:
        filtered_data = sorted(filtered_data, key=lambda x: x['time'], reverse=True)

    if not filtered_data:
        st.warning("Tidak ada foto di kategori ini.")
        return

    # Render Content
    if mode == "Grid":
        cols = st.columns(3)
        for idx, item in enumerate(filtered_data):
            with cols[idx % 3]:
                st.image(item['image'], use_container_width=True)
                st.markdown(f"<div class='timestamp'>⏰ {item['time'].strftime('%H:%M')} | {item['category']}</div>", unsafe_allow_html=True)
                buf = io.BytesIO(); item['image'].save(buf, format="JPEG")
                st.download_button("📥 Simpan", buf.getvalue(), f"img_{idx}.jpg", key=f"b_{suffix}_{idx}", use_container_width=True)
    else:
        for idx, item in enumerate(filtered_data):
            st.image(item['image'], use_container_width=True)
            st.write(f"⏰ Diunggah: {item['time'].strftime('%d %b, %H:%M')} | Kategori: {item['category']}")
            buf = io.BytesIO(); item['image'].save(buf, format="JPEG")
            st.download_button(f"Simpan Foto {idx+1}", buf.getvalue(), f"img_{idx}.jpg", key=f"l_{suffix}_{idx}")
            st.divider()

# --- DASHBOARD ---
if st.session_state.logged_in:
    tab1, tab2 = st.tabs(["📤 Upload", "👁️ Preview"])
    with tab1:
        up_col1, up_col2 = st.columns(2)
        with up_col1:
            category_choice = st.selectbox("Pilih Kategori Foto:", st.session_state.categories[1:])
        with up_col2:
            up = st.file_uploader("Upload", type=["jpg","png"], label_visibility="collapsed")
        
        if up:
            if st.session_state.frame is None: st.warning("Bingkai belum di-upload!")
            else:
                img = ImageOps.exif_transpose(Image.open(up)).convert("RGBA")
                f_res = st.session_state.frame.resize(img.size, Image.Resampling.LANCZOS)
                final = Image.alpha_composite(img, f_res).convert("RGB")
                # Simpan metadata: Gambar, Waktu, Kategori
                st.session_state.gallery.append({
                    "image": final,
                    "time": datetime.now(),
                    "category": category_choice
                })
                st.success(f"Berhasil di-upload ke {category_choice}!")
        render_gallery("adm")
    with tab2: render_gallery("pre")
else:
    render_gallery("gst")
