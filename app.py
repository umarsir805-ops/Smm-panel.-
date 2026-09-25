from flask import Flask, redirect, render_template_string, request, session, url_for
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = "umar_secret_key_super_secure"

API_URL = "https://sparkyinfluence.in/api/v2"
API_KEY = "6016e188a1f7a6bb303f16eb539f9a96"

# Yahan apna password set kar de jo tu panel kholne ke liye chahta hai
PANEL_PASSWORD = "umar"

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

        label { font-size: 13px; font-weight: 600; color: #16a34a; display: block; margin-top: 12px; margin-bottom: 6px; }
        input, select { width: 100%; padding: 12px; background: #f8fafc; border: 1px solid #cbd5e1; color: #0f172a; border-radius: 8px; font-size: 14px; transition: all 0.2s ease; }
        input:focus, select:focus { border-color: #16a34a; outline: none; background: #fff; box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.1); }
        
        .desc-box { background: #f1f5f9; border: 1px solid #e2e8f0; padding: 12px; border-radius: 8px; margin-top: 12px; font-size: 12px; color: #334155; white-space: pre-line; display: none; line-height: 1.5; }
        
        button { width: 100%; padding: 14px; background: #16a34a; border: none; color: white; font-weight: 600; border-radius: 8px; cursor: pointer; margin-top: 15px; font-size: 15px; transition: background 0.2s; }
        button:hover { background: #15803d; }

        .logout-btn { background: transparent; border: 1px solid #cbd5e1; color: #64748b; margin-top: 8px; }
        .logout-btn:hover { background: #f1f5f9; color: #0f172a; }
        
        .alert { padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 15px; text-align: center; font-weight: 500; }
        .alert-success { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
        .alert-error { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
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
                    {% if logged_in %}
                        <span style="font-size: 12px; color: #16a34a; font-weight: 600;">🔓 Unlocked</span>
                    {% endif %}
                </div>

                {% if error %}
                    <div class="alert alert-error">{{ error }}</div>
                {% endif %}
                {% if message %}
                    <div class="alert alert-success">{{ message }}</div>
                {% endif %}

                {% if not logged_in %}
                    <form method="POST" action="/login">
                        <label>Enter Panel Password</label>
                        <input type="password" name="password" placeholder="Enter password" required>
                        <button type="submit">Access Panel</button>
                    </form>
                {% else %}
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
                        <button type="submit" class="logout-btn">Lock Panel</button>
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
    logged_in = session.get('logged_in', False)
    services = fetch_services() if logged_in else []
    return render_template_string(TEMPLATE, logged_in=logged_in, services=services)

@app.route("/login", methods=["POST"])
def login():
    error = None
    password = request.form.get("password", "").strip()
    if password == PANEL_PASSWORD:
        session['logged_in'] = True
    else:
        error = "Incorrect Password!"
        return render_template_string(TEMPLATE, logged_in=False, error=error)
    return redirect(url_for('home'))

@app.route("/order", methods=["POST"])
def order():
    if not session.get('logged_in', False):
        return redirect(url_for('home'))
    
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
            message = f"Error from Provider: {res_json['error']}"
        else:
            message = "Error: Unexpected response format"
    except Exception as e:
        message = f"Connection Error: {e}"
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (service_name, link, quantity, charge, api_order_id, status) VALUES (?, ?, ?, ?, ?, ?)",
                   (service_name, target_link, quantity, total_charge, api_order_id, message))
    conn.commit()
    conn.close()
    
    return render_template_string(TEMPLATE, logged_in=True, services=services, message=message)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
