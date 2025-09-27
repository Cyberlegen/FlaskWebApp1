import sqlite3

# Database configuration
DATABASE = 'users.db'

def init_db():
    """Initialize the database with users table (drops existing table)"""
    with sqlite3.connect(DATABASE) as conn:
        # DROP EXISTING TABLE(OPTIONAL, FOR TESTING)
        conn.execute('DROP TABLE IF EXISTS users')

        # CREATE TABLE
        conn.execute('''
                        CREATE TABLE users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            email TEXT NOT NULL,
                            password TEXT NOT NULL,
                            role TEXT NOT NULL DEFAULT 'user'
                        )
                    ''')
        conn.commit()
def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def user_exists(username):
    conn= get_db_connection()
    # Check if username already exists in the database
    user = conn.execute('SELECT username FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user is not None

def create_user(username, email, password):
    """Create a new user in the database"""
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                    (username, email, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def validate_user(username, password):
       """Validate user credentials and return user data"""
       conn = get_db_connection()
       user = conn.execute(
           'SELECT username, role FROM users WHERE username = ? AND password = ?',
           (username, password)
       ).fetchone()
       conn.close()
       return user  # User data if found, None if not found
    
def set_admin(username): # SET ADMIN FUNCTION
       conn = sqlite3.connect('users.db')
       conn.execute(f'UPDATE users SET role = \"admin\" WHERE username = \"{username}"')
       conn.commit()
       conn.close()
       print('Admin user created!')
    
def get_all_users():
    """Get all users for admin dashboard"""
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, email, role FROM users ORDER BY id').fetchall()
    conn.close()
    return users

def promote_user_to_admin(user_id):
    """Promote a user to admin role"""
    conn = get_db_connection()
    conn.execute('UPDATE users SET role = ? WHERE id = ?', ('admin', user_id))
    conn.commit()
    conn.close()

def demote_user_to_user(user_id):
    """Demote an admin to regular user"""
    conn = get_db_connection()
    conn.execute('UPDATE users SET role = ? WHERE id = ?', ('user', user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    """Delete a user (admin function)"""
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()