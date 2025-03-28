import os
import sys
import streamlit as st
from src.utils.database import register_user
from src.utils.logger import logger
from src.utils.utils import is_valid_email, is_valid_phone, is_valid_username, is_valid_password

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def register_page():
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
            }
            
            .stButton > button {
                width: 100% !important;
                border-radius: 5px !important;
                height: 2.5rem !important;
                font-size: 0.9rem !important;
                font-weight: bold !important;
            }
            
            /* Column container to ensure buttons stay within the form */
            .stColumn > div {
                width: 100% !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Create three empty columns to center the form horizontally
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        # Register form title
        st.markdown('<h1>📝 Register for DeepFakeGuard</h1>', unsafe_allow_html=True)
        
        with st.form("register_form"):
            username = st.text_input("Username", key="reg-username", placeholder="Choose a username")
            email = st.text_input("Email", key="reg-email", placeholder="Enter your email")
            phone = st.text_input("Phone", key="reg-phone", placeholder="Enter your phone number")
            password = st.text_input("Password", key="reg-password", type="password", placeholder="Choose a password")
            confirm_password = st.text_input("Confirm Password", key="reg-confirm-password", type="password", placeholder="Confirm password")
            submit_button = st.form_submit_button("Register")
            
            if submit_button:
                if username and email and password and confirm_password:
                    if not is_valid_username(username):
                        logger.warning(f"Registration failed: Invalid username format - {username}")
                        st.error("Username must:\n- Be 3-20 characters long\n- Start with a letter\n- Contain only letters, numbers, and underscores\n- Not end with an underscore")
                    elif not is_valid_password(password):
                        logger.warning(f"Registration failed: Weak password for {username}")
                        st.error("Password must:\n- Be at least 8 characters long\n- Include at least one uppercase letter\n- Include at least one lowercase letter\n- Include at least one number\n- Include at least one special character (!@#$%^&*(),.?\":{}|<>)")
                    elif password != confirm_password:
                        logger.warning(f"Registration failed: Passwords do not match for {username}")
                        st.error("Passwords don't match")
                    elif not is_valid_email(email):
                        logger.warning(f"Registration failed: Invalid email format - {email}")
                        st.error("Please enter a valid email address")
                    elif not phone:
                        logger.warning(f"Registration failed: Missing phone number for {username}")
                        st.error("Phone number is required")
                    elif not is_valid_phone(phone):
                        logger.warning(f"Registration failed: Invalid phone format - {phone}")
                        st.error("Please enter a valid phone number (10-15 digits, optional country code)")
                    else:
                        success, message = register_user(username, email, password, phone)
                        if success:
                            logger.info(f"New user registered successfully: {username}")
                            st.success(message)
                            st.session_state.page = "login"
                            st.rerun()
                        else:
                            logger.warning(f"Registration failed for {username}: {message}")
                            st.error(message)
                else:
                    logger.warning("Registration attempt with missing required fields")
                    st.error("Please fill out all required fields")
        
        # Button container
        st.markdown('<div class="button-row">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("BACK TO LOGIN", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
        
        # Close button container
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    register_page()