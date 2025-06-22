import streamlit as st
from datetime import datetime
import base64
import warnings
import requests
from io import BytesIO

# Suppress warnings
warnings.filterwarnings("ignore")

# --- Hardcoded credentials ---
USERNAME = "Compiler Design"
PASSWORD = "cse331"

# GitHub repository information
GITHUB_USER = "azaz6216"
GITHUB_REPO = "cousrecontent"
GITHUB_BRANCH = "main"
CONTENT_PATH = "my-course/content"

# --- Initialize session state ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_slide' not in st.session_state:
    st.session_state['current_slide'] = 0

# --- Utility Functions ---
def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")
    show_footer()

def logout():
    st.session_state['logged_in'] = False
    st.rerun()

def show_navbar():
    with st.sidebar:
        st.title("Course Content Helper")
        st.write("---")
        nav = st.radio(
            "Navigate",
            ("Home", "Course Content", "Contact"),
            label_visibility="collapsed"
        )
        st.write("---")
        if st.button("Logout", use_container_width=True):
            logout()
    return nav

def show_footer():
    st.markdown("---")
    current_year = datetime.now().year
    footer = f"""
    <div style="text-align: center; padding: 10px; color: gray; font-size: 14px;">
        <p>© {current_year} Course Content Helper. All rights reserved.</p>
        <p>Version 1.0.0 | <a href="#" style="color: gray;">Privacy Policy</a> | <a href="#" style="color: gray;">Terms of Service</a></p>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)

def show_home():
    st.markdown(
        """
        <div style="text-align:center; padding: 20px;">
            <h1>🏠 Welcome to the Course Content Helper</h1>
            <img src="https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80" alt="Home Image" style="width:70%; border-radius:15px;"/>
            <p style="font-size:18px; margin-top:20px;">
                Use the navigation to browse course materials and learn at your own pace.<br>
                Happy Learning! 📚
            </p>
        </div>
        """, unsafe_allow_html=True
    )
    show_footer()

def get_github_files():
    """Fetch list of files from GitHub repository"""
    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{CONTENT_PATH}?ref={GITHUB_BRANCH}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        files = [item['name'] for item in response.json() if item['type'] == 'file' and 
                item['name'].lower().endswith(('.pdf', '.pptx', '.docx'))]
        return files
    except Exception as e:
        st.error(f"Error fetching files from GitHub: {str(e)}")
        return []

def download_github_file(filename):
    """Download a file from GitHub"""
    raw_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{CONTENT_PATH}/{filename}"
    try:
        response = requests.get(raw_url)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        st.error(f"Error downloading file: {str(e)}")
        return None

def display_pdf(file_bytes):
    """Display PDF from bytes"""
    base64_pdf = base64.b64encode(file_bytes.getvalue()).decode('utf-8')
    pdf_display = f'''
    <object data="data:application/pdf;base64,{base64_pdf}" 
            type="application/pdf" 
            width="120%" 
            height="1000px">
    </object>
    '''
    st.markdown(pdf_display, unsafe_allow_html=True)

def show_course_content():
    st.title("📁 Course Materials")
    
    files = get_github_files()
    
    if not files:
        st.info("No supported files found (PDF, PPTX, DOCX) in the GitHub repository.")
        show_footer()
        return

    selected_file = st.selectbox("Select a file to view or download", files)
    
    tab1, tab2 = st.tabs(["View", "Download"])
    
    with tab1:
        st.subheader(f"Viewing: {selected_file}")
        
        try:
            file_bytes = download_github_file(selected_file)
            if file_bytes:
                if selected_file.lower().endswith(".pdf"):
                    display_pdf(file_bytes)
                else:
                    st.warning("This file type is not supported for preview")
        except Exception as e:
            st.error(f"Error displaying file: {str(e)}")

    with tab2:
        st.subheader("Download Options")
        file_bytes = download_github_file(selected_file)
        if file_bytes:
            st.download_button(
                label="⬇️ Download File",
                data=file_bytes,
                file_name=selected_file,
                mime="application/octet-stream",
                use_container_width=True
            )
    
    show_footer()

def show_contact():
    st.title("📬 Contact Us")
    st.markdown(
        """
        <div style="font-size:18px; line-height:1.6;">
            <p><strong>Name:</strong> Azaz Ahamed</p>
            <p><strong>Email:</strong> ahamed15-6216@s.diu.edu.bd</p>
            <p><strong>Phone:</strong> +880 1931 707075</p>
            <p><strong>Address:</strong> Daffodil International University, Dhaka, Bangladesh</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    show_footer()

# --- Main App ---
if not st.session_state['logged_in']:
    login()
else:
    page = show_navbar()

    if page == "Home":
        show_home()
    elif page == "Course Content":
        show_course_content()
    elif page == "Contact":
        show_contact()