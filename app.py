import streamlit as st
from PIL import Image, ImageOps
import io
import urllib.parse
from datetime import datetime

# 1. Konfigurasi Awal
st.set_page_config(page_title="Wedding Gallery Live", layout="wide", initial_sidebar_state="collapsed")

# 2. Inisialisasi State yang Aman
if 'gallery' not in st.session_state: st.session_state.gallery = []
if 'frame' not in st.session_state: st.session_state.frame = None
if 'vendor_logo' not in st.session_state: st.session_state.vendor_logo = None
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wedding_name' not in st.session_state: st.session_state.wedding_name = "Pengantin Pria & Wanita"
if 'vendor_name' not in st.session_state: st.session_state.vendor_name = "Nama Vendor Anda"
# State tambahan untuk mencegah double upload pada satu sesi rerun
if 'last_uploaded' not in st.session_state: st.session_state.last_uploaded = None

def reset_data():
    st.session_state.gallery = []
    st.session_state.frame = None
    st.session_state.vendor_logo = None
    st.rerun()

# --- CSS ADAPTIF ---
st.markdown("""<style>.stApp h1, .stApp p, .stApp label { color: var(--text-color) !important; }.header-text { text-align: center; }</style>""", unsafe_allow_html=True)

# --- SIDEBAR & HEADER (Sama seperti sebelumnya) ---
with st.sidebar:
    st.title("🔐 Admin")
    if st.session_state.logged_in:
        st.session_state.wedding_name = st.text_input("Nama Pengantin", st.session_state.wedding_name)
        st.session_state.vendor_name = st.text_input("Nama Vendor", st.session_state.vendor_name)
        if st.button("🚨 RESET TOTAL", type="primary"): reset_data()

# --- FUNGSI RENDER (DENGAN KEY UNIK) ---
def render_gallery(suffix):
    if not st.session_state.gallery:
        st.info("Galeri kosong.")
        return

    # Filter & Sort
    data = [i for i in st.session_state.gallery if isinstance(i, dict)]
    data.sort(key=lambda x: x.get('time', datetime.min), reverse=True)

    cols = st.columns(3)
    for idx, item in enumerate(data):
        with cols[idx % 3]:
            st.image(item['image'], use_container_width=True)
            t_str = item['time'].strftime('%H:%M')
            st.caption(f"⏰ {t_str}")
            buf = io.BytesIO()
            item['image'].save(buf, format="JPEG")
            # Menambahkan suffix agar KEY download button unik dan tidak error duplicate key
            st.download_button("📥", buf.getvalue(), f"img_{idx}.jpg", key=f"dl_{suffix}_{idx}_{t_str}", use_container_width=True)

# --- PANEL UPLOAD (CEK DUPLIKASI) ---
if st.session_state.logged_in:
    t1, t2 = st.tabs(["📤 Upload", "👁️ Preview"])
    with t1:
        uploaded_file = st.file_uploader("Upload Foto", type=["jpg", "png"])
        
        # Validasi: Hanya proses jika file baru dan belum pernah diproses di sesi ini
        if uploaded_file is not None and uploaded_file.name != st.session_state.last_uploaded:
            if st.session_state.frame is None:
                st.warning("Upload bingkai dulu!")
            else:
                with st.spinner("Processing..."):
                    img = ImageOps.exif_transpose(Image.open(uploaded_file)).convert("RGBA")
                    fw, fh = st.session_state.frame.size
                    
                    # Smart Center-Crop (Story IG Format)
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
                    
                    final = Image.alpha_composite(img.resize((fw, fh)), st.session_state.frame).convert("RGB")
                    
                    # Simpan dan tandai file terakhir agar tidak duplikat saat rerun
                    st.session_state.gallery.append({"image": final, "time": datetime.now()})
                    st.session_state.last_uploaded = uploaded_file.name 
                    st.toast("Foto Berhasil!")
                    st.rerun() # Paksa rerun agar state terupdate bersih

        render_gallery("admin")
    with t2:
        render_gallery("preview")
else:
    render_gallery("guest")
