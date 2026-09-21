from flask import Flask, redirect, render_template_string, request, session, url_for
import requests

app = Flask(__name__)
app.secret_key = "umar_secret_key_123"

API_URL = "https://cheapestsmmpanels.com/api/v2"
API_KEY = "7f10f519fa301e5ac7ef9109abe3487e"
PANEL_PASSWORD = "UMAR ALI 007"

def fetch_services():
    try:
        response = requests.post(API_URL, data={"key": API_KEY, "action": "services"})
        data = response.json()
        if isinstance(data, list):
            filtered = []
            for s in data:
                name_lower = s.get('name', '').lower()
                cat_lower = s.get('category', '').lower()
                if 'instagram' in name_lower or 'instagram' in cat_lower:
                    if any(keyword in name_lower for keyword in ['follower', 'like', 'view', 'reel', 'post', 'comment']):
                        filtered.append(s)
            return filtered if filtered else data[:20]
    except Exception:
        pass
    return []

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AS illusion</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        body { background: #f8fafc; color: #1e293b; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; overflow-x: hidden; }
        
        /* Intro Splash Animation Screen */
        #splash-screen {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: #ffffff;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            animation: fadeOut 0.5s ease 1.2s forwards;
        }
        .splash-logo {
            font-size: 28px;
            font-weight: 700;
            letter-spacing: 1px;
            animation: scaleUp 0.8s ease infinite alternate;
        }
        .splash-logo .red-text { color: #dc2626; }
        .splash-logo .green-text { color: #16a34a; }
        .spinner {
            width: 35px;
            height: 35px;
            border: 3px solid #e2e8f0;
            border-top: 3px solid #16a34a;
            border-radius: 50%;
            margin-top: 20px;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes scaleUp {
            0% { transform: scale(0.95); opacity: 0.8; }
            100% { transform: scale(1.05); opacity: 1; }
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @keyframes fadeOut {
            0% { opacity: 1; visibility: visible; }
            100% { opacity: 0; visibility: hidden; }
        }

        /* Cool Lightning & Glowing Order Animation Overlay */
        #order-loading {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(6px);
            justify-content: center;
            align-items: center;
            z-index: 9998;
            animation: flashBg 0.3s ease;
        }
        .lightning-box {
            background: #ffffff;
            padding: 30px 40px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 0 30px rgba(22, 163, 74, 0.5), 0 0 60px rgba(220, 38, 38, 0.3);
            border: 2px solid #16a34a;
            animation: pulseGlow 1s infinite alternate;
        }
        .lightning-icon {
            font-size: 36px;
            margin-bottom: 10px;
            animation: bounceLightning 0.6s infinite alternate;
        }
        .order-loading-text {
            font-size: 15px;
            font-weight: 700;
            background: linear-gradient(45deg, #dc2626, #16a34a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 0.5px;
        }

        @keyframes flashBg {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        @keyframes pulseGlow {
            0% { box-shadow: 0 0 15px rgba(22, 163, 74, 0.4); transform: scale(0.98); }
            100% { box-shadow: 0 0 35px rgba(220, 38, 38, 0.6); transform: scale(1.02); }
        }
        @keyframes bounceLightning {
            0% { transform: translateY(0); filter: drop-shadow(0 0 2px #16a34a); }
            100% { transform: translateY(-8px); filter: drop-shadow(0 0 10px #dc2626); }
        }

        /* Main Dashboard Styles */
        .dashboard { width: 100%; max-width: 440px; padding: 15px; animation: fadeInDashboard 0.8s ease 1.2s both; }
        @keyframes fadeInDashboard {
            0% { opacity: 0; transform: translateY(15px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        .card { background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #dc2626; padding: 24px; border-radius: 14px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
        .brand { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #f1f5f9; padding-bottom: 12px; }
        .brand h2 { margin: 0; font-size: 22px; font-weight: 700; letter-spacing: 0.5px; }
        .brand .red-text { color: #dc2626; }
        .brand .green-text { color: #16a34a; }
        .menu-icon { font-size: 20px; cursor: pointer; color: #64748b; }
        
        label { font-size: 13px; font-weight: 600; color: #16a34a; display: block; margin-top: 14px; margin-bottom: 6px; }
        input, select { width: 100%; padding: 12px; background: #f8fafc; border: 1px solid #cbd5e1; color: #0f172a; border-radius: 8px; font-size: 14px; transition: all 0.2s ease; }
        input:focus, select:focus { border-color: #16a34a; outline: none; background: #fff; box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.1); }
        
        .desc-box { background: #f1f5f9; border: 1px solid #e2e8f0; padding: 12px; border-radius: 8px; margin-top: 12px; font-size: 12px; color: #334155; white-space: pre-line; display: none; line-height: 1.5; }
        .helper-text { font-size: 11px; color: #64748b; margin-top: 4px; }
        
        button { width: 100%; padding: 14px; background: #16a34a; border: none; color: white; font-weight: 600; border-radius: 8px; cursor: pointer; margin-top: 20px; font-size: 15px; transition: background 0.2s; }
        button:hover { background: #15803d; }
        
        .logout-btn { background: transparent; border: 1px solid #cbd5e1; color: #64748b; margin-top: 10px; }
        .logout-btn:hover { background: #f1f5f9; color: #0f172a; }
        
        .alert { padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 15px; text-align: center; font-weight: 500; }
        .alert-success { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
        .alert-error { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
    </style>
    <script>
        function updateServiceDetails() {
            const select = document.getElementById('serviceSelect');
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

        function showOrderLoading() {
            document.getElementById('order-loading').style.display = 'flex';
        }
    </script>
</head>
<body>
    <!-- Splash Animation Screen -->
    <div id="splash-screen">
        <div class="splash-logo">
            <span class="red-text">AS</span> <span class="green-text">illusion</span>
        </div>
        <div class="spinner"></div>
    </div>

    <!-- Lightning Glowing Order Animation Overlay -->
    <div id="order-loading">
        <div class="lightning-box">
            <div class="lightning-icon">⚡</div>
            <div class="order-loading-text">Processing Order...</div>
        </div>
    </div>

    <div class="dashboard">
        <div class="card">
            <div class="brand">
                <h2><span class="red-text">AS</span> <span class="green-text">illusion</span></h2>
                <span class="menu-icon">☰</span>
            </div>
            {% if not logged_in %}
                {% if error %}
                    <div class="alert alert-error">{{ error }}</div>
                {% endif %}
                <form method="POST" action="/login">
                    <label>Admin Password</label>
                    <input type="password" name="password" placeholder="Enter password" required>
                    <button type="submit">Login</button>
                </form>
            {% else %}
                {% if message %}
                    <div class="alert {{ 'alert-success' if 'Success' in message or 'ID' in message else 'alert-error' }}">{{ message }}</div>
                {% endif %}
                <form method="POST" action="/order" onsubmit="showOrderLoading()">
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
                    <div class="helper-text">Enter required quantity</div>
                    
                    <label>Charge</label>
                    <input type="text" id="chargeInput" value="₹ 0.00" disabled style="background: #e2e8f0; font-weight: bold; color: #16a34a;">
                    
                    <button type="submit">Submit Order</button>
                </form>
                <form method="POST" action="/logout">
                    <button type="submit" class="logout-btn">Sign Out</button>
                </form>
            {% endif %}
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
    password = request.form.get("password")
    if password == PANEL_PASSWORD:
        session['logged_in'] = True
        return redirect(url_for('home'))
    else:
        return render_template_string(TEMPLATE, logged_in=False, error="Invalid Password Provided!")

@app.route("/order", methods=["POST"])
def order():
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    
    service_id = request.form.get("service")
    target_link = request.form.get("link", "").strip()
    quantity = request.form.get("quantity")
    
    if "instagram.com/" in target_link:
        target_link = target_link.split("?")[0].rstrip("/")
    
    payload = {
        'key': API_KEY,
        'action': 'add',
        'service': service_id,
        'link': target_link,
        'quantity': quantity
    }
    
    try:
        response = requests.post(API_URL, data=payload)
        res_json = response.json()
        if 'order' in res_json:
            message = f"Success! Order ID: {res_json['order']}"
        else:
            message = f"Error: {res_json.get('error', 'API rejected order')}"
    except Exception as e:
        message = f"Connection Error: {e}"
        
    services = fetch_services()
    return render_template_string(TEMPLATE, logged_in=True, services=services, message=message)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
