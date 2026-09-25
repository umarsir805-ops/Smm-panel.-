from flask import Flask, redirect, render_template_string, request, session, url_for
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = "umar_secret_key_super_secure"

API_URL = "https://sparkyinfluence.in/api/v2"
API_KEY = "6016e188a1f7a6bb303f16eb539f9a96"

# Yahan apna username daal de jo tu login ke liye use karega, isko hamesha unlimited balance milega!
ADMIN_USERNAME = "umar" 

# Database Initialization
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance REAL DEFAULT 0.0
        )
    ''')
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            service_name TEXT NOT NULL,
            link TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            charge REAL NOT NULL,
            api_order_id TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_user_balance(username):
    # Agar admin login hai, toh use hamesha unlimited/high balance dikhayega
    if username.lower() == ADMIN_USERNAME.lower():
        return 99999.0
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0.0

def fetch_services():
    try:
        response = requests.post(API_URL, data={"key": API_KEY, "action": "services"}, timeout=10)
        data = response.json()
        if isinstance(data, list):
            filtered = []
            for s in data:
                name_lower = s.get('name', '').lower()
                cat_lower = s.get('category', '').lower()
                if 'instagram' in name_lower or 'instagram' in cat_lower:
                    if any(keyword in name_lower for keyword in ['follower', 'like', 'view', 'reel', 'post', 'comment', 'share', 'repost']):
                        if 'package' not in name_lower:
                            filtered.append(s)
            return filtered if filtered else data[:20]
    except Exception:
        pass
    return []

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Umar_Tools</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        body { background: #0f172a; color: #1e293b; display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 100vh; margin: 0; overflow-x: hidden; }
        
        .main-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 22px;
            font-weight: 800;
            color: #ffffff;
            text-align: center;
            margin-bottom: 15px;
            letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(255,255,255,0.3);
        }
        .main-title span {
            background: linear-gradient(45deg, #ff416c, #ff4b2b, #00ff87, #60efff);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientShift 5s ease infinite;
        }
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .dashboard { width: 100%; max-width: 440px; padding: 15px; }
        .card { 
            background: #ffffff; 
            border-radius: 16px; 
            padding: 24px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            position: relative;
            z-index: 1;
        }
        .card-glow-wrap {
            position: relative;
            border-radius: 18px;
            padding: 3px;
            background: linear-gradient(60deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000);
            background-size: 300% 300%;
            animation: rgbBorderAnimation 4s linear infinite;
        }
        @keyframes rgbBorderAnimation {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .brand { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #f1f5f9; padding-bottom: 12px; }
        .brand h2 { margin: 0; font-size: 18px; font-weight: 700; }
        .brand .red-text { color: #dc2626; }
        .brand .green-text { color: #16a34a; }
        
        .wallet-badge {
            background: #dcfce7;
            color: #166534;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 15px;
            border: 1px solid #bbf7d0;
        }

        label { font-size: 13px; font-weight: 600; color: #16a34a; display: block; margin-top: 12px; margin-bottom: 6px; }
        input, select { width: 100%; padding: 12px; background: #f8fafc; border: 1px solid #cbd5e1; color: #0f172a; border-radius: 8px; font-size: 14px; transition: all 0.2s ease; }
        input:focus, select:focus { border-color: #16a34a; outline: none; background: #fff; box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.1); }
        
        .desc-box { background: #f1f5f9; border: 1px solid #e2e8f0; padding: 12px; border-radius: 8px; margin-top: 12px; font-size: 12px; color: #334155; white-space: pre-line; display: none; line-height: 1.5; }
        
        button { width: 100%; padding: 14px; background: #16a34a; border: none; color: white; font-weight: 600; border-radius: 8px; cursor: pointer; margin-top: 15px; font-size: 15px; transition: background 0.2s; }
        button:hover { background: #15803d; }
        
        .secondary-btn { background: #3b82f6; margin-top: 8px; }
        .secondary-btn:hover { background: #2563eb; }

        .logout-btn { background: transparent; border: 1px solid #cbd5e1; color: #64748b; margin-top: 8px; }
        .logout-btn:hover { background: #f1f5f9; color: #0f172a; }
        
        .alert { padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 15px; text-align: center; font-weight: 500; }
        .alert-success { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
        .alert-error { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
        .switch-text { text-align: center; font-size: 12px; margin-top: 15px; color: #64748b; }
        .switch-text a { color: #16a34a; text-decoration: none; font-weight: 600; }
    </style>
    <script>
        function updateServiceDetails() {
            const select = document.getElementById('serviceSelect');
            if(!select) return;
            const qtyInput = document.getElementById('qtyInput');
            const chargeInput = document.getElementById('chargeInput');
            const descBox = document.getElementById('descBox');
            
            const selectedOption = select.options[select.selectedIndex];
            const ratePer1000 = parseFloat(selectedOption.getAttribute('data-rate')) || 0;
            const description = selectedOption.getAttribute('data-desc') || "";
            const quantity = parseInt(qtyInput.value) || 0;
            
            const totalCharge = (quantity / 1000) * ratePer1000;
            chargeInput.value = "₹ " + totalCharge.toFixed(2);
            
            if (description.trim() !== "") {
                descBox.style.display = "block";
                descBox.innerText = description;
            } else {
                descBox.style.display = "none";
            }
        }
    </script>
</head>
<body>
    <div class="dashboard">
        <div class="main-title"><span>Umar_Tools</span></div>
        <div class="card-glow-wrap">
            <div class="card">
                <div class="brand">
                    <h2><span class="red-text">AS</span> <span class="green-text">illusion</span></h2>
                    {% if username %}
                        <span style="font-size: 12px; color: #64748b;">
                            {% if is_admin %}👑 Admin{% else %}Hi, {{ username }}{% endif %}
                        </span>
                    {% endif %}
                </div>

                {% if error %}
                    <div class="alert alert-error">{{ error }}</div>
                {% endif %}
                {% if message %}
                    <div class="alert alert-success">{{ message }}</div>
                {% endif %}

                {% if page == 'login' %}
                    <form method="POST" action="/login">
                        <label>Username</label>
                        <input type="text" name="username" placeholder="Enter username" required>
                        <label>Password</label>
                        <input type="password" name="password" placeholder="Enter password" required>
                        <button type="submit">Login</button>
                    </form>
                    <div class="switch-text">Don't have an account? <a href="/register">Sign Up</a></div>

                {% elif page == 'register' %}
                    <form method="POST" action="/register">
                        <label>Choose Username</label>
                        <input type="text" name="username" placeholder="Choose username" required>
                        <label>Choose Password</label>
                        <input type="password" name="password" placeholder="Choose password" required>
                        <button type="submit">Register Account</button>
                    </form>
                    <div class="switch-text">Already have an account? <a href="/login">Login</a></div>

                {% elif page == 'add_funds' %}
                    <div class="wallet-badge">Wallet Balance: ₹ {{ "%.2f"|format(balance) }}</div>
                    <div style="text-align: center; margin-bottom: 15px;">
                        <p style="font-size: 13px; color: #475569; margin-bottom: 8px;">Scan QR to Pay via UPI:</p>
                        <div style="background: #f1f5f9; padding: 15px; border-radius: 12px; display: inline-block; font-weight: bold; color: #1e293b; border: 1px dashed #cbd5e1;">
                            [ 📱 YOUR UPI QR CODE HERE ]<br>
                            <span style="font-size: 11px; color: #64748b;">UPI ID: yourname@oksbi</span>
                        </div>
                    </div>
                    <form method="POST" action="/add_funds">
                        <label>Enter Amount Paid (₹)</label>
                        <input type="number" name="amount" placeholder="e.g. 100" required>
                        <button type="submit">Add to Wallet Instantly</button>
                    </form>
                    <form action="/" method="GET">
                        <button type="submit" class="logout-btn">Back to Dashboard</button>
                    </form>

                {% else %}
                    <div class="wallet-badge">Wallet Balance: ₹ {{ "%.2f"|format(balance) }}</div>
                    <a href="/add_funds"><button type="button" class="secondary-btn" style="margin-top:0; margin-bottom:15px;">➕ Add Funds (UPI)</button></a>

                    <form method="POST" action="/order">
                        <label>Service</label>
                        <select name="service" id="serviceSelect" onchange="updateServiceDetails()" required>
                            <option value="" disabled selected>Choose Instagram service...</option>
                            {% for s in services %}
                                <option value="{{ s.service }}" data-rate="{{ s.rate }}" data-desc="{{ s.description }}">
                                    {{ s.name }} (₹{{ s.rate }}/1k)
                                </option>
                            {% endfor %}
                        </select>
                        
                        <label>Description</label>
                        <div class="desc-box" id="descBox"></div>
                        
                        <label>Link / Username</label>
                        <input type="text" name="link" placeholder="Profile link or Username" required>
                        
                        <label>Quantity</label>
                        <input type="number" name="quantity" id="qtyInput" oninput="updateServiceDetails()" placeholder="Quantity" required>
                        
                        <label>Total Charge</label>
                        <input type="text" id="chargeInput" value="₹ 0.00" disabled style="background: #e2e8f0; font-weight: bold; color: #16a34a;">
                        
                        <button type="submit">Submit Order</button>
                    </form>
                    <form method="POST" action="/logout">
                        <button type="submit" class="logout-btn">Sign Out</button>
                    </form>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    is_admin = (username.lower() == ADMIN_USERNAME.lower())
    balance = get_user_balance(username)
    services = fetch_services()
    
    return render_template_string(TEMPLATE, page='dashboard', username=username, is_admin=is_admin, balance=balance, services=services)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        
        # Agar admin pehli baar login kar raha hai aur database mein nahi hai, toh auto-create kar do
        if username.lower() == ADMIN_USERNAME.lower():
            session['username'] = username
            return redirect(url_for('home'))
            
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error = "Invalid Username or Password!"
            
    return render_template_string(TEMPLATE, page='login', error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    message = None
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        
        if username.lower() == ADMIN_USERNAME.lower():
            error = "This username is reserved for Admin!"
        else:
            try:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password, balance) VALUES (?, ?, ?)", (username, password, 0.0))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                error = "Username already exists! Choose another."
                
    return render_template_string(TEMPLATE, page='register', error=error, message=message)

@app.route("/add_funds", methods=["GET", "POST"])
def add_funds():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    is_admin = (username.lower() == ADMIN_USERNAME.lower())
    
    if request.method == "POST" and not is_admin:
        try:
            amount = float(request.form.get("amount", 0))
            if amount > 0:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, username))
                conn.commit()
                conn.close()
        except ValueError:
            pass
            
    balance = get_user_balance(username)
    return render_template_string(TEMPLATE, page='add_funds', username=username, is_admin=is_admin, balance=balance)

@app.route("/order", methods=["POST"])
def order():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    username = session['username']
    is_admin = (username.lower() == ADMIN_USERNAME.lower())
    service_id = request.form.get("service")
    target_link = request.form.get("link", "").strip()
    quantity_str = request.form.get("quantity")
    
    try:
        quantity = int(quantity_str)
    except ValueError:
        return redirect(url_for('home'))
        
    services = fetch_services()
    rate = 0
    service_name = "Unknown"
    for s in services:
        if str(s.get('service')) == str(service_id):
            rate = float(s.get('rate', 0))
            service_name = s.get('name', 'Service')
            break
            
    total_charge = (quantity / 1000) * rate
    current_balance = get_user_balance(username)
    
    if current_balance < total_charge:
        return render_template_string(TEMPLATE, page='dashboard', username=username, is_admin=is_admin, balance=current_balance, services=services, error="Insufficient wallet balance! Please add funds.")
        
    # Deduct balance (agar normal user hai toh database se minus hoga)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if not is_admin:
        new_balance = current_balance - total_charge
        cursor.execute("UPDATE users SET balance = ? WHERE username = ?", (new_balance, username))
        conn.commit()
    else:
        new_balance = current_balance
        
    payload = {
        'key': API_KEY,
        'action': 'add',
        'service': service_id,
        'link': target_link,
        'quantity': quantity
    }
    
    message = ""
    api_order_id = None
    try:
        response = requests.post(API_URL, data=payload, timeout=15)
        res_json = response.json()
        if isinstance(res_json, dict) and 'order' in res_json:
            api_order_id = str(res_json['order'])
            message = f"Success! Order ID: {api_order_id}"
        elif isinstance(res_json, dict) and 'error' in res_json:
            if not is_admin:
                cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (total_charge, username))
                conn.commit()
            message = f"Error from Provider: {res_json['error']}"
        else:
            if not is_admin:
                cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (total_charge, username))
                conn.commit()
            message = "Error: Unexpected response format"
    except Exception as e:
        if not is_admin:
            cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (total_charge, username))
            conn.commit()
        message = f"Connection Error: {e}"
        
    cursor.execute("INSERT INTO orders (username, service_name, link, quantity, charge, api_order_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (username, service_name, target_link, quantity, total_charge, api_order_id, message))
    conn.commit()
    conn.close()
    
    return render_template_string(TEMPLATE, page='dashboard', username=username, is_admin=is_admin, balance=get_user_balance(username), services=services, message=message)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
