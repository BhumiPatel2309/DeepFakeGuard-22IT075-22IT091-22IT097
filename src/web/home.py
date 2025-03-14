import os
import sys
import streamlit as st

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import logger

def home_page():
    logger.info("Rendering home page")

    if 'page' not in st.session_state:
        st.session_state.page = "home"
        logger.debug("Initialized page session state to home")

    header_col1, header_col2 = st.columns([3, 1])  

    with header_col1:
        st.markdown("""
    <div style='font-size:40px; font-weight:bold; background-color: #f0f8ff;'>DeepFakeGuard</div>
    """, unsafe_allow_html=True)

    with header_col2:
        with st.container():
            button_col1, button_col2 = st.columns(2)
            with button_col1:
                if st.button("Login", key="login"):
                    st.session_state.page = "login"
                    logger.info("User clicked login button, redirecting to login page")
            with button_col2:
                if st.button("Register", key="register"):
                    st.session_state.page = "register"
                    logger.info("User clicked register button, redirecting to register page")
    
    # About section
    logger.debug("Rendering about section")
    st.markdown("""
    <div class="about-section">
        <p>Deepfake technology leverages artificial intelligence, specifically deep learning models, 
        to manipulate or generate highly realistic images and videos. These media alterations can 
        range from face-swapping in videos to entirely AI-generated content that mimics real people. 
        While deepfakes have innovative applications in entertainment and creative industries, they 
        also pose significant threats in areas such as misinformation, identity fraud, and cybercrime. 
        DeepFakeGuard is a state-of-the-art AI-powered deepfake detection platform designed to identify, 
        analyze, and verify the authenticity of media files. Our advanced deep learning models are trained 
        to detect subtle inconsistencies in pixel patterns, facial expressions, and motion dynamics that 
        indicate synthetic or manipulated content.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features section with cards
    logger.debug("Rendering features section")
    st.markdown("<h2 class='section-title'>Key Features</h2>", unsafe_allow_html=True)
    
    # First row of features
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown("""
    <div class="feature-card">
        <div class="card-icon">🔍</div>
        <h3>Image Analysis</h3>
        <p>Upload images to detect manipulation and deepfake content with precision.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with feat_col2:
        st.markdown("""
    <div class="feature-card">
        <div class="card-icon">🎬</div>
        <h3>Video Detection</h3>
        <p>Analyze videos frame by frame to identify deepfake manipulation.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with feat_col3:
        st.markdown("""
    <div class="feature-card">
        <div class="card-icon">📊</div>
        <h3>Detailed Reports</h3>
        <p>Get comprehensive analysis reports with confidence scores and visual highlights.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Second row of features
    feat_col4, feat_col5, feat_col6 = st.columns(3)
    
    with feat_col4:
        st.markdown("""
    <div class="feature-card">
        <div class="card-icon">⚙️</div>
        <h3>Customizable Models</h3>
        <p>Choose from multiple AI models or adjust detection thresholds for your needs.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with feat_col5:
        st.markdown("""
    <div class="feature-card">
        <div class="card-icon">📱</div>
        <h3>User Dashboard</h3>
        <p>Track your activity and manage your detection history from a personal dashboard.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with feat_col6:
        st.markdown("""
    <div class="feature-card">
        <div class="card-icon">🔒</div>
        <h3>Secure Platform</h3>
        <p>Your uploads are processed securely and privacy is maintained throughout.</p>
    </div>
    """, unsafe_allow_html=True)
    logger.debug("Home page rendering completed")

if __name__ == "__main__":
    home_page()
