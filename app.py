import streamlit as st
from PIL import Image, ImageOps
import io
from datetime import datetime
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload

# 1. Konfigurasi Dasar
st.set_page_config(page_title="Wedding Gallery Live", layout="wide", initial_sidebar_state="collapsed")

# 2. Inisialisasi Session State
if 'gallery' not in st.session_state: st.session_state.gallery = []
if 'frame' not in st.session_state: st.session_state.frame = None
if 'vendor_logo' not in st.session_state: st.session_state.vendor_logo = None
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'wedding_name' not in st.session_state: st.session_state.wedding_name = "Si A & Si B"
if 'vendor_name' not in st.session_state: st.session_state.vendor_name = "Nama Vendor Anda"
if 'last_processed_file' not in st.session_state: st.session_state.last_processed_file = None

# --- FUNGSI GOOGLE DRIVE ---
def upload_to_drive(img_bytes, filename):
    try:
        # Mengambil kredensial dari Streamlit Secrets
        info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': filename,
            # GANTI kode di bawah ini dengan ID Folder dari URL browser Anda
            'parents': ['1dImEY0-jGA8h4mIXVnkiqrhmdKG57FgV'] 
        }
        
        media = MediaIoBaseUpload(io.BytesIO(img_bytes), mimetype='image/jpeg')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    except Exception as e:
        st.error(f"Gagal upload ke Drive: {e}")
        return None

def reset_all_data():
    st.session_state.gallery = []
    st.session_state.frame = None
    st.session_state.vendor_logo = None
    st.session_state.last_processed_file = None
    st.rerun()

# --- CSS ADAPTIF ---
st.markdown("""
    <style>
    .stApp h1, .stApp p, .stApp label, .stApp div { color: var(--text-color) !important; }
    .header-text { text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: KENDALI ADMIN ---
with st.sidebar:
    st.title("🔐 Kendali Admin")
    if not st.session_state.logged_in:
        u = st.text_input("Username", key="login_username")
        p = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="btn_login_submit"):
            if u == "admin" and p == "wedding123":
                st.session_state.logged_in = True; st.rerun()
    else:
        st.session_state.wedding_name = st.text_input("Nama Pengantin", st.session_state.wedding_name)
        st.session_state.vendor_name = st.text_input("Nama Vendor", st.session_state.vendor_name)
        st.divider()
        l_up = st.file_uploader("Upload Logo Vendor", type=["png"])
        if l_up: st.session_state.vendor_logo = Image.open(l_up).convert("RGBA")
        f_up = st.file_uploader("Upload Bingkai Story", type=["png"])
        if f_up: st.session_state.frame = Image.open(f_up).convert("RGBA")
        
        if st.session_state.frame:
            st.image(st.session_state.frame, caption="Bingkai Aktif", width=80)
            if st.button("🗑️ Hapus Bingkai"): st.session_state.frame = None; st.rerun()
        
        st.divider()
        if st.button("🚨 RESET TOTAL", type="primary", use_container_width=True): reset_all_data()
        if st.button("Logout", use_container_width=True): st.session_state.logged_in = False; st.rerun()

# --- HEADER ---
st.markdown(f'<h1 class="header-text">✨ Wedding Gallery of {st.session_state.wedding_name}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="header-text" style="font-style:italic; opacity:0.8; margin-top:-10px;">Powered by {st.session_state.vendor_name}</p>', unsafe_allow_html=True)

if st.session_state.vendor_logo:
    _, mid, _ = st.columns([1, 0.3, 1])
    mid.image(st.session_state.vendor_logo, use_container_width=True)

st.divider()

# --- FUNGSI RENDER GALERI ---
def render_gallery_content(suffix):
    if not st.session_state.gallery:
        st.info("Galeri belum berisi foto.")
        return

    valid_data = [i for i in st.session_state.gallery if isinstance(i, dict)]
    valid_data.sort(key=lambda x: x.get('time', datetime.min), reverse=True)

    cols = st.columns(3)
    for idx, item in enumerate(valid_data):
        with cols[idx % 3]:
            st.image(item['image'], use_container_width=True)
            t_str = item['time'].strftime('%H:%M')
            st.caption(f"⏰ {t_str}")
            if 'image_bytes' in item:
                st.download_button(
                    label="📥 Simpan",
                    data=item['image_bytes'],
                    file_name=f"wedding_{idx}.jpg",
                    key=f"dl_btn_{suffix}_{idx}_{item['time'].timestamp()}",
                    use_container_width=True
                )

# --- DASHBOARD UTAMA ---
if st.session_state.logged_in:
    t1, t2 = st.tabs(["📤 Panel Fotografer", "👁️ Preview Tampilan Tamu"])
    with t1:
        st.subheader("Kirim Hasil Foto")
        uploaded = st.file_uploader("Drag and drop file here", type=["jpg", "png", "jpeg"], key="main_uploader")
        
        if uploaded and uploaded.name != st.session_state.last_processed_file:
            if st.session_state.frame is None:
                st.warning("Silakan upload bingkai potret terlebih dahulu di sidebar!")
            else:
                with st.spinner("Proses Bingkai & Sinkronisasi Drive..."):
                    img = ImageOps.exif_transpose(Image.open(uploaded)).convert("RGBA")
                    fw, fh = st.session_state.frame.size
                    
                    # Smart Center-Crop
                    img_ratio, frame_ratio = img.width / img.height, fw / fh
                    if img_ratio > frame_ratio:
                        new_w = int(frame_ratio * img.height)
                        left = (img.width - new_w) / 2
                        img = img.crop((left, 0, left + new_w, img.height))
                    else:
                        new_h = int(img.width / frame_ratio)
                        top = (img.height - new_h) / 2
                        img = img.crop((0, top, img.width, top + new_h))
                    
                    final_img = Image.alpha_composite(img.resize((fw, fh)), st.session_state.frame).convert("RGB")
                    
                    # Konversi ke bytes
                    img_byte_arr = io.BytesIO()
                    final_img.save(img_byte_arr, format='JPEG', quality=95)
                    img_data = img_byte_arr.getvalue()
                    
                    # --- UPLOAD KE DRIVE ---
                    file_name_drive = f"wedding_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    drive_id = upload_to_drive(img_data, file_name_drive)
                    
                    # Simpan ke state galeri lokal
                    st.session_state.gallery.append({
                        "image": final_img,
                        "image_bytes": img_data,
                        "time": datetime.now(),
                        "drive_id": drive_id
                    })
                    st.session_state.last_processed_file = uploaded.name
                    st.toast("Tersimpan di Galeri & Drive!", icon="☁️")
                    time.sleep(1)
                    st.rerun()
    with t2:
        render_gallery_content("admin")
else:
    render_gallery_content("public")
