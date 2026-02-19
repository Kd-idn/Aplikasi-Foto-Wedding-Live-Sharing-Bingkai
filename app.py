import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# Konfigurasi Halaman
st.set_page_config(page_title="Wedding Gallery", layout="wide")

# Ambil data dari Secrets
CLIENT_ID = st.secrets["google_oauth"]["client_id"]
CLIENT_SECRET = st.secrets["google_oauth"]["client_secret"]
REDIRECT_URI = st.secrets["google_oauth"]["redirect_uri"]

# Scopes yang dibutuhkan
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_flow():
    return Flow.from_client_config(
        {"web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI]
        }},
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

# --- UI UTAMA ---
st.title("✨ Wedding Gallery of Si A & Si B")

# Sidebar untuk Admin
with st.sidebar:
    st.header("🔐 Kendali Admin")
    if 'credentials' not in st.session_state:
        # Tombol Login Google
        flow = get_flow()
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.link_button("🔑 Login with Google Drive", auth_url)
        
        # Cek jika kembali dari login
        code = st.query_params.get("code")
        if code:
            flow.fetch_token(code=code)
            st.session_state.credentials = flow.credentials
            st.rerun()
    else:
        st.success("✅ Terhubung ke Drive Anda")
        if st.button("Logout"):
            del st.session_state.credentials
            st.rerun()

# --- BAGIAN UPLOAD (Hanya muncul jika sudah login) ---
if 'credentials' in st.session_state:
    st.divider()
    st.subheader("📸 Unggah Foto Baru")
    uploaded_file = st.file_uploader("Pilih foto (JPG/PNG)", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file and st.button("Simpan ke Drive"):
        try:
            service = build('drive', 'v3', credentials=st.session_state.credentials)
            
            file_metadata = {'name': uploaded_file.name}
            media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.type)
            
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            st.success(f"Berhasil! Foto tersimpan dengan ID: {file.get('id')}")
        except Exception as e:
            st.error(f"Gagal upload: {e}")
else:
    st.info("Silakan login melalui sidebar untuk mengunggah foto.")
