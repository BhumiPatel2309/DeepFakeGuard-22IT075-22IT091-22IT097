import streamlit as st
from requests_oauthlib import OAuth2Session
import os
from .oauth_config import *
from src.utils.database import register_user, login_user
from src.utils.logger import logger
from src.web.dashboard import dashboard

def init_google_oauth():
    """Initialize Google OAuth session"""
    if 'oauth_state' not in st.session_state:
        st.session_state.oauth_state = None
    
    return OAuth2Session(
        GOOGLE_CLIENT_ID,
        scope=GOOGLE_SCOPE,
        redirect_uri=GOOGLE_REDIRECT_URI,
        state=st.session_state.oauth_state
    )

def get_google_auth_url():
    """Get Google authorization URL"""
    try:
        google = init_google_oauth()
        authorization_url, state = google.authorization_url(
            GOOGLE_AUTH_URL,
            access_type="offline",
            prompt="select_account",
            state=st.session_state.oauth_state
        )
        st.session_state.oauth_state = state
        return authorization_url
    except Exception as e:
        logger.error(f"Error generating auth URL: {str(e)}")
        return None

def handle_oauth_callback():
    """Handle OAuth callback via Streamlit query parameters"""
    try:
        # Get query parameters
        query_params = st.experimental_get_query_params()
        
        # Check for error in query parameters
        if 'error' in query_params:
            error = query_params['error'][0]
            logger.error(f"OAuth error: {error}")
            return False, f"Authentication failed: {error}"
            
        # Verify state to prevent CSRF
        if 'state' in query_params:
            received_state = query_params['state'][0]
            if received_state != st.session_state.oauth_state:
                logger.error("OAuth state mismatch")
                return False, "Invalid authentication state"
        
        # Get authorization code
        if 'code' not in query_params:
            logger.error("No authorization code received")
            return False, "No authorization code received"
            
        code = query_params['code'][0]
        
        # Exchange code for token
        google = init_google_oauth()
        token = google.fetch_token(
            GOOGLE_TOKEN_URL,
            client_secret=GOOGLE_CLIENT_SECRET,
            code=code
        )
        
        # Get user info
        user_info = google.get(GOOGLE_USERINFO_URL).json()
        
        # Extract user details
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0])
        
        # Check if user exists, if not register them
        success, message, user_data = login_user(email, None, is_google_auth=True)
        
        if not success:
            # Register new user with Google credentials
            username = email.split('@')[0]
            success, message = register_user(
                username=username,
                email=email,
                password=None,  # No password for Google auth
                phone=None,     # Phone can be updated later
                is_google_auth=True
            )
            
            if success:
                success, message, user_data = login_user(email, None, is_google_auth=True)
        
        if success:
            # Store user info in session state
            st.session_state.logged_in = True
            dashboard()
            st.session_state.username = user_data["username"]
            st.session_state.email = user_data["email"]
            st.session_state.is_google_auth = True
            
            # Set query parameters to navigate to dashboard instead of clearing them
            st.experimental_set_query_params(page="dashboard")
            
            logger.info(f"Google SSO successful for user: {email}")
            return True, "Successfully logged in with Google"
            
        else:
            logger.error(f"Google SSO failed for user: {email}")
            return False, "Failed to authenticate with Google"
            
    except Exception as e:
        logger.error(f"Error in OAuth callback: {str(e)}")
        return False, f"Authentication failed: {str(e)}"
