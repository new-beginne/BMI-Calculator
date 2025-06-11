from flask import Flask, render_template, request, session, jsonify
from datetime import datetime
from flask_cors import CORS
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_session_storage'
CORS(app)

bmi_history_store = {}

def convert_height_to_meters(height, unit):
    try:
        height = float(height)
    except ValueError:
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
    try:
        weight = float(weight)
        bmi = weight / (height_m ** 2)
        return round(bmi, 2)
    except:
        return None

def get_bmi_category(bmi):
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

        if height_m and height_m > 0:
            bmi = calculate_bmi(weight, height_m)
            if bmi:
                category, advice = get_bmi_category(bmi)
                result['bmi'] = bmi
                result['category'] = category
                result['advice'] = advice

                # Store result in session-based history
                record = {
                    'bmi': bmi,
                    'category': category,
                    'advice': advice,
                    'weight': weight,
                    'height': height,
                    'unit': unit,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                bmi_history_store.setdefault(user_id, []).append(record)
            else:
                result['error'] = "Invalid input for weight or height."
        else:
            result['error'] = "Please enter a valid height."

    return render_template('index.html', result=result)

@app.route('/history')
def history():
    user_id = session.get('user_id')
    if not user_id or user_id not in bmi_history_store:
        return jsonify([])
    return jsonify(bmi_history_store[user_id])

if __name__ == '__main__':
    app.run(debug=True)
