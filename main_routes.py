from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Patient, Doctor, Appointment, User
from app.forms import PatientForm, LoginForm, RegisterForm, DoctorForm, AppointmentForm
from app import db
from sqlalchemy import or_, func
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main_bp.route('/about')
def about():
    if current_user.is_authenticated:
        return render_template('about.html')
    return redirect(url_for('main.login'))

@main_bp.route('/contact')
def contact():
    if current_user.is_authenticated:
        return render_template('contact.html')
    return redirect(url_for('main.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        total_patients = Patient.query.count()
        total_doctors = Doctor.query.count()
        total_appointments = Appointment.query.count()
        recent_patients = Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
        male_count = Patient.query.filter_by(gender='Male').count()
        female_count = Patient.query.filter_by(gender='Female').count()
        
        return render_template('dashboard.html', 
                             total_patients=total_patients,
                             total_doctors=total_doctors,
                             total_appointments=total_appointments,
                             recent_patients=recent_patients,
                             male_count=male_count,
                             female_count=female_count)
    except Exception as e:
        print(f"Dashboard error: {e}")
        return render_template('dashboard.html', 
                             total_patients=0,
                             total_doctors=0,
                             total_appointments=0,
                             recent_patients=[],
                             male_count=0,
                             female_count=0)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html', form=form)

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    flash('Registration is currently disabled. Please contact admin.', 'danger')
    return redirect(url_for('main.login'))

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main_bp.route('/patients')
@login_required
def patients():
    search_query = request.args.get('search', '')
    
    if search_query:
        all_patients = Patient.query.filter(
            or_(
                Patient.name.ilike(f'%{search_query}%'),
                Patient.phone.ilike(f'%{search_query}%'),
                Patient.address.ilike(f'%{search_query}%')
            )
        ).all()
    else:
        all_patients = Patient.query.all()
    
    return render_template('patients.html', patients=all_patients, search_query=search_query)

@main_bp.route('/add_patient', methods=['GET', 'POST'])
@login_required
def add_patient():
    form = PatientForm()
    
    if form.validate_on_submit():
        new_patient = Patient(
            name=form.name.data,
            age=form.age.data,
            gender=form.gender.data,
            phone=form.phone.data,
            address=form.address.data
        )
        
        db.session.add(new_patient)
        db.session.commit()
        
        flash(f'Patient {new_patient.name} added successfully!', 'success')
        return redirect(url_for('main.patients'))
    
    return render_template('add_patient.html', form=form)

@main_bp.route('/edit_patient/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_patient(id):
    patient = Patient.query.get_or_404(id)
    form = PatientForm()
    
    if form.validate_on_submit():
        patient.name = form.name.data
        patient.age = form.age.data
        patient.gender = form.gender.data
        patient.phone = form.phone.data
        patient.address = form.address.data
        
        db.session.commit()
        flash(f'Patient {patient.name} updated successfully!', 'success')
        return redirect(url_for('main.patients'))
    
    elif request.method == 'GET':
        form.name.data = patient.name
        form.age.data = patient.age
        form.gender.data = patient.gender
        form.phone.data = patient.phone
        form.address.data = patient.address
    
    return render_template('edit_patient.html', form=form, patient=patient)

@main_bp.route('/delete_patient/<int:id>', methods=['POST'])
@login_required
def delete_patient(id):
    patient = Patient.query.get_or_404(id)
    name = patient.name
    db.session.delete(patient)
    db.session.commit()
    flash(f'Patient {name} deleted successfully!', 'success')
    return redirect(url_for('main.patients'))

@main_bp.route('/doctors')
@login_required
def doctors():
    all_doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=all_doctors)

@main_bp.route('/add_doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():
    form = DoctorForm()
    
    if form.validate_on_submit():
        # Check if email already exists
        existing_doctor = Doctor.query.filter_by(email=form.email.data).first()
        if existing_doctor:
            flash('A doctor with this email already exists!', 'danger')
        else:
            new_doctor = Doctor(
                name=form.name.data,
                specialization=form.specialization.data,
                phone=form.phone.data,
                email=form.email.data
            )
            
            db.session.add(new_doctor)
            db.session.commit()
            
            flash(f'Doctor {new_doctor.name} added successfully!', 'success')
            return redirect(url_for('main.doctors'))
    
    return render_template('add_doctor.html', form=form)

@main_bp.route('/edit_doctor/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    form = DoctorForm()
    
    if form.validate_on_submit():
        # Check if email already exists for another doctor
        existing_doctor = Doctor.query.filter(Doctor.email == form.email.data, Doctor.id != id).first()
        if existing_doctor:
            flash('A doctor with this email already exists!', 'danger')
        else:
            doctor.name = form.name.data
            doctor.specialization = form.specialization.data
            doctor.phone = form.phone.data
            doctor.email = form.email.data
            
            db.session.commit()
            flash(f'Doctor {doctor.name} updated successfully!', 'success')
            return redirect(url_for('main.doctors'))
    
    elif request.method == 'GET':
        form.name.data = doctor.name
        form.specialization.data = doctor.specialization
        form.phone.data = doctor.phone
        form.email.data = doctor.email
    
    return render_template('edit_doctor.html', form=form, doctor=doctor)

@main_bp.route('/delete_doctor/<int:id>', methods=['POST'])
@login_required
def delete_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    name = doctor.name
    db.session.delete(doctor)
    db.session.commit()
    flash(f'Doctor {name} deleted successfully!', 'success')
    return redirect(url_for('main.doctors'))

@main_bp.route('/appointments')
@login_required
def appointments():
    all_appointments = Appointment.query.all()
    return render_template('appointments.html', appointments=all_appointments)

@main_bp.route('/add_appointment', methods=['GET', 'POST'])
@login_required
def add_appointment():
    form = AppointmentForm()
    
    # Populate dropdown choices
    form.patient_id.choices = [(p.id, f"{p.name} (ID: {p.id})") for p in Patient.query.order_by(Patient.name).all()]
    form.doctor_id.choices = [(d.id, f"Dr. {d.name} ({d.specialization})") for d in Doctor.query.order_by(Doctor.name).all()]
    
    if not form.patient_id.choices:
        flash('Please add a patient first before creating an appointment!', 'warning')
        return redirect(url_for('main.add_patient'))
    
    if not form.doctor_id.choices:
        flash('Please add a doctor first before creating an appointment!', 'warning')
        return redirect(url_for('main.add_doctor'))
    
    if form.validate_on_submit():
        # Combine date and time
        appointment_datetime = datetime.combine(form.date.data, form.time.data)
        
        new_appointment = Appointment(
            patient_id=form.patient_id.data,
            doctor_id=form.doctor_id.data,
            date=appointment_datetime,
            status=form.status.data
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        
        patient = Patient.query.get(form.patient_id.data)
        doctor = Doctor.query.get(form.doctor_id.data)
        
        flash(f'Appointment scheduled for {patient.name} with Dr. {doctor.name} on {appointment_datetime.strftime("%Y-%m-%d %H:%M")}!', 'success')
        return redirect(url_for('main.appointments'))
    
    return render_template('add_appointment.html', form=form)