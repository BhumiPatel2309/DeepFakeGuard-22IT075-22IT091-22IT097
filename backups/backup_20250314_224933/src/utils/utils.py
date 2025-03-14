import os
import sys
import re
import time

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import logger

# Email validation
def is_valid_email(email):
    """Validate email format"""
    logger.debug(f"Validating email: {email}")
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = bool(re.match(pattern, email))
    if not is_valid:
        logger.warning(f"Invalid email format: {email}")
    return is_valid

# Username validation
def is_valid_username(username):
    # Allow alphanumeric characters and underscores, 3-20 characters
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None

# Phone number validation
def is_valid_phone(phone):
    """Validate phone number format"""
    logger.debug(f"Validating phone number: {phone}")
    pattern = r'^\+?1?\d{9,15}$'
    is_valid = bool(re.match(pattern, phone))
    if not is_valid:
        logger.warning(f"Invalid phone number format: {phone}")
    return is_valid

# Generate a unique filename
def get_unique_filename(filename):
    base, ext = os.path.splitext(filename)
    timestamp = int(time.time())
    return f"{base}_{timestamp}{ext}"

# Get file extension
def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

# Format timestamp for display
def format_timestamp(timestamp):
    if not timestamp or timestamp == "Never":
        return "Never"
    # Add your timestamp formatting logic here
    return timestamp

# Format confidence score for display
def format_confidence(confidence):
    return f"{confidence:.2f}"