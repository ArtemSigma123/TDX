from flask import Flask, render_template, request, jsonify, json, session, redirect, url_for, make_response
from flask_mail import Mail, Message
import os, random, uuid
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'TDX_V5_STABLE_FIXED'
app.permanent_session_lifetime = timedelta(days=30)

# --- ПОЧТА ---
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='tdxmessage@gmail.com',
    MAIL_PASSWORD='wiai bzvz konk ddbf', 
    MAIL_DEFAULT_SENDER='tdxmessage@gmail.com'
)

mail = Mail(app)
DB_FILE = 'database.json'
temp_codes = {}
temp_users = {} # Для регистрации

def load_db():
    if not os.path.exists(DB_FILE):
        db = {"users": [], "chats": {}, "saved": {}}
        save_db(db)
        return db
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_current_user():
    email = session.get('user_email')
    if not email: return None
    db = load_db()
    return next((u for u in db['users'] if u['email'].lower() == email.lower()), None)

# --- РОУТЫ ---

@app.route('/')
def index():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    if session.get('2fa_needed'): return redirect(url_for('two_factor_page'))
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        db = load_db()
        email = data.get('login', '').lower().strip()
        user = next((u for u in db['users'] if u['email'].lower() == email), None)
        
        if user and check_password_hash(user['password'], data.get('password')):
            session['user_email'] = user['email']
            temp_codes[user['email']] = "111111"
            session['2fa_needed'] = True
            return jsonify({"status": "2fa_required"})
        return jsonify({"message": "Ошибка входа"}), 401
    return render_template('login.html')

@app.route('/2fa', methods=['GET', 'POST'])
def two_factor_page():
    if request.method == 'POST':
        code = request.json.get('code')
        email = session.get('user_email')
        if code == "111111":
            session.pop('2fa_needed', None)
            return jsonify({"status": "success"})
        return jsonify({"message": "Неверный код"}), 400
    return render_template('2fa.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        email = data.get('email', '').lower().strip()
        db = load_db()
        if any(u['email'] == email for u in db['users']):
            return jsonify({"message": "Email занят"}), 400
        
        # Временное сохранение
        temp_users[email] = {
            "email": email,
            "display_name": data.get('username'),
            "password": generate_password_hash(data.get('password')),
            "trusted_devices": []
        }
        session['reg_email'] = email
        return jsonify({"status": "2fa_required"})
    return render_template('register.html')

@app.route('/verify_reg', methods=['POST'])
def verify_reg():
    code = request.json.get('code')
    email = session.get('reg_email')
    if email in temp_users and code == "111111":
        db = load_db()
        db['users'].append(temp_users.pop(email))
        save_db(db)
        session.pop('reg_email', None)
        return jsonify({"status": "success"})
    return jsonify({"message": "Код неверный"}), 400

@app.route('/search_user', methods=['POST'])
def search_user():
    q = request.json.get('username', '').lower()
    db = load_db()
    curr = get_current_user()
    return jsonify([u['display_name'] for u in db['users'] if q in u['display_name'].lower() and u['display_name'] != curr['display_name']])

@app.route('/get_chat', methods=['POST'])
def get_chat():
    target = request.json.get('target')
    user = get_current_user()
    db = load_db()
    c_id = "_".join(sorted([user['display_name'], target]))
    return jsonify({"messages": db['chats'].get(c_id, [])})

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    user = get_current_user()
    db = load_db()
    c_id = "_".join(sorted([user['display_name'], data['target']]))
    if c_id not in db['chats']: db['chats'][c_id] = []
    db['chats'][c_id].append({"sender": user['display_name'], "text": data['text']})
    save_db(db)
    return jsonify({"status": "success"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

