import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# FOLDER_ID diletakkan paling atas (Global)
FOLDER_ID = "1dImEY0-jGA8h4mIXVnkiqrhmdKG57FgV"

# Ambil data dari Secrets
CLIENT_ID = st.secrets["google_oauth"]["client_id"]
CLIENT_SECRET = st.secrets["google_oauth"]["client_secret"]
REDIRECT_URI = st.secrets["google_oauth"]["redirect_uri"]
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_flow():
    return Flow.from_client_config(
        {"web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }},
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

st.title("✨ Wedding Gallery Live Sharing")

with st.sidebar:
    st.header("🔐 Admin")
    if 'credentials' not in st.session_state:
        flow = get_flow()
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.link_button("🔑 Login with Google", auth_url)
        
        # Proses kembalinya kode dari Google
        code = st.query_params.get("code")
        if code:
            flow.fetch_token(code=code)
            st.session_state.credentials = flow.credentials
            st.rerun()
    else:
        st.success("✅ Terhubung!")
        if st.button("Logout"):
            del st.session_state.credentials
            st.rerun()

if 'credentials' in st.session_state:
    st.divider()
    uploaded_file = st.file_uploader("Pilih foto", type=['jpg', 'png'])
    if uploaded_file and st.button("Upload"):
        try:
            service = build('drive', 'v3', credentials=st.session_state.credentials)
            file_md = {'name': uploaded_file.name, 'parents': [FOLDER_ID]}
            media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.type)
            service.files().create(body=file_md, media_body=media).execute()
            st.success("Foto masuk ke Drive!")
        except Exception as e:
            st.error(f"Error: {e}")
