import sqlite3
import hashlib
from database import create_connection

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    """Register a new user"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            hashed_pw = hash_password(password)
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
            conn.commit()
            print("User registered successfully!")
            return True
        except sqlite3.IntegrityError:
            print("Username already exists. Please choose another.")
        except Error as e:
            print(f"Error registering user: {e}")
        finally:
            conn.close()
    return False

def login_user(username, password):
    """Authenticate a user"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            hashed_pw = hash_password(password)
            cursor.execute('SELECT id FROM users WHERE username=? AND password=?', (username, hashed_pw))
            user = cursor.fetchone()
            if user:
                print("Login successful!")
                return user[0]  # Return user ID
            else:
                print("Invalid username or password.")
        except Error as e:
            print(f"Error logging in: {e}")
        finally:
            conn.close()
    return None

def change_password(user_id, old_password, new_password):
    """Change user password"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            # Verify old password first
            cursor.execute('SELECT id FROM users WHERE id=? AND password=?',
                          (user_id, hash_password(old_password)))
            if cursor.fetchone():
                new_hashed_pw = hash_password(new_password)
                cursor.execute('UPDATE users SET password=? WHERE id=?', (new_hashed_pw, user_id))
                conn.commit()
                print("Password changed successfully!")
                return True
            else:
                print("Old password is incorrect.")
        except Error as e:
            print(f"Error changing password: {e}")
        finally:
            conn.close()
    return False