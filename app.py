from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# URL of your bot's endpoint
BOT_URL = 'http://localhost:5000'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/setstatus', methods=['POST'])
def set_status():
    if not session.get('logged_in'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    status = request.form['status']
    response = requests.post(f'{BOT_URL}/setstatus', json={'status': status})
    return jsonify({'status': 'success'}) if response.ok else jsonify({'status': 'error'})

@app.route('/sendmessage', methods=['POST'])
def send_message():
    if not session.get('logged_in'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    channel_id = request.form['channel_id']
    message = request.form['message']
    response = requests.post(f'{BOT_URL}/sendmessage', json={'channel_id': channel_id, 'message': message})
    return jsonify({'status': 'success'}) if response.ok else jsonify({'status': 'error'})

@app.route('/createrole', methods=['POST'])
def create_role():
    if not session.get('logged_in'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    role_name = request.form['role_name']
    response = requests.post(f'{BOT_URL}/createrole', json={'role_name': role_name})
    return jsonify({'status': 'success'}) if response.ok else jsonify({'status': 'error'})

@app.route('/serverinfo')
def server_info():
    if not session.get('logged_in'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    response = requests.get(f'{BOT_URL}/serverinfo')
    return jsonify(response.json()) if response.ok else jsonify({'status': 'error'})

if __name__ == '__main__':
    app.run(port=5001)
