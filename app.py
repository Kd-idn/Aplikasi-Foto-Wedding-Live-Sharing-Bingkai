import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from PIL import Image
import io
import os

# --- CONFIGURATION ---
NAMA_PENGANTIN = "Budi & Wati" 
NAMA_VENDOR = "Kudianta Photography"
EMAIL_ADMIN = "kudianta@gmail.com"
FOLDER_ID = "1dImEY0-jGA8h4mIXVnkiqrhm dKG57fgV".replace(" ", "") 

# OAuth Config
CLIENT_ID = st.secrets["google_oauth"]["client_id"]
CLIENT_SECRET = st.secrets["google_oauth"]["client_secret"]
REDIRECT_URI = st.secrets["google_oauth"]["redirect_uri"]
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

def get_flow():
    client_config = {"web": {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, 
                             "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                             "token_uri": "https://oauth2.googleapis.com/token"}}
    return Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=REDIRECT_URI)

# --- UI SETUP ---
st.set_page_config(page_title=f"Wedding {NAMA_PENGANTIN}", layout="centered")

# Custom CSS untuk tombol share
st.markdown("""<style>.stDownloadButton, .stButton {width: 100%;}</style>""", unsafe_allow_html=True)

st.title(f"✨ Wedding Gallery {NAMA_PENGANTIN}")
st.caption(f"Captured by: {NAMA_VENDOR}")

# --- AUTH LOGIC ---
if "auth_code" not in st.session_state:
    query_params = st.query_params
    if "code" in query_params:
        st.session_state.auth_code = query_params["code"]

if "credentials" not in st.session_state:
    if "auth_code" not in st.session_state:
        auth_url, _ = get_flow().authorization_url(prompt='consent')
        st.link_button("🔑 Login with Google untuk Kirim Foto", auth_url)
        st.stop()
    else:
        try:
            flow = get_flow()
            flow.fetch_token(code=st.session_state.auth_code)
            st.session_state.credentials = flow.credentials
            service = build('oauth2', 'v2', credentials=st.session_state.credentials)
            st.session_state.user_email = service.userinfo().get().execute().get("email")
            st.rerun()
        except:
            st.error("Sesi berakhir. Silakan login kembali.")
            if st.button("Refresh Login"):
                del st.session_state.auth_code
                st.rerun()
            st.stop()

# --- SIDEBAR NAVIGATION ---
user_email = st.session_state.get("user_email", "")
with st.sidebar:
    st.write(f"Logged in: **{user_email}**")
    menu = ["📸 Kamera & Unggah", "🖼️ Gallery Foto"]
    if user_email == EMAIL_ADMIN:
        menu.append("🎨 Admin: Upload Bingkai")
    choice = st.radio("Menu", menu)
    
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

# --- FEATURES ---

if choice == "📸 Kamera & Unggah":
    st.subheader("📸 Ambil Foto Momen Bahagia")
    # Fitur Kamera Langsung
    img_file = st.camera_input("Ambil foto sekarang")
    
    # Jika tidak pakai kamera, bisa upload file
    if not img_file:
        img_file = st.file_uploader("Atau pilih dari galeri HP", type=["jpg", "png", "jpeg"])

    if img_file:
        img = Image.open(img_file)
        
        # LOGIKA BINGKAI OTOMATIS
        if os.path.exists("bingkai.png"):
            with st.spinner("Memasang bingkai..."):
                overlay = Image.open("bingkai.png").convert("RGBA")
                img = img.convert("RGBA")
                # Resize bingkai agar pas dengan foto
                overlay = overlay.resize(img.size)
                img = Image.alpha_composite(img, overlay)
                img = img.convert("RGB")
        
        st.image(img, caption="Hasil Foto Berbingkai", use_container_width=True)
        
        if st.button("🚀 Kirim ke Gallery Drive"):
            with st.spinner("Sedang mengupload..."):
                buf = io.BytesIO()
                img.save(buf, format="JPEG")
                
                drive_service = build('drive', 'v3', credentials=st.session_state.credentials)
                file_metadata = {'name': f"Wedding_{img_file.name}", 'parents': [FOLDER_ID]}
                media = MediaIoBaseUpload(buf, mimetype='image/jpeg', resumable=True)
                drive_service.files().create(body=file_metadata, media_body=media).execute()
                
                st.balloons()
                st.success("Foto Berhasil Dikirim!")
                
                # Fitur Share Link
                share_url = f"https://drive.google.com/drive/folders/{FOLDER_ID}"
                st.text_input("Salin Link Gallery untuk Teman:", share_url)
                st.share_button("Bagikan Link Gallery", url=share_url)

elif choice == "🖼️ Gallery Foto":
    st.subheader("🖼️ Live Gallery")
    st.info("Menampilkan foto terbaru langsung dari Drive.")
    st.link_button("📂 Buka Full Gallery (Google Drive)", f"https://drive.google.com/drive/folders/{FOLDER_ID}")
    
    # Menampilkan hasil upload di web secara sederhana (melalui link)
    st.write("Daftar momen terbaru akan muncul di folder Drive di atas secara real-time.")

elif choice == "🎨 Admin: Upload Bingkai":
    st.subheader("Upload Master Bingkai")
    st.warning("Pastikan file bernama 'bingkai.png' dan memiliki background transparan.")
    new_frame = st.file_uploader("Pilih file bingkai (.png)", type=["png"])
    if st.button("Simpan Bingkai Baru"):
        if new_frame:
            with open("bingkai.png", "wb") as f:
                f.write(new_frame.getbuffer())
            st.success("Bingkai berhasil diperbarui! Sekarang semua foto baru akan menggunakan bingkai ini.")
        else:
            st.error("Pilih file dulu!")
