from flask import Flask, render_template, request, session, jsonify
from datetime import datetime
from flask_cors import CORS
import os
import json

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_session_storage'
CORS(app)

# History ফাইল এর নাম
HISTORY_FILE = 'bmi_history.json'

# Helper function to load history from file
def load_history():
    """JSON ফাইল থেকে history লোড করে। ফাইল না থাকলে খালি ডিকশনারি রিটার্ন করে।"""
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Helper function to save history to file
def save_history(data):
    """History ডেটা JSON ফাইলে সেভ করে।"""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def convert_height_to_meters(height, unit):
    """বিভিন্ন ইউনিট থেকে উচ্চতাকে মিটারে কনভার্ট করে।"""
    try:
        height = float(height)
    except (ValueError, TypeError):
        return None

    unit = unit.lower()
    if unit == 'cm':
        return height / 100
    elif unit == 'meter':
        return height
    elif unit == 'inch':
        return height * 0.0254
    elif unit == 'feet':
        return height * 0.3048
    elif unit == 'mm':
        return height / 1000
    else:
        return None

def calculate_bmi(weight, height_m):
    """ওজন এবং উচ্চতা (মিটার) থেকে BMI ক্যালকুলেট করে।"""
    try:
        weight = float(weight)
        if height_m is None or height_m <= 0:
            return None
        bmi = weight / (height_m ** 2)
        return round(bmi, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def get_bmi_category(bmi):
    """BMI অনুযায়ী ক্যাটাগরি এবং পরামর্শ রিটার্ন করে।"""
    if bmi < 18.5:
        return "Underweight", "You may need to gain weight."
    elif 18.5 <= bmi < 24.9:
        return "Normal", "You are in a healthy range."
    elif 25 <= bmi < 29.9:
        return "Overweight", "Consider healthier habits."
    else:
        return "Obese", "Talk to a health professional for proper guidance."

@app.route('/', methods=['GET', 'POST'])
def index():
    result = {}
    if 'user_id' not in session:
        session['user_id'] = os.urandom(8).hex()
    user_id = session['user_id']

    if request.method == 'POST':
        weight = request.form.get('weight')
        height = request.form.get('height')
        unit = request.form.get('unit', 'inch')

        height_m = convert_height_to_meters(height, unit)
        bmi = calculate_bmi(weight, height_m)

        if bmi:
            category, advice = get_bmi_category(bmi)
            result['bmi'] = bmi
            result['category'] = category
            result['advice'] = advice

            # History ফাইলে সেভ করার জন্য
            record = {
                'bmi': bmi,
                'category': category,
                'advice': advice,
                'weight': weight,
                'height': height,
                'unit': unit,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            
            # প্রথমে বর্তমান history লোড করুন
            bmi_history_store = load_history()
            # নতুন রেকর্ড যোগ করুন
            user_records = bmi_history_store.get(user_id, [])
            user_records.append(record)
            bmi_history_store[user_id] = user_records
            # আপডেট করা history সেভ করুন
            save_history(bmi_history_store)
            
        else:
            result['error'] = "Invalid input. Please enter valid numbers for weight and height."

    return render_template('index.html', result=result)

@app.route('/history')
def history():
    """নির্দিষ্ট ইউজারের history দেখানোর জন্য পেজ রেন্ডার করে।"""
    user_id = session.get('user_id')
    user_history = []
    if user_id:
        bmi_history_store = load_history()
        # ইউজারের history ডেটা নিন, না থাকলে খালি লিস্ট
        user_history = bmi_history_store.get(user_id, [])
    
    # history.html টেমপ্লেটে ডেটা পাস করুন
    return render_template('history.html', history=user_history)

# একটি API endpoint যা শুধুমাত্র JSON ডেটা রিটার্ন করবে (ঐচ্ছিক)
@app.route('/api/history')
def api_history():
    """শুধুমাত্র JSON ফরম্যাটে ইউজারের history রিটার্ন করে।"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])
        
    bmi_history_store = load_history()
    user_history = bmi_history_store.get(user_id, [])
    return jsonify(user_history)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')


if __name__ == '__main__':
    app.run(debug=True)
