from flask import Flask, redirect, render_template_string, request, session, url_for
import requests

app = Flask(__name__)
app.secret_key = "umar_secret_key_123"

API_URL = "https://cheapestsmmpanels.com/api/v2"
API_KEY = "a80914253900dbf6ff33b16a59fb9ecb"
PANEL_PASSWORD = "UMAR ALI 007"

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Private SMM Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; background: #000000; color: #ffffff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: #121212; border: 1px solid #27272a; padding: 25px; border-radius: 12px; width: 340px; box-shadow: 0 8px 24px rgba(0,0,0,0.8); box-sizing: border-box; }
        h2 { text-align: center; margin-bottom: 20px; font-size: 22px; color: #f43f5e; }
        label { font-size: 13px; color: #a1a1aa; display: block; margin-top: 10px; }
        input, select { width: 100%; padding: 12px; margin-top: 5px; background: #18181b; border: 1px solid #3f3f46; color: white; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        input:focus, select:focus { border-color: #f43f5e; outline: none; }
        button { width: 100%; padding: 12px; background: #f43f5e; border: none; color: white; font-weight: bold; border-radius: 6px; cursor: pointer; margin-top: 18px; font-size: 15px; transition: background 0.2s; }
        button:hover { background: #e11d48; }
        .logout { background: #27272a; color: #f43f5e; margin-top: 12px; }
        .logout:hover { background: #3f3f46; }
        .msg { background: #064e3b; color: #34d399; padding: 10px; border-radius: 6px; text-align: center; font-size: 13px; margin-bottom: 15px; border: 1px solid #059669; }
        .error { background: #7f1d1d; color: #fca5a5; padding: 10px; border-radius: 6px; text-align: center; font-size: 13px; margin-bottom: 15px; border: 1px solid #dc2626; }
    </style>
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
            <h2>⚡ SMM Order Panel</h2>
            {% if message %}
                <p class="{{ 'msg' if 'Success' in message or 'ID' in message else 'error' }}">{{ message }}</p>
            {% endif %}
            <form method="POST" action="/order">
                <label>Select Category / Service:</label>
                <select name="service" required>
                    <option value="" disabled selected>Service Chuniye</option>
                    <option value="4681">Instagram Followers (Refill)</option>
                    <option value="COM_SERVICE_ID">Instagram Likes</option>
                    <option value="COM_SERVICE_ID">Instagram Views</option>
                </select>
                
                <label>Service ID (Custom ya Upar Wali):</label>
                <input type="text" name="service_id_manual" placeholder="Jaise: 4681 (agar upar se na chunein)" required>
                
                <label>Instagram Link:</label>
                <input type="text" name="link" placeholder="Profile ya Post ka Link" required>
                
                <label>Quantity:</label>
                <input type="number" name="quantity" placeholder="Quantity daalein" required>
                
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
  return render_template_string(TEMPLATE, logged_in=logged_in)


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

  # Agar dropdown se select kiya ya manual dala, dono handle karega
  service_id = request.form.get("service_id_manual") or request.form.get(
      "service"
  )
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

  return render_template_string(
      TEMPLATE, logged_in=True, message=message
  )


@app.route("/logout", methods=["POST"])
def logout():
  session.pop("logged_in", None)
  return redirect(url_for("home"))


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
