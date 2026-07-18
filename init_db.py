from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define models
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('Patient', backref='appointments')
    doctor = db.relationship('Doctor', backref='appointments')

# Create database and add data
with app.app_context():
    # Create all tables
    db.create_all()
    print("✅ Tables created successfully!")
    
    # Add sample patients
    patients = [
        Patient(name="Ahmed Ali", age=30, gender="Male", phone="612345678", address="Mogadishu"),
        Patient(name="Fatima Hassan", age=25, gender="Female", phone="612345679", address="Hargeisa"),
        Patient(name="Omar Osman", age=45, gender="Male", phone="612345680", address="Kismayo"),
        Patient(name="Amina Abdi", age=28, gender="Female", phone="612345681", address="Baidoa"),
    ]
    
    for patient in patients:
        db.session.add(patient)
    
    db.session.commit()
    print(f"✅ {len(patients)} patients added successfully!")
    
    # Verify
    all_patients = Patient.query.all()
    print("\n📋 Patients in database:")
    print("-" * 50)
    for p in all_patients:
        print(f"ID: {p.id} | Name: {p.name} | Age: {p.age} | Phone: {p.phone}")
    print("-" * 50)
    print(f"Total: {len(all_patients)} patients")
    
    print("\n🎉 Database setup completed successfully!")

print("Done!")