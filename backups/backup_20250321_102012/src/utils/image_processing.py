import os
import tempfile
import random
from PIL import Image
import numpy as np
from src.utils.logger import logger

def process_image(uploaded_file, model_name="EfficientNetB4", dataset="DFDC", threshold=0.5):
    """
    Process an uploaded image for deepfake detection
    
    Args:
        uploaded_file: Streamlit uploaded file object
        model_name (str): Name of the model to use for detection
        dataset (str): Dataset used for training the model
        threshold (float): Confidence threshold for classification
        
    Returns:
        tuple: (prediction_result, confidence_score)
    """
    try:
        # Create a temporary file to save the uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        # Load and preprocess image
        image = Image.open(tmp_path)
        
        # For testing: Randomly classify as real or fake
        is_fake = random.random() > threshold  # Use threshold as probability boundary
        confidence = random.uniform(0.7, 0.99)  # Random confidence between 0.7 and 0.99
        
        result = "fake" if is_fake else "real"
        logger.info(f"Image classified as {result} with confidence {confidence:.2f}")
        
        return result, confidence
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return None, None
    finally:
        # Clean up the temporary file
        if 'tmp_path' in locals():
            try:
                os.remove(tmp_path)
            except:
                pass
