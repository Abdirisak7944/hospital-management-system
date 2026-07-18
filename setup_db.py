from app import create_app, db
from app.models import Patient, Doctor, Appointment
from datetime import datetime
import os

def setup_database():
    # Tirtir database-ka hore haddii uu jiro
    db_path = 'hospital.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️ Removed old database: {db_path}")
    
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Tables created successfully!")
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📋 Tables in database: {tables}")
        
        # Add sample patients
        patients_data = [
            Patient(name="Ahmed Ali", age=30, gender="Male", phone="612345678", address="Mogadishu"),
            Patient(name="Fatima Hassan", age=25, gender="Female", phone="612345679", address="Hargeisa"),
            Patient(name="Omar Osman", age=45, gender="Male", phone="612345680", address="Kismayo"),
            Patient(name="Amina Abdi", age=28, gender="Female", phone="612345681", address="Baidoa"),
        ]
        
        for patient in patients_data:
            db.session.add(patient)
        
        db.session.commit()
        print(f"✅ {len(patients_data)} patients added successfully!")
        
        # Verify data
        patients = Patient.query.all()
        print("\n📋 Patients in database:")
        print("-" * 50)
        for p in patients:
            print(f"ID: {p.id} | Name: {p.name} | Age: {p.age} | Phone: {p.phone}")
        print("-" * 50)
        print(f"Total patients: {len(patients)}")
        
        print("\n🎉 Database setup completed successfully!")

if __name__ == "__main__":
    setup_database()