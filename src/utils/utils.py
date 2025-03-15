import os
import sys
import re
import time

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import logger

# Email validation
def is_valid_email(email):
    """Validate email format
    Rules:
    - Standard email format (user@domain.tld)
    - Domain must have valid TLD
    - No consecutive dots
    - Length limits on parts
    """
    logger.debug(f"Validating email: {email}")
    if len(email) > 254:  # Maximum total length
        logger.warning(f"Email too long: {email}")
        return False
        
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]{0,63}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        logger.warning(f"Invalid email format: {email}")
        return False
        
    # Check for consecutive dots
    if '..' in email:
        logger.warning(f"Invalid email - consecutive dots: {email}")
        return False
        
    # Validate local part and domain lengths
    local, domain = email.split('@')
    if len(local) > 64 or len(domain) > 255:
        logger.warning(f"Email part too long: {email}")
        return False
        
    return True

# Username validation
def is_valid_username(username):
    """Validate username format
    Rules:
    - 3-20 characters long
    - Can contain letters, numbers, and underscores
    - Must start with a letter
    - Cannot end with an underscore
    """
    logger.debug(f"Validating username: {username}")
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]{1,18}[a-zA-Z0-9]$'
    is_valid = bool(re.match(pattern, username))
    if not is_valid:
        logger.warning(f"Invalid username format: {username}")
    return is_valid

# Password validation
def is_valid_password(password):
    """Validate password strength
    Rules:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    logger.debug("Validating password strength")
    if len(password) < 8:
        logger.warning("Password too short")
        return False
    
    patterns = [
        r'[A-Z]',  # uppercase
        r'[a-z]',  # lowercase
        r'[0-9]',  # numbers
        r'[!@#$%^&*(),.?":{}|<>]'  # special characters
    ]
    
    for pattern in patterns:
        if not re.search(pattern, password):
            logger.warning("Password missing required character type")
            return False
    
    return True

# Phone number validation
def is_valid_phone(phone):
    """Validate phone number format
    Rules:
    - Must be between 10-15 digits
    - Can optionally start with + and country code
    - Only digits allowed after country code
    """
    logger.debug(f"Validating phone number: {phone}")
    # Remove spaces and hyphens for validation
    phone = re.sub(r'[\s-]', '', phone)
    # Pattern allows optional + followed by 10-15 digits
    pattern = r'^\+?[1-9]\d{9,14}$'
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