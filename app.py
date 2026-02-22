import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from PIL import Image, ImageOps
import io

# --- CONFIGURATION (Identitas Acara & Vendor) ---
NAMA_PENGANTIN = "Budi & Wati"  # <--- Ganti dengan nama pengantin
NAMA_VENDOR = "Kudianta Photography" # <--- Ganti dengan nama vendor Anda
EMAIL_ADMIN = "kudianta@gmail.com" # <--- Email Anda untuk akses menu Admin

# --- GOOGLE DRIVE & OAUTH CONFIG ---
# ID Folder dari Drive (Spasi sudah dihapus otomatis)
FOLDER_ID = "1dImEY0-jGA8h4mIXVnkiqrhm dKG57fgV".replace(" ", "") 

CLIENT_ID = st.secrets["google_oauth"]["client_id"]
CLIENT_SECRET = st.secrets["google_oauth"]["client_secret"]
REDIRECT_URI = st.secrets["google_oauth"]["redirect_uri"]
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/userinfo.email', 'openid']

def get_flow():
    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    return Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=REDIRECT_URI)

# --- UI SETUP ---
st.set_page_config(page_title=f"Wedding {NAMA_PENGANTIN}", page_icon="✨")

# Header Utama
st.title(f"✨ Wedding Gallery {NAMA_PENGANTIN}")
st.write(f"Captured by: **{NAMA_VENDOR}**")

# Sinkronisasi Session State
if "auth_code" not in st.session_state:
    query_params = st.query_params
    if "code" in query_params:
        st.session_state.auth_code = query_params["code"]

# --- AUTH LOGIC ---
if "credentials" not in st.session_state:
    if "auth_code" not in st.session_state:
        flow = get_flow()
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.info("Selamat datang! Silakan login untuk berbagi momen bahagia.")
        st.link_button("🔑 Login with Google", auth_url)
        st.stop()
    else:
        try:
            flow = get_flow()
            flow.fetch_token(code=st.session_state.auth_code)
            st.session_state.credentials = flow.credentials
            # Ambil email user
            service = build('oauth2', 'v2', credentials=st.session_state.credentials)
            user_info = service.userinfo().get().execute()
            st.session_state.user_email = user_info.get("email")
            st.rerun()
        except Exception as e:
            st.error(f"Login Gagal: {e}")
            if st.button("Coba Login Lagi"):
                del st.session_state.auth_code
                st.rerun()
            st.stop()

# --- SIDEBAR & MENU NAVIGATION ---
user_email = st.session_state.get("user_email", "")
with st.sidebar:
    st.success(f"✅ Terhubung: {user_email}")
    menu = ["📸 Unggah Foto", "🖼️ Lihat Gallery"]
    
    # Menu Admin muncul jika email cocok
    if user_email == EMAIL_ADMIN:
        st.markdown("---")
        st.subheader("🛠️ Admin Panel")
        menu.append("🎨 Kelola Bingkai")
    
    choice = st.radio("Pilih Menu:", menu)
    
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- MAIN FEATURES ---

if choice == "📸 Unggah Foto":
    st.subheader("📤 Kirim Foto Anda")
    uploaded_file = st.file_uploader("Pilih file gambar", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Preview Foto", use_container_width=True)
        
        if st.button("Simpan ke Folder Wedding"):
            try:
                # Proses Bingkai (Otomatis jika ada file bingkai.png di folder lokal)
                try:
                    overlay = Image.open("bingkai.png").convert("RGBA")
                    img = img.convert("RGBA")
                    # Resize bingkai agar sesuai ukuran foto
                    overlay = overlay.resize(img.size)
                    img.paste(overlay, (0, 0), overlay)
                    img = img.convert("RGB")
                except FileNotFoundError:
                    pass # Jika tidak ada bingkai, kirim foto asli

                # Simpan ke Buffer
                buf = io.BytesIO()
                img.save(buf, format="JPEG")
                buf.seek(0)
                
                # Upload ke Drive
                drive_service = build('drive', 'v3', credentials=st.session_state.credentials)
                file_metadata = {
                    'name': f"Wedding_{user_email.split('@')[0]}_{uploaded_file.name}",
                    'parents': [FOLDER_ID]
                }
                media = MediaIoBaseUpload(buf, mimetype='image/jpeg', resumable=True)
                drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                
                st.balloons()
                st.success("Foto berhasil tersimpan di Drive pribadi Anda!")
                st.link_button("📂 Lihat Semua Foto di Drive", f"https://drive.google.com/drive/folders/{FOLDER_ID}")
                
            except Exception as e:
                st.error(f"Gagal mengunggah: {e}")

elif choice == "🖼️ Lihat Gallery":
    st.subheader("✨ Gallery Momen Bahagia")
    st.info("Anda dapat melihat seluruh foto yang telah diunggah tamu lain di sini.")
    st.link_button("🌐 Buka Google Drive Gallery", f"https://drive.google.com/drive/folders/{FOLDER_ID}")

elif choice == "🎨 Kelola Bingkai":
    st.subheader("Upload Bingkai (bingkai.png)")
    st.write("Admin bisa mengganti bingkai aplikasi di sini.")
    new_frame = st.file_uploader("Upload bingkai transparan format .PNG", type=["png"])
    if new_frame:
        with open("bingkai.png", "wb") as f:
            f.write(new_frame.getbuffer())
        st.success("Bingkai berhasil diperbarui!")
