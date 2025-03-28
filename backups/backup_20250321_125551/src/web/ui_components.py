import os
import sys
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import logger

# App styling
def set_page_style():
    logger.debug("Setting page style")
    st.markdown("""
        <style>
            /* Override Streamlit's default theme */
            .stApp {
            background-color: #ffffff !important;
        }
            
            /* Remove all default Streamlit elements */
            header {display: none !important;}
            footer {display: none !important;}
            #MainMenu {display: none !important;}
            .stDeployButton {display: none !important;}
            #stDecoration {display: none !important;}
            div[data-testid="stToolbar"] {display: none !important;}
            div[data-testid="stHeader"] {display: none !important;}
            section[data-testid="stSidebar"] {display: none !important;}
            
            /* Container styling */
            .block-container {
                padding: 0 !important;
                max-width: 100% !important;
                margin: 0 auto !important;
            }
            
            /* Authentication form styling */
            .form-header {
                color: #1a1a1a !important;
                text-align: center;
                font-size: 32px !important;
                font-weight: 700 !important;
                margin-bottom: 2.5rem !important;
                padding: 0 !important;
                line-height: 1.4 !important;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
            }
            
            .form-header * {
                color: #1a1a1a !important;
            }
            
            .form-header span {
                font-size: 36px;
            }
            
            /* Form group styling */
            .form-group {
                margin-bottom: 1.5rem;
            }
            
            /* Label styling */
            .form-label {
                display: block !important;
                font-size: 30px !important;
                font-weight: 600 !important;
                color: #1a1a1a !important;
                margin-bottom: 8px !important;
                text-transform: uppercase !important;
                letter-spacing: 0.05em !important;
            }
            
            /* Input styling */
            .stTextInput > div {
                margin-bottom: 0 !important;
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
                transition: all 0.2s ease !important;
            }
            
            .stTextInput > div > div > input:focus {
                box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.3) !important;
                border-color: #4299e1 !important;
            }
            
            /* Placeholder text */
            .stTextInput > div > div > input::placeholder {
                color: #a0aec0 !important;
                font-size: 15px !important;
            }
            
            /* Button group styling */
            .button-group {
                margin-top: 2.5rem;
                display: flex;
                gap: 1rem;
            }
            
            /* Button styling */
            .stButton > button {
                width: 100% !important;
                padding: 12px 24px !important;
                font-size: 15px !important;
                font-weight: 600 !important;
                border-radius: 8px !important;
                cursor: pointer !important;
                transition: all 0.2s ease !important;
                text-transform: uppercase !important;
                letter-spacing: 0.05em !important;
                background-color: blue;
            }
            
            /* Primary button (Login/Register) */
            .stButton:first-child > button {
                background: linear-gradient(135deg, #4299e1, #2b6cb0) !important;
                color: white !important;
                border: none !important;
            }
            
            .stButton:first-child > button:hover {
                background: linear-gradient(135deg, #2b6cb0, #2c5282) !important;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3) !important;
            }
            
            /* Secondary button (Register/Login Instead) */
            .stButton:last-child > button {
                background: white !important;
                color: #4299e1 !important;
                border: 2px solid #4299e1 !important;
            }
            
            .stButton:last-child > button:hover {
                background: #ebf8ff !important;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(66, 153, 225, 0.15) !important;
            }
            
            /* Alert styling */
            .stAlert {
                padding: 1rem !important;
                border-radius: 8px !important;
                margin: 1rem 0 !important;
                border: none !important;
            }
            
            /* Success message */
            .element-container:has(div.stAlert) {
                margin-top: 1rem !important;
            }
            
            /* Results display */
            .result {
                padding: 1rem;
                border-radius: 8px;
                font-weight: bold;
                font-size: 1.2rem;
                text-align: center;
            }
            
            .result-fake {
                background-color: #FED7D7;
                color: #9B2C2C;
                border-left: 4px solid #E53E3E;
            }
            
            .result-real {
                background-color: #C6F6D5;
                color: #276749;
                border-left: 4px solid #48BB78;
            }
            
            /* Home page specific styling */
            /* Background styling */
            body {
                background-color: #F0F8FF !important;
            }
            
            .stApp {
                background-color: #F0F8FF !important;
            }
            
            /* Remove default padding and margins */
            .block-container {
                padding-top: 0 !important;
                padding-left: 0 !important;
                padding-right: 0 !important;
                max-width: 100% !important;
            }
            
            /* Hide Streamlit branding */
            #MainMenu, footer, header {
                visibility: hidden;
            }
            
            /* Navigation bar styling - IMPROVED */
            .navbar {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background-color: #1a4587;  /* This is the blue color you're already using */
                    padding: 2rem 2rem;
                    color: white;
                    width: 100%;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            }

            .navbar-brand {
    font-size: 40px;
    font-weight: bold;
    color: white;
    margin: 0;
    padding: 0;
}

            .navbar-buttons {
                display: flex;
                gap: 1rem;
            }

            .navbar-button {
                background-color: transparent;
                color: white;
                border: 1px solid white;
                padding: 0.5rem 1.5rem;
                border-radius: 5px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .navbar-button:hover {
                background-color: white;
                color: #1a4587;
            }

            .navbar-button.login {
                background-color: white;
                color: #1a4587;
            }

            .navbar-button.login:hover {
                background-color: #f0f0f0;
            }

            .navbar-button.register {
                background-color: transparent;
            }

            /* Content container */
            .content-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            /* About section styling */
            .about-section {
            max-width: 60%;
            margin: 3rem auto;
            padding: 3rem 0;
            line-height: 1.6;
            border-bottom: 1px solid #e0e0e0;
            }

            .about-section p {
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            font-family: 'Georgia', Times, serif;
            color: #232323;
            text-align: justify;
            }
            
            /* Section title styling */
            .section-title {
                text-align: center;
                margin: 2rem 0;
                font-size: 2rem;
                font-weight: 700;
                color: #1a4587;
            }
            
            /* Feature card styling */
            .feature-card {
                background-color: white;
                border-radius: 8px;
                padding: 2rem 4rem;
                height: 100%;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: all 0.3s;
                margin-bottom: 1.5rem;
                margin-left: 2rem;
                margin-right: 2rem;
            }
            
            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 15px rgba(0,0,0,0.1);
            }
            
            .card-icon {
                font-size: 2.5rem;
                margin-bottom: 1rem;
                text-align: center;
            }
            
            .feature-card h3 {
                margin-bottom: 1rem;
                text-align: center;
                font-size: 1.4rem;
                color: #1a4587;
            }
            
            .feature-card p {
                text-align: center;
                font-size: 1rem;
                line-height: 1.5;
                color: #4a5568;
            }
            
            /* Mobile responsiveness */
            @media (max-width: 768px) {
                .navbar {
                    flex-direction: column;
                    padding: 1rem;
                }
                
                .navbar-brand {
                    margin-bottom: 1rem;
                }
                
                .navbar-buttons {
                    width: 100%;
                    justify-content: center;
                }
                
                .content-container {
                    padding: 1rem;
                }
            }
        </style>
    """, unsafe_allow_html=True)
    logger.debug("Page style applied successfully")

# Function to display a styled card
def styled_card(title, content, icon="📊"):
    logger.debug(f"Rendering styled card: {title}")
    st.markdown(f"""
        <div class="feature-card">
            <div class="card-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{content}</p>
        </div>
    """, unsafe_allow_html=True)

# Function to display user stats with modified stats display
def display_user_stats(stats):
    logger.debug("Displaying user statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Images Analyzed", value=stats["images_analyzed"])
    with col2:
        st.metric(label="Videos Analyzed", value=stats["videos_analyzed"])
    with col3:
        st.metric(label="Deepfakes Detected", value=stats["deepfakes_detected"])
    with col4:
        st.metric(label="Last Analysis", value=stats["last_analysis"])

# Function to create a detection results chart
def create_detection_chart(real_count, fake_count):
    logger.debug("Creating detection chart")
    labels = 'Real', 'Fake'
    sizes = [real_count, fake_count]
    explode = (0, 0.1)
    
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
           shadow=True, startangle=90, colors=['#6eb52f', '#ff4b4b'])
    ax.axis('equal')
    
    return fig

# Function to display activity table
def display_activity_table(activity_data):
    logger.debug(f"Displaying activity table with {len(activity_data)} entries")
    if not activity_data:
        st.info("No activity recorded yet.")
        return
    
    formatted_data = []
    for item in activity_data:
        try:
            # Safely convert probability to float
            if isinstance(item['probability'], bytes):
                # Try to convert bytes to string then to float
                prob_str = item['probability'].decode('utf-8', errors='replace')
                prob = float(prob_str)
            else:
                # Try direct conversion
                prob = float(item['probability'])
            
            confidence = f"{prob:.2f}"
        except (ValueError, UnicodeDecodeError, TypeError):
            # If conversion fails, use a placeholder
            confidence = "N/A"
        
        formatted_data.append({
            'Time': item['timestamp'],
            'File Type': item['file_type'],
            'Result': item['result'],
            'Confidence': confidence
        })
    
    st.table(formatted_data)

# Show loading spinner
def loading_spinner(message="Processing..."):
    logger.debug("Showing loading spinner")
    with st.spinner(message):
        time.sleep(2)  # Simulate loading