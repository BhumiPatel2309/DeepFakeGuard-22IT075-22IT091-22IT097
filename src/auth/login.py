import os
import sys
import streamlit as st
from src.utils.database import login_user
from src.utils.logger import logger
from src.utils.utils import is_valid_username, is_valid_password
from .google_auth import get_google_auth_url, handle_oauth_callback

# Add the project root directory to Python path
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(current_dir)

# Add CSS for central container
st.markdown("""
    <style>
        /* App styling */
        .stApp {
            background-color: #F0F8FF !important;
        }
        
        /* Remove default padding and center form */
        .block-container {
            padding-top: 6rem !important;
            max-width: 100% !important;
        }
        
        h1 {
            text-align: center;
            margin-bottom: 2rem;
            font-size: 1.8rem;
        }
        
        /* Override Streamlit's default text input styling */
        .stTextInput {
            max-width: 100% !important;
        }
        
        .stTextInput > div {
            margin-bottom: 0.8rem !important;
            max-width: 100% !important;
        }
        
        .stTextInput > div > div > input {
            font-size: 16px !important;
            padding: 12px 16px !important;
            border: 2px solid #e2e8f0 !important;
            border-radius: 8px !important;
            background-color: #ffffff !important;
            color: #2d3748 !important;
            height: auto !important;
            width: 100% !important;
            max-width: 100% !important;
            transition: all 0.2s ease !important;
            box-sizing: border-box !important;
        }
        
        .stTextInput > div > div > input:focus {
            box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.3) !important;
            border-color: #4299e1 !important;
        }
        
        /* Button container styling */
        .button-row {
            display: flex;
            gap: 0.5rem;
            margin-top: 1.5rem;
        }
        
        .stButton {
            width: 100%;
            align-items: center !important;
        }
        
        .stButton > button {
            width: 100% !important;
            border-radius: 5px !important;
            height: 2.5rem !important;
            font-size: 0.9rem !important;
            font-weight: bold !important;
            align-items: center !important;
        }
        
        /* Column container to ensure buttons stay within the form */
        .stColumn > div {
            width: 100% !important;
        }
        
        .google-btn {
            background-color: #4285F4;
            color: white;
            padding: 12px 16px;
            border-radius: 4px;
            border: none;
            font-size: 16px;
            font-weight: 500;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            cursor: pointer;
            margin-bottom: 20px;
        }
        
        .google-btn:hover {
            background-color: #357ABD;
        }
    </style>
""", unsafe_allow_html=True)

def login_page():
    # Handle Google OAuth callback if there are query parameters
    query_params = st.experimental_get_query_params()
    if query_params:
        success, message = handle_oauth_callback()
        if success:
            # Clear query parameters and trigger rerun to show dashboard
            st.experimental_set_query_params()
            st.success(message)
            # Force rerun to trigger main routing logic which will show dashboard
        else:
            st.error(message)
            # Clear query parameters to prevent reprocessing
            st.experimental_set_query_params()
            
    # Create three empty columns to center the form horizontally
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        # Login form title
        st.markdown('<h1>🔐 Login to DeepFakeGuard</h1>', unsafe_allow_html=True)
        
        # Google Sign-In button with custom styling
        if st.button("🔒 Sign in with Google", key="google_signin", help="Click to sign in with your Google account"):
            auth_url = get_google_auth_url()
            if auth_url:
                st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)
            else:
                st.error("Failed to generate Google authentication URL")
        
        st.markdown("<p style='text-align: center; color: #666; margin: 20px 0;'>- OR -</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", key="username-input", placeholder="Enter your username")
            password = st.text_input("Password", key="password-input", type="password", placeholder="Enter your password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if username and password:
                    if not is_valid_username(username):
                        logger.warning(f"Login failed: Invalid username format - {username}")
                        st.error("Invalid username format. Please check your username.")
                    else:
                        success, message, user_info = login_user(username, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.email = user_info["email"]
                            st.session_state.phone = user_info["phone"]
                            st.session_state.is_admin = user_info["is_admin"]
                            logger.info(f"User {username} logged in successfully")
                            st.success(message)

                        else:
                            logger.warning(f"Login failed for user {username}: {message}")
                            st.error("Invalid username or password")
                else:
                    logger.warning("Login attempt with empty username or password")
                    st.error("Please fill in all fields")
        
        # Button container
        st.markdown('<div class="button-row">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("REGISTER", use_container_width=True):
                st.session_state.page = "register"
                
        with col2:
            pass
        
        with col3:
            if st.button("HOME", use_container_width=True):
                st.session_state.page = "home"
        
        # Close button container
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Close login container
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    login_page()