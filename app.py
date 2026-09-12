
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
      followers = [
          s
          for s in data
          if "instagram" in s.get("name", "").lower()
          and "follower" in s.get("name", "").lower()
      ][:12]
      likes = [
          s
          for s in data
          if "instagram" in s.get("name", "").lower()
          and "like" in s.get("name", "").lower()
      ][:12]
      views = [
          s
          for s in data
          if "instagram" in s.get("name", "").lower()
          and ("view" in s.get("name", "").lower() or "reel" in s.get("name", "").lower())
      ][:12]

      combined = followers + likes + views
      if combined:
        return combined
  except Exception:
    pass
  return [
      {"service": "4681", "name": "Instagram Followers (Refill)", "rate": "35.00"},
      {"service": "6243", "name": "Instagram Auto Likes", "rate": "5.00"},
      {"service": "1348", "name": "Instagram Views (Cheapest)", "rate": "0.15"},
  ]


TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Umar Panel | Pro Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; font-family: 'Inter', sans-serif; }
        body { background: #09090b; color: #f4f4f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .dashboard { width: 100%; max-width: 420px; padding: 20px; }
        .card { background: #121215; border: 1px solid #27272a; padding: 30px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
        .brand { text-align: center; margin-bottom: 25px; }
        .brand h2 { margin: 0; font-size: 24px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px; }
        .brand span { color: #f43f5e; }
        .brand p { margin: 5px 0 0; font-size: 13px; color: #a1a1aa; }
        
        label { font-size: 12px; font-weight: 600; color: #a1a1aa; display: block; margin-top: 16px; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
        input, select { width: 100%; padding: 14px; background: #18181b; border: 1px solid #27272a; color: white; border-radius: 8px; font-size: 14px; transition: all 0.2s ease; }
        input:focus, select:focus { border-color: #f43f5e; outline: none; background: #202025; box-shadow: 0 0 0 3px rgba(244, 63, 94, 0.15); }
        
        .price-card { background: #18181b; border: 1px solid #27272a; padding: 14px; border-radius: 8px; margin-top: 20px; display: flex; justify-content: space-between; align-items: center; }
        .price-card span { font-size: 13px; color: #a1a1aa; }
        .price-card h3 { margin: 0; font-size: 18px; color: #34d399; font-weight: 700; }
        
        button { width: 100%; padding: 14px; background: #f43f5e; border: none; color: white; font-weight: 600; border-radius: 8px; cursor: pointer; margin-top: 22px; font-size: 15px; transition: background 0.2s, transform 0.1s; }
        button:hover { background: #e11d48; }
        button:active { transform: scale(0.98); }
        
        .logout-btn { background: transparent; border: 1px solid #27272a; color: #a1a1aa; margin-top: 10px; }
        .logout-btn:hover { background: #18181b; color: #ffffff; border-color: #3f3f46; }
        
        .alert { padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 20px; text-align: center; font-weight: 500; }
        .alert-success { background: rgba(6, 78, 59, 0.4); color: #34d399; border: 1px solid #059669; }
        .alert-error { background: rgba(127, 29, 29, 0.4); color: #fca5a5; border: 1px solid #dc2626; }
    </style>
    <script>
        function calculatePrice() {
            const select = document.getElementById('serviceSelect');
            const qtyInput = document.getElementById('qtyInput');
            const priceDisplay = document.getElementById('priceDisplay');
            
            const selectedOption = select.options[select.selectedIndex];
            const ratePer1000 = parseFloat(selectedOption.getAttribute('data-rate')) || 0;
            const quantity = parseInt(qtyInput.value) || 0;
            
            const totalPrice = (quantity / 1000) * ratePer1000;
            priceDisplay.innerText = "₹ " + totalPrice.toFixed(2);
        }
    </script>
</head>
<body>
    <div class="dashboard">
        <div class="card">
            {% if not logged_in %}
                <div class="brand">
                    <h2>Umar<span>Panel</span></h2>
                    <p>Secure Admin Access</p>
                </div>
                {% if error %}
                    <div class="alert alert-error">{{ error }}</div>
                {% endif %}
                <form method="POST" action="/login">
                    <label>Admin Password</label>
                    <input type="password" name="password" placeholder="Enter secure password" required>
                    <button type="submit">Authenticate</button>
                </form>
            {% else %}
                <div class="brand">
                    <h2>Umar<span>Panel</span></h2>
                    <p>Managed by Umar Ali</p>
                </div>
                {% if message %}
                    <div class="alert {{ 'alert-success' if 'Success' in message or 'ID' in message else 'alert-error' }}">{{ message }}</div>
                {% endif %}
                <form method="POST" action="/order">
                    <label>Select Service</label>
                    <select name="service" id="serviceSelect" onchange="calculatePrice()" required>
                        <option value="" disabled selected>Choose a service...</option>
                        {% for s in services %}
                            <option value="{{ s.service }}" data-rate="{{ s.rate }}">{{ s.name }} (₹{{ s.rate }}/1k)</option>
                        {% endfor %}
                    </select>
                    
                    <label>Target URL / Link or Username</label>
                    <input type="text" name="link" placeholder="Link ya Username daalein" required>
                    
                    <label>Quantity</label>
                    <input type="number" name="quantity" id="qtyInput" oninput="calculatePrice()" placeholder="Enter quantity" required>
                    
                    <label>Username (Agar service maange)</label>
                    <input type="text" name="username" placeholder="Optional / Username agar zaroori ho">
                    
                    <div class="price-card">
                        <span>Estimated Total</span>
                        <h3 id="priceDisplay">₹ 0.00</h3>
                    </div>
                    
                    <button type="submit">Place Order</button>
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
  logged_in = session.get("logged_in", False)
  services = fetch_services() if logged_in else []
  return render_template_string(
      TEMPLATE, logged_in=logged_in, services=services
  )


@app.route("/login", methods=["POST"])
def login():
  password = request.form.get("password")
  if password == PANEL_PASSWORD:
    session["logged_in"] = True
    return redirect(url_for("home"))
  else:
    return render_template_string(
        TEMPLATE, logged_in=False, error="Invalid Password Provided!"
    )


@app.route("/order", methods=["POST"])
def order():
  if not session.get("logged_in"):
    return redirect(url_for("home"))

  service_id = request.form.get("service")
  target_link = request.form.get("link")
  quantity = request.form.get("quantity")
  username = request.form.get("username")

  payload = {
      "key": API_KEY,
      "action": "add",
      "service": service_id,
      "link": target_link,
      "quantity": quantity,
  }

  if username:
    payload["username"] = username

  try:
    response = requests.post(API_URL, data=payload)
    res_json = response.json()
    if "order" in res_json:
      message = f"Success! Order ID: {res_json['order']}"
    else:
      message = f"Error: {res_json.get('error', 'API rejected order')}"
  except Exception as e:
    message = f"Connection Error: {e}"

  services = fetch_services()
  return render_template_string(
      TEMPLATE, logged_in=True, services=services, message=message
  )


@app.route("/logout", methods=["POST"])
def logout():
  session.pop("logged_in", None)
  return redirect(url_for("home"))


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
