import streamlit as st
from PIL import Image
# from api import process_image, process_video
from api import process_image
# Custom Streamlit UI
st.set_page_config(page_title="Deepfake Detector", page_icon="🔍", layout="wide")

st.markdown("""
    <style>
        .result {
            font-size: 20px;
            font-weight: bold;
        }
        .result-fake {
            color: #ff4b4b;
        }
        .result-real {
            color: #6eb52f;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar for Settings
st.sidebar.title("🔧 Settings")
# file_type = st.sidebar.radio("Select file type:", ["Image", "Video"])
file_type = "Image"
model = st.sidebar.selectbox("Select Model", ["EfficientNetB4", "EfficientNetB4ST", "EfficientNetAutoAttB4", "EfficientNetAutoAttB4ST"])
dataset = st.sidebar.radio("Select Dataset", ["DFDC", "FFPP"])
threshold = 0.5 
# threshold = st.sidebar.slider("Select Threshold", 0.0, 1.0, 0.5)
# frames = st.sidebar.slider("Select Frames", 0, 100, 50) if file_type == "Video" else None

# Main Section
st.title("🔍 Deepfake Detector App")
st.write("Upload an image or video to detect deepfakes.")

# File Upload
# uploaded_file = st.file_uploader(f"Choose a {file_type.lower()}...", type=["jpg", "jpeg", "png", "mp4"])
uploaded_file = st.file_uploader(f"Choose an image...", type=["jpg", "jpeg", "png"]) 

if uploaded_file:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if file_type == "Image":
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", width=250)
            except:
                st.error("Error: Invalid Filetype")
        else:
            st.video(uploaded_file)
    
    with col2:
        if st.button("🚀 Check for Deepfake"):
            with st.spinner("Analyzing... Please wait ⏳"):
                if file_type == "Image":
                    result, pred = process_image(uploaded_file, model, dataset, threshold)
                else:
                    video_path = f"uploads/{uploaded_file.name}"
                    with open(video_path, "wb") as f:
                        f.write(uploaded_file.read())
                    result, pred = process_video(video_path, model, dataset, threshold, frames)
                
                color_class = "result-fake" if result == "fake" else "result-real"
                # st.markdown(f'<p class="result {color_class}">The given {file_type} is: {result.upper()} (Probability: {pred:.2f})</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="result {color_class}">The given {file_type} is: {result.upper()} ', unsafe_allow_html=True)
else:
    st.info("📂 Please upload a file to proceed.")

# Additional Information
st.divider()
