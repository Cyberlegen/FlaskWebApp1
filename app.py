from functools import wraps
from flask_caching import Cache

from flask import Flask, flash, redirect, render_template, request, session, url_for

from database import (
    create_user,
    delete_user,
    demote_user_to_user,
    get_all_users,
    init_db,
    promote_user_to_admin,
    set_admin,
    user_exists,
    validate_user,
)

app = Flask(__name__)
app.secret_key = 'paranoid'  # Change this in production
"""app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_HOST'] = '0.0.0.0'
app.config['CACHE_REDIS_PORT'] = 34313
#app.config['CACHE_REDIS_DB'] = 0
cache = Cache(app)"""



"""""""""""""INDEX AND CONDITIONS"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

@app.route('/')
@cache.cached(timeout=50)
def index():
    return render_template('index.html')

def admin_required(f):      #CONDITION FOR ADMIN REQUIRED
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in first', 'error')
            return redirect(url_for('login'))

        if session.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('index'))

        return f(*args, **kwargs)
    return wrapper

def login_required(f):     #CONDITION FOR LOGIN REQUIRED
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in first', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper
"""""""""ADMIN: DASHBOARD, PROMOTE, DEMOTE, DELETE"""""""""""""""""""""""""""""""""""""""""""""""""""
@app.route('/admin')
@admin_required
def admin_dashboard():
    users = get_all_users()
    return render_template('admin/dashboard.html', users=users)
@app.route('/admin/promote/<int:user_id>')
@admin_required
def promote_user(user_id):
    promote_user_to_admin(user_id)
    flash('User promoted to admin successfully', 'success')
    return redirect(url_for('admin_dashboard'))
@app.route('/admin/demote/<int:user_id>')
@admin_required  
def demote_user(user_id):
    demote_user_to_user(user_id)
    flash('User demoted to regular user', 'success')
    return redirect(url_for('admin_dashboard'))
@app.route('/admin/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user_route(user_id):
    delete_user(user_id)
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))
    
"""""""""""""AUTHENTICATION: LOGIN, SIGNUP, LOGOUT"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
promote_user_to_admin('admin')
@app.route('/login', methods=['GET', 'POST'])
#@cache.cached(timeout=50)
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Basic validation
        if not username or not password:
            flash('Please fill in all fields', 'error')
        else:
            # Validate credentials and get user data
            user = validate_user(username, password)

            if user:
                # Store user data in session
                session['username'] = user['username']
                session['role'] = user['role']
                session['logged_in'] = True

                flash(f'Login successful! Welcome back, {username}', 'success')
                return redirect(url_for('subjects'))
            else:
                flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
#@cache.cached(timeout=50)
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']     
        # Basic validation 
        if not username or not email or not password or not confirm_password:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('signup'))
        elif '@' not in email:
            flash('Invalid email address', 'error')
            return redirect(url_for('signup'))
        elif password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))
        elif user_exists(username):
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('signup'))
        else:
            # Save user to database
            if create_user(username, email, password):
                flash(f'Signup successful for user: {username}. You can now login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Failed to create user due to a server error.', 'error')
    return render_template('signup.html')
                
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

"""""""""""""SUBJECTS"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@app.route('/subjects')
@login_required
#@cache.cached(timeout=20)
def subjects():
    # Add your logic to fetch and display subjects here
    # For now, we'll just render the subjects template
    # You can use the database to fetch subjects and pass them to the template
    subjects = [
        {"name": "Computer Science", "description": "CS101 - Introduction to programming and algorithms"},
        {"name": "Mathematics", "description": "MATH101 - Calculus and linear algebra fundamentals"},
        {"name": "Physics", "description": "PHY101 - Classical mechanics and thermodynamics"},
        {"name": "Chemistry", "description": "CHEM101 - Atomic structure and chemical reactions"},
        {"name": "Biology", "description": "BIO101 - Cell biology and genetics"},
        {"name": "Geography", "description": "GEO101 - Physical and human geography"},
        {"name": "English", "description": "ENG101 - Literature and composition"},
        {"name": "Spanish", "description": "SPA101 - Basic Spanish language and culture"}
    ]
    return render_template('subjects.html', subjects=subjects)
    return render_template('subjects.html', subjects=subjects)

if __name__ == '__main__':
       # Initialize database first
       init_db()
       # Then set admin (after table exists)
       set_admin('admin')
       app.run(host='0.0.0.0', port=5000, debug=True)