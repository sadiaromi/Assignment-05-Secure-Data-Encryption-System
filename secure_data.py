import streamlit as st
import hashlib
from cryptography.fernet import Fernet

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'stored_data' not in st.session_state:
    st.session_state.stored_data = {}
if 'failed_attempts' not in st.session_state:
    st.session_state.failed_attempts = 0
if 'encryption_key' not in st.session_state:
    st.session_state.encryption_key = Fernet.generate_key()
    st.session_state.cipher_suite = Fernet(st.session_state.encryption_key)

# Navigation functions
def navigate(page):
    st.session_state.page = page
    if page == 'retrieve':
        st.session_state.failed_attempts = 0

# Security functions
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def encrypt_data(data):
    return st.session_state.cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data):
    try:
        return st.session_state.cipher_suite.decrypt(encrypted_data.encode()).decode()
    except:
        return None


def render_header(title):
    st.markdown("""
        <style>
            .title {
                text-align: center;
                font-size: 28px;
                font-weight: bold;
                color: #00796B;
            }
            .divider {
                margin-top: 10px;
                margin-bottom: 20px;
                border-bottom: 2px solid #ddd;
            }
        </style>
    """, unsafe_allow_html=True)
    st.markdown(f'<p class="title">{title}</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


def home_page():
    render_header("🔒 Secure Data Encryption System")
    st.write("Your data is encrypted and stored securely with a unique passkey 📂🔑.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📂 Store Data", use_container_width=True):
            navigate('insert')
    with col2:
        if st.button("🔎 Retrieve Data", use_container_width=True):
            navigate('retrieve')

def insert_data_page():
    render_header("🔐 Store Data Securely")
    data_id = st.text_input("Data ID")
    data = st.text_area("Enter Data")
    passkey = st.text_input("Create Passkey", type="password")
    confirm_passkey = st.text_input("Confirm Passkey", type="password")
    if st.button("Store Data", use_container_width=True):
        if not data_id or not data or not passkey:
            st.error("⚠️ All fields are required")
        elif passkey != confirm_passkey:
            st.error("❌ Passkeys do not match")
        else:
            st.session_state.stored_data[data_id] = {
                "encrypted_text": encrypt_data(data),
                "passkey": hash_passkey(passkey)
            }
            st.success(f"✅ Data stored securely with ID: {data_id}")
            st.balloons()
    if st.button("⬅ Back", use_container_width=True):
        navigate('home')

def retrieve_data_page():
    render_header("🔎 Retrieve Encrypted Data")
    if st.session_state.failed_attempts > 0:
        st.warning(f"Failed attempts: {st.session_state.failed_attempts}/3")
    data_id = st.text_input("Enter Data ID")
    passkey = st.text_input("Enter Passkey", type="password")
    if st.button("Retrieve Data", use_container_width=True):
        if not data_id or not passkey:
            st.error("⚠️ Both fields are required")
        elif data_id not in st.session_state.stored_data:
            st.error("❌ Data ID not found")
            st.session_state.failed_attempts += 1
        else:
            stored_item = st.session_state.stored_data[data_id]
            if hash_passkey(passkey) == stored_item["passkey"]:
                st.success("✅ Data retrieved successfully!")
                st.code(decrypt_data(stored_item["encrypted_text"]))
                st.session_state.failed_attempts = 0
            else:
                st.error("❌ Incorrect passkey")
                st.session_state.failed_attempts += 1
        if st.session_state.failed_attempts >= 3:
            st.error("⚠️ Maximum attempts reached. Please reauthorize.")
            navigate('home')
    if st.button("⬅ Back", use_container_width=True):
        navigate('home')


def main():
    if st.session_state.page == 'home':
        home_page()
    elif st.session_state.page == 'insert':
        insert_data_page()
    elif st.session_state.page == 'retrieve':
        retrieve_data_page()

if __name__ == "__main__":
    main()
