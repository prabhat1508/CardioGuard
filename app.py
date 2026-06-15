from flask import Flask, render_template, request
import joblib
import sqlite3
import os

app = Flask(__name__)

# ---------------- DATABASE CREATE ----------------

def init_db():
    conn = sqlite3.connect("patients.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        systolic INTEGER,
        diastolic INTEGER,
        result TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- LOAD BP MODEL ----------------

model = None
label_encoder = None

try:
    model = joblib.load("models/bp_model.joblib")
    label_encoder = joblib.load("models/label_encoder.joblib")
    print("BP Model loaded successfully")
except:
    print("BP model not found")

# ---------------- HOME PAGE ----------------

@app.route('/')
def home():
    return render_template('home.html')

# ---------------- BP PAGE ----------------

@app.route('/predict-page')
def predict_page():
    return render_template('index.html')

# ---------------- BP PREDICTION ----------------

@app.route('/predict', methods=['POST'])
def predict():

    if model is None:
        return render_template("index.html", error="Model not loaded")

    try:

        name = request.form.get("Name")

        input_data = [
            int(request.form.get('C')),
            int(request.form.get('Age')),
            int(request.form.get('History')),
            int(request.form.get('Patient')),
            int(request.form.get('TakeMedication')),
            int(request.form.get('Severity')),
            int(request.form.get('BreathShortness')),
            int(request.form.get('VisualChanges')),
            int(request.form.get('NoseBleeding')),
            int(request.form.get('Whendiagnoused')),
            int(request.form.get('Systolic_Num')),
            int(request.form.get('Diastolic_Num')),
            int(request.form.get('ControlledDiet')),
        ]

        prediction = model.predict([input_data])[0]
        decoded_prediction = label_encoder.inverse_transform([prediction])[0]

        advice_map = {
            "NORMAL": "Your blood pressure is normal.",
            "HYPERTENSION (Stage-1)": "Reduce salt and monitor BP.",
            "HYPERTENSION (Stage-2)": "Consult a doctor.",
            "HYPERTENSIVE CRISIS": "Immediate medical attention required!"
        }

        advice = advice_map.get(decoded_prediction)

        # -------- SAVE DATA TO DATABASE --------

        conn = sqlite3.connect("patients.db")
        cursor = conn.cursor()

        cursor.execute(
        "INSERT INTO patients (name, systolic, diastolic, result) VALUES (?,?,?,?)",
        (name, input_data[10], input_data[11], decoded_prediction)
        )

        conn.commit()
        conn.close()

        return render_template(
            "index.html",
            prediction_text=decoded_prediction,
            advice=advice,
            name=name,
            systolic=input_data[10],
            diastolic=input_data[11]
        )

    except Exception as e:
        return render_template("index.html", error=str(e))


# ---------------- SUGAR PAGE ----------------

@app.route('/sugar-page')
def sugar_page():
    return render_template('sugar.html')


# ---------------- SUGAR PREDICTION ----------------

@app.route('/predict-sugar', methods=['POST'])
def predict_sugar():

    name = request.form.get("Name")
    glucose = int(request.form.get("Glucose"))
    bmi = float(request.form.get("BMI"))
    age = int(request.form.get("Age"))

    if glucose < 100:
        result = "Normal Sugar Level"
        advice = "Maintain healthy diet and exercise."

    elif glucose < 126:
        result = "Prediabetes"
        advice = "Control diet and monitor sugar."

    else:
        result = "High Sugar (Diabetes Risk)"
        advice = "Consult a doctor immediately."

    return render_template(
        "sugar.html",
        prediction_text=result,
        advice=advice,
        name=name,
        glucose=glucose,
        bmi=bmi,
        age=age
    )


# ---------------- DOCTOR PAGE ----------------

@app.route('/doctor-page')
def doctor_page():

    doctors = [
        {"name": "Dr. Rajesh Sharma", "type": "Cardiologist", "phone": "9876543210"},
        {"name": "Dr. Neha Gupta", "type": "Diabetologist", "phone": "9876543211"},
        {"name": "Dr. Amit Verma", "type": "General Physician", "phone": "9876543212"},
        {"name": "Dr. Pooja Singh", "type": "Heart Specialist", "phone": "9876543213"},
        {"name": "Dr. Ankit Jain", "type": "Diabetes Specialist", "phone": "9876543214"},
        {"name": "Dr. Rohit Kumar", "type": "Cardiologist", "phone": "9876543215"},
        {"name": "Dr. Sneha Patel", "type": "General Physician", "phone": "9876543216"},
        {"name": "Dr. Vivek Mehta", "type": "Cardiologist", "phone": "9876543217"},
        {"name": "Dr. Priya Arora", "type": "Diabetologist", "phone": "9876543218"},
        {"name": "Dr. Kunal Shah", "type": "Heart Specialist", "phone": "9876543219"},
    ]

    return render_template("doctor.html", doctors=doctors)


# ---------------- RECORDS PAGE ----------------

@app.route('/records')
def records():

    conn = sqlite3.connect("patients.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    data = cursor.fetchall()

    conn.close()

    return render_template("records.html", data=data)


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    app.run(debug=True)