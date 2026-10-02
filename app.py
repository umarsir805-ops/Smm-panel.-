from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = "umar_heavy_backend_secret"

# Yahan apni API details dali hain
API_URL = "https://sparkyinfluence.in/api/v2"
API_KEY = "6016e188a1f7a6bb303f16eb539f9a96"
PANEL_PASSWORD = "umar"

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT,
            link TEXT,
            quantity INTEGER,
            charge REAL,
            api_order_id TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

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
    <title>AS illusion - SMM Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        body { background: #0f172a; color: #f8fafc; margin: 0; padding: 0; min-height: 100vh; display: flex; flex-direction: column; }
        
        header {
            background: #1e293b;
            border-bottom: 1px solid #334155;
            padding: 15px 30px;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }
        .logo {
            font-family: 'Orbitron', sans-serif;
            font-size: 22px;
            font-weight: 800;
            text-align: center;
            letter-spacing: 1px;
        }
        .logo .red-text { color: #ef4444; }
        .logo .white-text { color: #f8fafc; }
        
        .logout-container {
            position: absolute;
            right: 30px;
        }
        
        .main-container {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .full-card {
            background: #1e293b;
            width: 100%;
            max-width: 600px;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            border: 1px solid #334155;
        }
        
        input, select {
            width: 100%;
            padding: 14px;
            margin-top: 8px;
            margin-bottom: 15px;
            background: #0f172a;
            border: 1px solid #475569;
            color: #fff;
            border-radius: 8px;
            font-size: 14px;
        }
        input:focus, select:focus {
            border-color: #22c55e;
            outline: none;
        }
        
        label {
            font-size: 13px;
            color: #22c55e;
            font-weight: 600;
            display: block;
        }
        
        button {
            width: 100%;
            padding: 14px;
            background: #22c55e;
            border: none;
            color: white;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            transition: background 0.2s;
        }
        button:hover { background: #16a34a; }
        
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 600;
            font-size: 14px;
        }
        .alert-success { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
        .alert-error { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
        
        h2 { margin-top: 0; color: #f8fafc; font-size: 22px; margin-bottom: 20px; }
    </style>
    <script>
        function updateServiceDetails() {
            const select = document.getElementById('serviceSelect');
            if(!select) return;
            const qtyInput = document.getElementById('qtyInput');
            const chargeInput = document.getElementById('chargeInput');
            
            const selectedOption = select.options[select.selectedIndex];
            const ratePer1000 = parseFloat(selectedOption.getAttribute('data-rate')) || 0;
            const quantity = parseInt(qtyInput.value) || 0;
            
            const totalCharge = (quantity / 1000) * ratePer1000;
            chargeInput.value = "₹ " + totalCharge.toFixed(2);
        }
    </script>
</head>
<body>
    <header>
        <div class="logo"><span class="red-text">AS</span> <span class="white-text">illusion</span></div>
        {% if session.get('logged') %}
            <div class="logout-container">
                <form method="POST" action="/logout" style="margin: 0;">
                    <button type="submit" style="padding: 8px 16px; background: #ef4444; font-size: 13px; width: auto;">Lock Panel</button>
                </form>
            </div>
        {% endif %}
    </header>

    <div class="main-container">
        <div class="full-card">
            {% if not session.get('logged') %}
                <h2>Panel Access</h2>
                {% if error %}
                    <div class="alert alert-error">{{ error }}</div>
                {% endif %}
                <form method="POST" action="/login">
                    <label>Enter Password</label>
                    <input type="password" name="password" placeholder="Enter panel password" required>
                    <button type="submit">Unlock Panel</button>
                </form>
            {% else %}
                <h2>New Order Dashboard</h2>
                {% if message %}
                    <div class="alert alert-success">{{ message }}</div>
                {% elif error %}
                    <div class="alert alert-error">{{ error }}</div>
                {% endif %}
                <form method="POST" action="/order">
                    <label>Select Service</label>
                    <select name="service" id="serviceSelect" onchange="updateServiceDetails()" required>
                        <option value="" disabled selected>Choose Instagram service...</option>
                        {% for s in services %}
                            <option value="{{ s.service }}" data-rate="{{ s.rate }}">
                                {{ s.name }} (₹{{ s.rate }}/1k)
                            </option>
                        {% endfor %}
                    </select>
                    
                    <label>Target Link / Username</label>
                    <input type="text" name="link" placeholder="Paste profile or post link here" required>
                    
                    <label>Quantity</label>
                    <input type="number" name="quantity" id="qtyInput" oninput="updateServiceDetails()" placeholder="Enter quantity" required>
                    
                    <label>Total Charge</label>
                    <input type="text" id="chargeInput" value="₹ 0.00" disabled style="background: #0f172a; font-weight: bold; color: #22c55e;">
                    
                    <button type="submit">Submit Order</button>
                </form>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    logged_in = session.get('logged', False)
    services = fetch_services() if logged_in else []
    return render_template_string(TEMPLATE, logged_in=logged_in, services=services)

@app.route("/login", methods=["POST"])
def login():
    password = request.form.get("password", "").strip()
    if password == PANEL_PASSWORD:
        session['logged'] = True
        return redirect(url_for('index'))
    return render_template_string(TEMPLATE, logged_in=False, error="Incorrect Password!")

@app.route("/order", methods=["POST"])
def order():
    if not session.get('logged', False):
        return redirect(url_for('index'))
    
    service_id = request.form.get("service")
    target_link = request.form.get("link", "").strip()
    quantity_str = request.form.get("quantity")
    
    try:
        quantity = int(quantity_str)
    except ValueError:
        return redirect(url_for('index'))
        
    services = fetch_services()
    rate = 0
    service_name = "Unknown"
    for s in services:
        if str(s.get('service')) == str(service_id):
            rate = float(s.get('rate', 0))
            service_name = s.get('name', 'Service')
            break
            
    total_charge = (quantity / 1000) * rate
    
    payload = {
        'key': API_KEY,
        'action': 'add',
        'service': service_id,
        'link': target_link,
        'quantity': quantity
    }
    
    message = ""
    error = None
    api_order_id = None
    
    try:
        response = requests.post(API_URL, data=payload, timeout=15)
        res_json = response.json()
        if isinstance(res_json, dict) and 'order' in res_json:
            api_order_id = str(res_json['order'])
            message = f"Success! Order placed. ID: {api_order_id}"
        elif isinstance(res_json, dict) and 'error' in res_json:
            error = f"Provider Error: {res_json['error']}"
        else:
            error = "Unexpected response from provider."
    except Exception as e:
        error = f"Connection Error: {e}"
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (service_name, link, quantity, charge, api_order_id, status) VALUES (?, ?, ?, ?, ?, ?)",
                   (service_name, target_link, quantity, total_charge, api_order_id, message if not error else error))
    conn.commit()
    conn.close()
    
    return render_template_string(TEMPLATE, logged_in=True, services=services, message=message, error=error)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('logged', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
