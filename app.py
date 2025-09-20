from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

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
            # Here you would typically validate against a database
            flash(f'Login attempt for user: {username}', 'success')
            return redirect(url_for('index'))
    
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
        else:
            # Here you would typically save to a database
            flash(f'Signup successful for user: {username}', 'success')
            return redirect(url_for('login'))
    
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)