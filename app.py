from flask import Flask, request, render_template, redirect, send_from_directory, session, url_for, flash
import os
import hashlib
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret123'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
USERS_DIR = os.path.join(BASE_DIR, 'users')
os.makedirs(USERS_DIR, exist_ok=True)

# Simulasi user: username -> password
USER_DB = {
    'admin': 'admin',
    'user1': 'pass1'
}

def get_user_folder(username):
    folder = os.path.join(USERS_DIR, username)
    os.makedirs(folder, exist_ok=True)
    return folder

def encrypt_filename(filename):
    salt = uuid.uuid4().hex
    hashed = hashlib.sha256((salt + filename).encode()).hexdigest()
    ext = os.path.splitext(filename)[1]
    return f"{hashed}{ext}"

@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')
    user_folder = get_user_folder(session['user'])
    files = os.listdir(user_folder)
    return render_template('dashboard.html', files=files, user=session['user'])

@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        return redirect('/login')
    if 'file' in request.files:
        f = request.files['file']
        if f.filename:
            filename = secure_filename(f.filename)
            encrypted_name = encrypt_filename(filename)
            f.save(os.path.join(get_user_folder(session['user']), encrypted_name))
            flash(f"Uploaded as {encrypted_name}", 'info')
    return redirect('/')

@app.route('/download/<filename>')
def download(filename):
    if 'user' not in session:
        return redirect('/login')
    return send_from_directory(get_user_folder(session['user']), filename, as_attachment=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USER_DB and USER_DB[username] == password:
            session['user'] = username
            return redirect('/')
        flash("Invalid credentials", 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

