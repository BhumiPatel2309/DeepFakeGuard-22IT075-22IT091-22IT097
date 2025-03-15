import os
import sys
import sqlite3
import hashlib
from datetime import datetime

# Add the project root directory to Python path
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(current_dir)

from src.utils.logger import logger

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initialize the database with required tables"""
    logger.info("Initializing database")
    db_path = os.path.join(current_dir, 'deepfake.db')
    
    try:
        # Ensure the database connection is properly closed
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Users table with admin field and google_id
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      email TEXT UNIQUE NOT NULL,
                      phone TEXT UNIQUE,
                      password TEXT,
                      google_id TEXT UNIQUE,
                      is_admin BOOLEAN DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        logger.debug("Users table initialized")
        
        # Activity tracking
        c.execute('''CREATE TABLE IF NOT EXISTS activity_log
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT NOT NULL,
                      file_type TEXT NOT NULL,
                      result TEXT NOT NULL,
                      probability REAL NOT NULL,
                      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        logger.debug("Activity log table initialized")
        
        # Check if admin exists, if not create default admin
        c.execute('SELECT COUNT(*) FROM users WHERE username = ? OR email = ?', 
                 ("admin", "admin@deepfakeguard.com"))
        if c.fetchone()[0] == 0:
            admin_password = hash_password("admin123")  # Default password
            c.execute('''INSERT INTO users 
                        (username, email, password, is_admin)
                        VALUES (?, ?, ?, ?)''',
                     ("admin", "admin@deepfakeguard.com", admin_password, 1))
            logger.info("Created default admin user")
        else:
            logger.info("Admin user already exists")
        
        conn.commit()
        logger.info("Database initialization completed successfully")
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def get_db_connection():
    """Get a database connection with proper error handling"""
    try:
        db_path = os.path.join(current_dir, 'deepfake.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise

def register_user(username, email, password, phone=None, is_admin=False, is_google_auth=False):
    logger.info(f"Attempting to register new user: {username}")
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        # Check if username or email already exists
        c.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
        if c.fetchone():
            logger.warning(f"Registration failed: Username or email already exists - {username}")
            return False, "Username or email already exists"
        
        # Check if phone number is already registered
        if phone:
            c.execute('SELECT username FROM users WHERE phone = ?', (phone,))
            if c.fetchone():
                logger.warning(f"Registration failed: Phone number already registered - {phone}")
                return False, "Phone number already registered"
        
        # Insert new user
        if is_google_auth:
            # For Google auth, we don't store a password
            c.execute('''INSERT INTO users 
                        (username, email, phone, is_admin, google_id)
                        VALUES (?, ?, ?, ?, ?)''',
                    (username, email, phone, is_admin, email))  # Using email as google_id
        else:
            # For regular auth, store hashed password
            c.execute('''INSERT INTO users 
                        (username, email, phone, password, is_admin)
                        VALUES (?, ?, ?, ?, ?)''',
                    (username, email, phone, hash_password(password), is_admin))
        
        conn.commit()
        logger.info(f"User registered successfully: {username}")
        return True, "Registration successful"
    
    except Exception as e:
        logger.error(f"Registration error for user {username}: {str(e)}")
        return False, "Registration failed"
    finally:
        if conn:
            conn.close()

def login_user(username, password, is_google_auth=False):
    logger.info(f"Login attempt for user: {username}")
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        if is_google_auth:
            # For Google auth, check by email in google_id
            c.execute('''SELECT username, email, phone, is_admin 
                        FROM users 
                        WHERE google_id = ?''',
                    (username,))  # username parameter contains email for Google auth
        else:
            # For regular auth, check username and password
            c.execute('''SELECT username, email, phone, is_admin 
                        FROM users 
                        WHERE username = ? AND password = ?''',
                    (username, hash_password(password)))
        
        result = c.fetchone()
        
        if not result:
            logger.warning(f"Failed login attempt for user: {username}")
            return False, "Invalid credentials", None
        
        username, email, phone, is_admin = result
        logger.info(f"Successful login for user: {username}")
        
        return True, "Login successful", {
            "username": username,
            "email": email,
            "phone": phone,
            "is_admin": bool(is_admin)
        }
    
    except Exception as e:
        logger.error(f"Login error for user {username}: {str(e)}")
        return False, "Login failed", None
    finally:
        if conn:
            conn.close()

def log_activity(username, file_type, result, probability):
    logger.info(f"Logging activity for user {username}: {file_type} analysis")
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('''INSERT INTO activity_log 
                     (username, file_type, result, probability)
                     VALUES (?, ?, ?, ?)''',
                 (username, file_type, result, probability))
        conn.commit()
        logger.debug(f"Activity logged - User: {username}, Type: {file_type}, Result: {result}, Probability: {probability}")
    except Exception as e:
        logger.error(f"Error logging activity for user {username}: {str(e)}")
    finally:
        if conn:
            conn.close()

def get_user_stats(username):
    logger.info(f"Retrieving stats for user: {username}")
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('''SELECT COUNT(*) as total,
                     SUM(CASE WHEN result = 'fake' THEN 1 ELSE 0 END) as fakes,
                     SUM(CASE WHEN file_type = 'Image' THEN 1 ELSE 0 END) as images,
                     SUM(CASE WHEN file_type = 'Video' THEN 1 ELSE 0 END) as videos
                     FROM activity_log WHERE username = ?''', (username,))
        
        result = c.fetchone()
        stats = {
            'total_analyzed': result['total'] or 0,
            'deepfakes_detected': result['fakes'] or 0,
            'images_analyzed': result['images'] or 0,
            'videos_analyzed': result['videos'] or 0
        }
        logger.debug(f"Retrieved stats for {username}: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error retrieving stats for user {username}: {str(e)}")
        return {
            'total_analyzed': 0,
            'deepfakes_detected': 0,
            'images_analyzed': 0,
            'videos_analyzed': 0
        }
    finally:
        if conn:
            conn.close()

def get_recent_activity(username, limit=5):
    logger.info(f"Retrieving recent activity for user: {username}")
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('''SELECT file_type, result, probability, timestamp
                     FROM activity_log 
                     WHERE username = ?
                     ORDER BY timestamp DESC
                     LIMIT ?''', (username, limit))
        
        activities = c.fetchall()
        activities_list = [{
            'file_type': a['file_type'],
            'result': a['result'],
            'probability': a['probability'],
            'timestamp': a['timestamp']
        } for a in activities]
        logger.debug(f"Retrieved {len(activities_list)} recent activities for {username}")
        return activities_list
    except Exception as e:
        logger.error(f"Error retrieving recent activity for user {username}: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()