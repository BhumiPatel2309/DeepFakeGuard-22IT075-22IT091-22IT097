import os
import sys
import streamlit as st

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.auth.login import login_page
from src.auth.register import register_page
from src.web.dashboard import dashboard
from src.web.home import home_page
from src.web.ui_components import set_page_style
from src.utils.database import init_db
from src.utils.logger import logger

# Create uploads directory if it doesn't exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')
    logger.info("Created uploads directory")

# Initialize database
init_db()
logger.info("Database initialized")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.page = "home"

# Set page config
st.set_page_config(
    page_title="DeepFakeGuard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    main()