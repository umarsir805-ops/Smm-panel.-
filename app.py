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
      ig_services = [
          s
          for s in data
          if "instagram" in s.get("name", "").lower()
          and any(k in s.get("name", "").lower() for k in ["follower", "like", "view"])
      ]
      return ig_services[:30] if ig_services else data[:20]
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
    <title>Professional SMM Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; background: #000000; color: #ffffff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: #121212; border: 1px solid #27272a; padding: 25px; border-radius: 12px; width: 360px; box-shadow: 0 8px 24px rgba(0,0,0,0.8); box-sizing: border-box; }
        h2 { text-align: center; margin-bottom: 20px; font-size: 22px; color: #f43f5e; }
        label { font-size: 13px; color: #a1a1aa; display: block; margin-top: 10px; }
        input, select { width: 100%; padding: 12px; margin-top: 5px; background: #18181b; border: 1px solid #3f3f46; color: white; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        input:focus, select:focus { border-color: #f43f5e; outline: none; }
        .price-box { background: #1e1e24; border: 1px dashed #f43f5e; padding: 10px; border-radius: 6px; margin-top: 12px; text-align: center; font-size: 14px; color: #34d399; font-weight: bold; }
        button { width: 100%; padding: 12px; background: #f43f5e; border: none; color: white; font-weight: bold; border-radius: 6px; cursor: pointer; margin-top: 18px; font-size: 15px; transition: background 0.2s; }
        button:hover { background: #e11d48; }
        .logout { background: #27272a; color: #f43f5e; margin-top: 12px; }
        .logout:hover { background: #3f3f46; }
        .msg { background: #064e3b; color: #34d399; padding: 10px; border-radius: 6px; text-align: center; font-size: 13px; margin-bottom: 15px; border: 1px solid #059669; }
        .error { background: #7f1d1d; color: #fca5a5; padding: 10px; border-radius: 6px; text-align: center; font-size: 13px; margin-bottom: 15px; border: 1px solid #dc2626; }
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
            priceDisplay.innerText = "Total Price: ₹ " + totalPrice.toFixed(2);
        }
    </script>
</head>
<body>
    <div class="card">
        {% if not logged_in %}
            <h2>🔒 Admin Login</h2>
            {% if error %}
                <p class="error">{{ error }}</p>
            {% endif %}
            <form method="POST" action="/login">
                <label>Enter Password:</label>
                <input type="password" name="password" placeholder="Password daalein" required>
                <button type="submit">Login</button>
            </form>
        {% else %}
            <h2>⚡ Pro SMM Panel</h2>
            {% if message %}
                <p class="{{ 'msg' if 'Success' in message or 'ID' in message else 'error' }}">{{ message }}</p>
            {% endif %}
            <form method="POST" action="/order">
                <label>Select Service:</label>
                <select name="service" id="serviceSelect" onchange="calculatePrice()" required>
                    <option value="" disabled selected>Service Chuniye</option>
                    {% for s in services %}
                        <option value="{{ s.service }}" data-rate="{{ s.rate }}">{{ s.name }} (₹{{ s.rate }}/1k)</option>
                    {% endfor %}
                </select>
                
                <label>Instagram Link:</label>
                <input type="text" name="link" placeholder="Profile ya Post ka Link" required>
                
                <label>Quantity:</label>
                <input type="number" name="quantity" id="qtyInput" oninput="calculatePrice()" placeholder="Quantity daalein" required>
                
                <div class="price-box" id="priceDisplay">Total Price: ₹ 0.00</div>
                
                <button type="submit">Place Order</button>
            </form>
            <form method="POST" action="/logout">
                <button type="submit" class="logout">Logout</button>
            </form>
        {% endif %}
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
        TEMPLATE, logged_in=False, error="Galat Password!"
    )


@app.route("/order", methods=["POST"])
def order():
  if not session.get("logged_in"):
    return redirect(url_for("home"))

  service_id = request.form.get("service")
  target_link = request.form.get("link")
  quantity = request.form.get("quantity")

  payload = {
      "key": API_KEY,
      "action": "add",
      "service": service_id,
      "link": target_link,
      "quantity": quantity,
  }

  try:
    response = requests.post(API_URL, data=payload)
    res_json = response.json()
    if "order" in res_json:
      message = f"Success! Order ID: {res_json['order']}"
    else:
      message = f"Error: {res_json.get('error', 'Kuch gadbad hai')}"
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
