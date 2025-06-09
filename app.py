from flask import Flask, render_template, request

app = Flask(__name__)

def convert_height_to_meters(height, unit):
    """
    Height কে মিটারে রূপান্তর করে।
    """
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
    if request.method == 'POST':
        weight = request.form.get('weight')
        height = request.form.get('height')
        unit = request.form.get('unit', 'inch')  # Default to 'inch'

        height_m = convert_height_to_meters(height, unit)

        if height_m and height_m > 0:
            bmi = calculate_bmi(weight, height_m)
            if bmi:
                category, advice = get_bmi_category(bmi)
                result['bmi'] = bmi
                result['category'] = category
                result['advice'] = advice
            else:
                result['error'] = "Invalid input for weight or height."
        else:
            result['error'] = "Please enter a valid height."
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)

