import os
import sys
import streamlit as st
from PIL import Image

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.database import log_activity, get_user_stats, get_recent_activity
from src.utils.logger import logger
from src.web.ui_components import styled_card, display_user_stats, create_detection_chart, display_activity_table

def dashboard():
    logger.info(f"Loading dashboard for user: {st.session_state.username}")
    
    # Custom CSS for better layout and spacing
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        margin-bottom: 20px;
        padding-top: 10px;
        font-size: 32px;
    }
    .sidebar-header {
        font-size: 18px; 
        font-weight: bold;
        margin-bottom: 15px;
        border-bottom: 1px solid #dee2e6;
        padding-bottom: 8px;
    }
    .user-info {
        margin-bottom: 15px;
        font-size: 14px;
    }
    .tabs-container {
        display: flex;
        border-bottom: 1px solid #dee2e6;
        margin-bottom: 20px;
    }
    .tab-button {
        background-color: #f0f2f6;
        border: none;
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
        font-weight: 500;
        cursor: pointer;
        margin-right: 5px;
    }
    .tab-selected {
        background-color: #1f77b4;
        color: white;
    }
    .content-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .tips-container {
        background-color: #f0f8ff;
        border-radius: 8px;
        padding: 5px;
        margin-bottom: 15px;
    }
    .tip-item {
        padding: 6px;
        border-bottom: 1px dashed #e6e6e6;
    }
    .tip-item:last-child {
        border-bottom: none;
    }
    .result {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        margin: 10px 0;
    }
    .result-fake {background-color: #ff6b6b; color: white;}
    .result-real {background-color: #4CAF50; color: white;}
    .file-uploader {
        border: 2px dashed #dcdcdc;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        margin: 15px 0;
    }
    .radio-container {
        margin: 12px 0;
    }
    .slider-container {
        margin: 15px 0;
    }
    .logout-button {
        width: 100%;
        margin-top: 10px;
        background-color: #f44336;
        color: white;
        border: none;
        padding: 8px 0;
        border-radius: 5px;
        cursor: pointer;
    }
    .check-button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 5px;
        cursor: pointer;
        font-weight: 500;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main layout with better proportions
    st.markdown("<h1 class='main-header'>🔍 Deepfake Detector Dashboard</h1>", unsafe_allow_html=True)
    
    # Use more balanced column proportions
    col1, col2, col3 = st.columns([1.2, 2.5, 1])

    # LEFT SIDEBAR - Better organized with sections
    with col1:
        # User info section
        st.markdown("<div class='sidebar-container'>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-header'>👤 User Profile</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='user-info'>Logged in as: <b>{st.session_state.username}</b></div>", unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn", type="primary"):
            logger.info(f"User {st.session_state.username} logged out")
            st.session_state.logged_in = False
            st.session_state.username = None
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Settings section with better spacing
        st.markdown("<div class='sidebar-container'>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-header'>🔧 Settings</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='radio-container'>", unsafe_allow_html=True)
        st.write("File Type:")
        file_type = st.radio("", ["Image", "Video"], horizontal=True, label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='select-container'>", unsafe_allow_html=True)
        st.write("Model:")
        model = st.selectbox("", 
                           ["EfficientNetB4", "EfficientNetB4ST", 
                            "EfficientNetAutoAttB4", "EfficientNetAutoAttB4ST"],
                            label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='radio-container'>", unsafe_allow_html=True)
        st.write("Dataset:")
        dataset = st.radio("", ["DFDC", "FFPP"], horizontal=True, label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='slider-container'>", unsafe_allow_html=True)
        st.write("Detection Threshold:")
        threshold = st.slider("", 0.0, 1.0, 0.5, step=0.05, label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if file_type == "Video":
            st.markdown("<div class='slider-container'>", unsafe_allow_html=True)
            st.write("Number of Frames:")
            frames = st.slider("", 10, 100, 50, step=5, label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            frames = None
        st.markdown("</div>", unsafe_allow_html=True)
    
    # MAIN CONTENT - Better spaced tabs and content areas
    with col2:
        # Custom tabs with better styling
        tab1, tab2 = st.columns(2)
        
        with tab1:
            detector_tab_class = "tab-button tab-selected" if st.session_state.get('active_tab', 'detector') == "detector" else "tab-button"
            if st.button("DETECTOR", key="detector_tab", use_container_width=True):
                st.session_state.active_tab = "detector"
        
        with tab2:
            analytics_tab_class = "tab-button tab-selected" if st.session_state.get('active_tab', 'analytics') == "analytics" else "tab-button"
            if st.button("ANALYTICS", key="analytics_tab", use_container_width=True):
                st.session_state.active_tab = "analytics"
        
        # Initialize the active tab if not set
        if 'active_tab' not in st.session_state:
            st.session_state.active_tab = "detector"
        
        # DETECTOR TAB
        if st.session_state.active_tab == "detector":
            st.markdown(f"### Welcome, {st.session_state.username}!")
            st.write("Upload an image or video to detect deepfakes.")
            
            # Improved file uploader with visual cues
            uploaded_file = st.file_uploader(f"Choose a {file_type.lower()}...", 
                                           type=["jpg", "jpeg", "png"] if file_type == "Image" else ["mp4"])
            
            if uploaded_file:
                preview_col, result_col = st.columns([1, 1])
                
                with preview_col:
                    if file_type == "Image":
                        try:
                            image = Image.open(uploaded_file)
                            st.image(image, caption="Uploaded Image", width=250)
                        except:
                            st.error("Error: Invalid Filetype")
                    else:
                        st.video(uploaded_file)
                
                with result_col:
                    st.markdown("<div style='padding-top:25px;'></div>", unsafe_allow_html=True)
                    if st.button("🚀 Check for Deepfake", use_container_width=True):
                        with st.spinner("Analyzing... Please wait ⏳"):
                            if file_type == "Image":
                                result, pred = process_image(uploaded_file, model, dataset, threshold)
                            else:
                                video_path = f"uploads/{uploaded_file.name}"
                                with open(video_path, "wb") as f:
                                    f.write(uploaded_file.read())
                                result, pred = process_video(video_path, model, dataset, threshold, frames)
                            
                            # Log the activity
                            log_activity(st.session_state.username, file_type, result, pred)
                            
                            # Ensure pred is properly handled for display
                            try:
                                pred_display = float(pred) if not isinstance(pred, bytes) else float(pred.decode('utf-8', errors='replace'))
                            except (ValueError, TypeError, UnicodeDecodeError):
                                pred_display = 0.0
                            
                            color_class = "result-fake" if result == "fake" else "result-real"
                            st.markdown(f'<p class="result {color_class}">The given {file_type} is: {result.upper()}<br>(Probability: {pred_display:.2f})</p>', unsafe_allow_html=True)
            else:
                st.markdown("📂 Drag and drop your file here or click Browse files")
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top:15px; padding-top:15px; border-top:1px solid #e6e6e6;'>", unsafe_allow_html=True)
            st.write("This application uses deep learning models to detect deepfake content.")
            st.write("For best results, use the recommended parameters:")
            st.write("- Model: **EfficientNetAutoAttB4**")
            st.write("- Dataset: **DFDC**")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # ANALYTICS TAB
        else:            
            # Get user stats and activity
            user_stats = get_user_stats(st.session_state.username)
            recent_activity = get_recent_activity(st.session_state.username)
            
            # Calculate last analysis time
            if recent_activity:
                user_stats['last_analysis'] = recent_activity[0]['timestamp']
            else:
                user_stats['last_analysis'] = "Never"
            
            # Display statistics in a more visually organized way
            st.markdown("### Your Statistics")
            stat_col1, stat_col2 = st.columns(2)
            
            with stat_col1:
                st.metric("Images Analyzed", user_stats.get('images_analyzed', 0))
                st.metric("Real Media Detected", 
                          (user_stats.get('images_analyzed', 0) + user_stats.get('videos_analyzed', 0)) - 
                          user_stats.get('deepfakes_detected', 0))
            
            with stat_col2:
                st.metric("Videos Analyzed", user_stats.get('videos_analyzed', 0))
                st.metric("Deepfakes Detected", user_stats.get('deepfakes_detected', 0))
            
            st.markdown("### Detection Results")
            real_count = user_stats.get('images_analyzed', 0) + user_stats.get('videos_analyzed', 0) - user_stats.get('deepfakes_detected', 0)
            fake_count = user_stats.get('deepfakes_detected', 0)
            
            chart_col1, chart_col2 = st.columns([2, 1])
            
            with chart_col1:
                if real_count > 0 or fake_count > 0:
                    st.pyplot(create_detection_chart(real_count, fake_count))
                else:
                    st.info("No detection data available yet.")
            
            with chart_col2:
                st.markdown("<div style='padding:20px;'>", unsafe_allow_html=True)
                st.metric("Detection Rate", f"{100 * fake_count / (real_count + fake_count):.1f}%" if (real_count + fake_count) > 0 else "N/A")
                st.metric("Last Analysis", user_stats.get('last_analysis', "Never"))
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("### Recent Activity")
            display_activity_table(recent_activity)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # RIGHT COLUMN - Tips section with better formatting
    with col3:
        st.markdown("<div class='sidebar-header'>💡 Tips & Best Practices</div>", unsafe_allow_html=True)
        st.markdown("<div class='tip-item'>", unsafe_allow_html=True)
        st.info("Upload high-resolution images (at least 720p) for better detection accuracy.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='tip-item'>", unsafe_allow_html=True)
        st.info("For videos, 50 frames is a good balance between accuracy and processing time.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='tip-item'>", unsafe_allow_html=True)
        st.info("EfficientNetAutoAttB4 with DFDC dataset typically provides the best results for most cases.")
        st.markdown("</div>", unsafe_allow_html=True)