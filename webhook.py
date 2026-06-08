from flask import Flask, request
import json
import os

app = Flask(__name__)
DB_FILE = "users.json"

def upgrade_user(email, plan_name):
    """This small function updates your 'Diary' file"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            db = json.load(f)
        
        # Change them to Pro or Student automatically!
        db[email] = {"usage": 0, "plan": plan_name}
        
        with open(DB_FILE, "w") as f:
            json.dump(db, f)

# --- THE PAYPAL DOOR ---
@app.route('/paypal-webhook', methods=['POST'])
def paypal_payment():
    # PayPal sends data in a 'form' format
    data = request.form.to_dict()
    email = data.get('payer_email')
    item = data.get('item_name') # You name your PayPal button 'Pro' or 'Student'

    if email and data.get('payment_status') == 'Completed':
        plan = "Pro" if "Pro" in item else "Student"
        upgrade_user(email, plan)
        return "OK", 200
    return "Error", 400

# --- THE RAZORPAY DOOR ---
@app.route('/razorpay-webhook', methods=['POST'])
def razorpay_payment():
    data = request.json
    email = data.get('payload', {}).get('payment', {}).get('entity', {}).get('email')
    amount = data.get('payload', {}).get('payment', {}).get('entity', {}).get('amount')

    if email:
        plan = "Pro" if amount >= 29900 else "Student"
        upgrade_user(email, plan)
        return "OK", 200
    return "Error", 400

if __name__ == '__main__':
    app.run(port=5000)