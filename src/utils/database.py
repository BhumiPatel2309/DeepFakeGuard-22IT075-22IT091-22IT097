import os
import sys
import sqlite3
import hashlib
from datetime import datetime

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import logger

def init_db():
    logger.info("Initializing database")
    conn = sqlite3.connect('deepfake.db')
    c = conn.cursor()
    
    try:
        # Users table without verification fields
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      email TEXT UNIQUE NOT NULL,
                      phone TEXT UNIQUE,
                      password TEXT NOT NULL,
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
        
        conn.commit()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password, phone=None):
    logger.info(f"Attempting to register new user: {username}")
    conn = sqlite3.connect('deepfake.db')
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
        c.execute('''INSERT INTO users 
                     (username, email, phone, password)
                     VALUES (?, ?, ?, ?)''',
                 (username, email, phone, hash_password(password)))
        
        conn.commit()
        logger.info(f"User registered successfully: {username}")
        return True, "Registration successful"
    
    except Exception as e:
        logger.error(f"Registration error for user {username}: {e}")
        return False, "Registration failed"
    finally:
        conn.close()

def login_user(username, password):
    logger.info(f"Login attempt for user: {username}")
    conn = sqlite3.connect('deepfake.db')
    c = conn.cursor()
    
    try:
        # Check credentials and get user info
        c.execute('''SELECT email, phone 
                     FROM users 
                     WHERE username = ? AND password = ?''',
                 (username, hash_password(password)))
        result = c.fetchone()
        
        if not result:
            logger.warning(f"Failed login attempt for user: {username}")
            return False, "Invalid credentials", None
        
        email, phone = result
        logger.info(f"Successful login for user: {username}")
        
        return True, "Login successful", {
            "email": email,
            "phone": phone
        }
    
    except Exception as e:
        logger.error(f"Login error for user {username}: {e}")
        return False, "Login failed", None
    finally:
        conn.close()

def log_activity(username, file_type, result, probability):
    logger.info(f"Logging activity for user {username}: {file_type} analysis")
    conn = sqlite3.connect('deepfake.db')
    c = conn.cursor()
    
    try:
        c.execute('''INSERT INTO activity_log 
                     (username, file_type, result, probability)
                     VALUES (?, ?, ?, ?)''',
                 (username, file_type, result, probability))
        conn.commit()
        logger.debug(f"Activity logged - User: {username}, Type: {file_type}, Result: {result}, Probability: {probability}")
    except Exception as e:
        logger.error(f"Error logging activity for user {username}: {e}")
    finally:
        conn.close()

def get_user_stats(username):
    logger.info(f"Retrieving stats for user: {username}")
    conn = sqlite3.connect('deepfake.db')
    c = conn.cursor()
    
    try:
        c.execute('''SELECT COUNT(*) as total,
                     SUM(CASE WHEN result = 'fake' THEN 1 ELSE 0 END) as fakes,
                     SUM(CASE WHEN file_type = 'Image' THEN 1 ELSE 0 END) as images,
                     SUM(CASE WHEN file_type = 'Video' THEN 1 ELSE 0 END) as videos
                     FROM activity_log WHERE username = ?''', (username,))
        
        result = c.fetchone()
        stats = {
            'total_analyzed': result[0] or 0,
            'deepfakes_detected': result[1] or 0,
            'images_analyzed': result[2] or 0,
            'videos_analyzed': result[3] or 0
        }
        logger.debug(f"Retrieved stats for {username}: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error retrieving stats for user {username}: {e}")
        return {
            'total_analyzed': 0,
            'deepfakes_detected': 0,
            'images_analyzed': 0,
            'videos_analyzed': 0
        }
    finally:
        conn.close()

def get_recent_activity(username, limit=5):
    logger.info(f"Retrieving recent activity for user: {username}")
    conn = sqlite3.connect('deepfake.db')
    c = conn.cursor()
    
    try:
        c.execute('''SELECT file_type, result, probability, timestamp
                     FROM activity_log 
                     WHERE username = ?
                     ORDER BY timestamp DESC
                     LIMIT ?''', (username, limit))
        
        activities = c.fetchall()
        activities_list = [{
            'file_type': a[0],
            'result': a[1],
            'probability': a[2],
            'timestamp': a[3]
        } for a in activities]
        logger.debug(f"Retrieved {len(activities_list)} recent activities for {username}")
        return activities_list
    except Exception as e:
        logger.error(f"Error retrieving recent activity for user {username}: {e}")
        return []
    finally:
        conn.close()