import sqlite3

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Database configuration
DATABASE = 'users.db'

def init_db():
    """Initialize the database with users table"""
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def user_exists(username):
    """Check if username already exists"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT username FROM users WHERE username = ?', (username,)
    ).fetchone()
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
    """Validate user credentials"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT username, password FROM users WHERE username = ? AND password = ?',
        (username, password)
    ).fetchone()
    conn.close()
    return user is not None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Basic validation
        if not username or not password:
            flash('Please fill in all fields', 'error')
        else:
            # Validate credentials against database
            if validate_user(username, password):
                flash(f'Login successful! Welcome back, {username}', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Basic validation
        if not username or not email or not password or not confirm_password:
            flash('Please fill in all fields', 'error')
        elif password != confirm_password:
            flash('Passwords do not match', 'error')
        elif user_exists(username):
            flash('Username already exists. Please choose a different username.', 'error')
        else:
            # Save user to database
            if create_user(username, email, password):
                flash(f'Signup successful for user: {username}. You can now login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Error creating user. Please try again.', 'error')
    
    return render_template('signup.html')

if __name__ == '__main__':
    # Initialize database
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)