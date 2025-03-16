import os
import sys
import streamlit as st
import ssl


st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add the project root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.auth.login import login_page
from src.auth.register import register_page
from src.web.dashboard import dashboard
from src.web.home import home_page
from src.web.ui_components import set_page_style
from src.utils.database import init_db
from src.utils.logger import logger
from src.backup_manager import BackupManager

# Create uploads directory if it doesn't exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Initialize database
init_db()

# Initialize backup manager
backup_manager = BackupManager()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.page = "home"

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    logger.info("Application startup")
    set_page_style()
    
    # Direct to appropriate page
    if st.session_state.logged_in:
        logger.info(f"User {st.session_state.username} accessing dashboard")
        dashboard()
    else:
        if st.session_state.page == "home":
            logger.info("Rendering home page")
            home_page()
        elif st.session_state.page == "login":
            logger.info("Rendering login page")
            login_page()
        elif st.session_state.page == "register":
            logger.info("Rendering register page")
            register_page()

if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("certs/cert.pem", "certs/key.pem")
    main()