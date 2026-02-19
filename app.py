import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Konfigurasi Folder & Secrets
FOLDER_ID = "1dImEY0-jGA8h4mIXVnkiqrhmdKG57FgV"
CLIENT_ID = st.secrets["google_oauth"]["client_id"]
CLIENT_SECRET = st.secrets["google_oauth"]["client_secret"]
REDIRECT_URI = st.secrets["google_oauth"]["redirect_uri"]
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_flow():
    # Menggunakan konfigurasi langsung agar lebih akurat
    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    return Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

st.title("✨ Wedding Gallery Live Sharing")

# --- LOGIKA LOGIN ---
if 'credentials' not in st.session_state:
    # Cek apakah ada kode kembali dari Google di URL
    query_params = st.query_params
    if "code" in query_params:
        try:
            flow = get_flow()
            flow.fetch_token(code=query_params["code"])
            st.session_state.credentials = flow.credentials
            st.query_params.clear() # Bersihkan URL
            st.rerun()
        except Exception as e:
            st.error(f"Login Gagal: {e}")
            if st.button("Coba Login Lagi"):
                st.query_params.clear()
                st.rerun()
    else:
        st.info("Silakan login untuk mengunggah foto.")
        flow = get_flow()
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.link_button("🔑 Login with Google", auth_url)

# --- PANEL UPLOAD ---
else:
    with st.sidebar:
        st.success("✅ Terhubung ke Drive")
        if st.button("Logout"):
            del st.session_state.credentials
            st.rerun()

    st.subheader("📸 Unggah Foto")
    uploaded_file = st.file_uploader("Pilih file gambar", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file and st.button("Simpan ke Folder Wedding"):
        try:
            service = build('drive', 'v3', credentials=st.session_state.credentials)
            file_metadata = {'name': uploaded_file.name, 'parents': [FOLDER_ID]}
            media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.type)
            service.files().create(body=file_metadata, media_body=media).execute()
            st.balloons()
            st.success("Foto berhasil tersimpan di Drive pribadi Anda!")
        except Exception as e:
            st.error(f"Gagal Upload: {e}")
