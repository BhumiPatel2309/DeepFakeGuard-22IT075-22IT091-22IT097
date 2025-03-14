# Application configuration settings

# Database settings
DB_NAME = 'deepfake.db'

# File upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png']
ALLOWED_VIDEO_EXTENSIONS = ['mp4']
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Model settings
DEFAULT_MODEL = 'EfficientNetAutoAttB4'
DEFAULT_DATASET = 'DFDC'
DEFAULT_THRESHOLD = 0.5
DEFAULT_FRAMES = 50

# Security settings
MIN_PASSWORD_LENGTH = 6
PASSWORD_SALT = "deepfake_detector_salt" 

# UI settings
APP_TITLE = "Deepfake Detector"
APP_ICON = "🔍"
APP_LAYOUT = "wide"