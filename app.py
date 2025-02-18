from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, time
import os
from models import User, Appointment, MedicalRecord, Prescription, db  # Import the models and db
from forms import LoginForm, RegistrationForm, AddDoctorForm, AddStaffForm, ResourceForm, PricingForm, InventoryForm, AppointmentForm, MedicalRecordForm, DoctorSearchForm, PrescriptionForm, DoctorAppointmentForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email
from flask_wtf import FlaskForm

app = Flask(__name__)
app.config.from_pyfile('config.py')  # Load configuration from config.py

# Add database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use SQLite database
# Optional: Disable track modifications for less overhead
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Add a secret key for Flask-Login

# Initialize the database with the app
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        name = f"{first_name} {last_name}"  # Combine first and last name

        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))

        new_user = User()
        new_user.email = email
        new_user.set_password(password)
        new_user.role = 'patient'  # Assign 'patient' role
        new_user.name = name
        db.session.add(new_user)
        db.session.commit()

        # Log the user in after registration
        login_user(new_user)

        print(f"New user registered with role: patient")  # Check the assigned role

        return redirect(url_for('profile'))
    return render_template('auth/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next') # Check if there is next page
            return redirect(next_page or url_for('index')) # Redirect to the next page if any or index
        else:
            flash('Invalid email or password')
    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    now = datetime.now()
    appointments = Appointment.query.filter_by(patient_id=current_user.id).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    medical_records = MedicalRecord.query.filter_by(patient_id=current_user.id).all()
    return render_template('patient/profile.html', appointments=appointments, medical_records=medical_records, now=now)

@app.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if current_user.role != 'patient':
        return "You are not authorized to access this page."
    form = AppointmentForm()
    form.doctor.choices = [(doctor.id, f"{doctor.name} ({doctor.specialization})") for doctor in User.query.filter_by(role='doctor').all()]
    if form.validate_on_submit():
        # Construct the appointment time from hours and minutes
        appointment_time = time(hour=form.hours.data, minute=form.minutes.data)
        appointment = Appointment(
            appointment_date=form.date.data,
            appointment_time=appointment_time,
            patient_id=current_user.id,
            doctor_id=form.doctor.data
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Your appointment has been booked!', 'success')
        return redirect(url_for('profile'))
    return render_template('patient/appointments.html', form=form)

@app.route('/book_appointment/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def book_doctor_appointment(doctor_id):
    if current_user.role != 'patient':
        return "You are not authorized to access this page."
    form = AppointmentForm()
    # Filter the doctor choices to only include the selected doctor
    form.doctor.choices = [(doctor_id, f"{db.session.get(User, doctor_id).name} ({db.session.get(User, doctor_id).specialization})")]
    if form.validate_on_submit():
        appointment_time = time(hour=form.hours.data, minute=form.minutes.data)
        appointment = Appointment(
            appointment_date=form.date.data,
            appointment_time=appointment_time,
            patient_id=current_user.id,
            doctor_id=doctor_id  # Use the doctor_id from the URL
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Your appointment has been booked!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'POST':
        # If the form is submitted but not valid, print the errors
        print(form.errors)
    return render_template('patient/appointments.html', form=form)

# Doctor routes
@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        return "You are not authorized to access this page."
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).all() # Get all appointments for the current doctor
    return render_template('doctor/dashboard.html', appointments=appointments)

@app.route('/doctor/add_report/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def add_report(appointment_id):
    if current_user.role != 'doctor':
        return "You are not authorized to access this page."
    appointment = Appointment.query.get_or_404(appointment_id)
    if request.method == 'POST':
        report_text = request.form.get('report')
        if report_text:
            medical_record = MedicalRecord(patient_id=appointment.patient_id, report=report_text)
            db.session.add(medical_record)
            db.session.commit()
            appointment.medical_record_id = medical_record.id # Link the appointment to the medical record
            db.session.commit()
            flash('Medical report added successfully!')
            return redirect(url_for('doctor_dashboard'))
        else:
            flash('Please enter a medical report.')
    return render_template('doctor/medical_report.html', appointment=appointment)

@app.route('/doctor/add_medical_record/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def add_medical_record(appointment_id):
    if current_user.role != 'doctor':
        return "You are not authorized to access this page."
    appointment = Appointment.query.get_or_404(appointment_id)
    form = MedicalRecordForm()
    if form.validate_on_submit():
        medical_record = MedicalRecord(
            patient_id=appointment.patient_id,
            report=form.report.data
        )
        db.session.add(medical_record)
        db.session.commit()
        flash('Medical record added successfully!')
        return redirect(url_for('doctor_dashboard'))
    return render_template('doctor/add_medical_record.html', form=form, appointment=appointment)

@app.route('/doctor/search_patients', methods=['GET', 'POST'])
@login_required
def search_patients():
    if current_user.role != 'doctor':
        return "You are not authorized to access this page."
    form = DoctorSearchForm()
    patients = User.query.filter_by(role='patient').all()  # Default to all patients
    if form.validate_on_submit():
        search_term = form.search_term.data
        search_by = form.search_by.data
        if search_by == 'name':
            patients = User.query.filter(User.name.ilike(f'%{search_term}%'), User.role == 'patient').all()
        elif search_by == 'id':
            patients = User.query.filter(User.id == search_term, User.role == 'patient').all()
        elif search_by == 'diagnosis':
            patients = User.query.join(MedicalRecord).filter(MedicalRecord.report.ilike(f'%{search_term}%'), User.role == 'patient').all()
    return render_template('doctor/search_patients.html', form=form, patients=patients)

@app.route('/doctor/issue_prescription', methods=['GET', 'POST'])
@login_required
def issue_prescription():
    if current_user.role != 'doctor':
        return "You are not authorized to access this page."
    form = PrescriptionForm()
    form.patient.choices = [(patient.id, patient.name) for patient in User.query.filter_by(role='patient').all()]
    patient_id = request.args.get('patient_id', type=int)
    if patient_id:
        form.patient.data = patient_id  # Pre-select the patient
    if form.validate_on_submit():
        prescription = Prescription(
            doctor_id=current_user.id,
            patient_id=form.patient.data,
            medication=form.medication.data,
            dosage=form.dosage.data,
            instructions=form.instructions.data
        )
        db.session.add(prescription)
        db.session.commit()
        flash('Prescription issued successfully!', 'success')
        return redirect(url_for('doctor_dashboard'))
    return render_template('doctor/issue_prescription.html', form=form)

@app.route('/doctor/patient_profile/<int:patient_id>')
@login_required
def patient_profile(patient_id):
    if current_user.role != 'doctor':
        return "You are not authorized to access this page."
    patient = User.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    medical_records = MedicalRecord.query.filter_by(patient_id=patient.id).all()
    prescriptions = Prescription.query.filter_by(patient_id=patient.id).all()
    return render_template('doctor/patient_profile.html', patient=patient, appointments=appointments, medical_records=medical_records, prescriptions=prescriptions)

@app.route('/doctor/schedule_appointment', methods=['GET', 'POST'])
@login_required
def schedule_appointment():
    if current_user.role != 'doctor':
        return "You are not authorized to access this page."
    form = DoctorAppointmentForm()
    form.patient.choices = [(patient.id, f"{patient.name}") for patient in User.query.filter_by(role='patient').all()]
    patient_id = request.args.get('patient_id', type=int)
    if patient_id:
        form.patient.data = patient_id  # Pre-select the patient
    if form.validate_on_submit():
        appointment_date = form.date.data
        appointment_time = time(hour=int(form.hours.data), minute=int(form.minutes.data))
        appointment = Appointment(
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            patient_id=form.patient.data,
            doctor_id=current_user.id
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment scheduled successfully!', 'success')
        return redirect(url_for('doctor_dashboard'))
    elif request.method == 'POST':
        print(form.errors)
    return render_template('doctor/schedule_appointment.html', form=form)

# Admin Routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    print(f"Current user role in admin dashboard: {current_user.role}")  # Check current user's role
    if current_user.role != 'admin':
        return "You are not authorized to access this page."

    total_patients = User.query.filter_by(role='patient').count()
    total_doctors = User.query.filter_by(role='doctor').count()
    total_staff = User.query.filter(User.role.in_(['staff', 'nurse'])).count()  # Assuming 'staff' and 'nurse' are staff roles

    # For available resources, you might need a separate table/model
    # Assuming you have a Resource model
    # total_resources = Resource.query.count()  # Example, adjust as needed
    available_resources = "To be implemented"

    return render_template('admin/dashboard.html', total_patients=total_patients,
                           total_doctors=total_doctors, total_staff=total_staff,
                           available_resources=available_resources)

@app.route('/admin/add_doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():
    print(f"Current user role in add_doctor: {current_user.role}")
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    form = AddDoctorForm()
    if request.method == 'POST':  # Check if the request method is POST
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            name = form.name.data
            specialization = form.specialization.data

            if User.query.filter_by(email=email).first():
                flash('Email already exists')
                return render_template('admin/doctors.html', form=form, doctors=User.query.filter_by(role='doctor').all())

            new_doctor = User()
            new_doctor.email = email
            new_doctor.set_password(password)
            new_doctor.role = 'doctor'  # Set role to 'doctor'
            new_doctor.name = name
            new_doctor.specialization = specialization
            db.session.add(new_doctor)
            db.session.commit()
            flash('Doctor added successfully!')
            return redirect(url_for('add_doctor'))
        else:
            # Pass the form and doctors to the template when validation fails
            return render_template('admin/doctors.html', form=form, doctors=User.query.filter_by(role='doctor').all())

    doctors = User.query.filter_by(role='doctor').all()
    return render_template('admin/doctors.html', form=form, doctors=doctors)

@app.route('/admin/add_staff', methods=['GET', 'POST'])
@login_required
def add_staff():
    print(f"Current user role in add_staff: {current_user.role}")
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    form = AddStaffForm()
    staff_members = User.query.filter(User.role != 'patient', User.role != 'doctor', User.role != 'admin').all()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            position = form.position.data
            name = form.name.data

            if User.query.filter_by(email=email).first():
                flash('Email already exists')
                return render_template('admin/staff.html', form=form, staff_members=staff_members)

            new_staff = User()
            new_staff.email = email
            # Generate a default password hash
            new_staff.set_password("defaultpassword")  # Or generate a random one
            new_staff.role = 'staff' # Set role to staff
            new_staff.position = position
            new_staff.name = name
            db.session.add(new_staff)
            db.session.commit()
            print('Staff added successfully!')
            flash('Staff added successfully!')
            return redirect(url_for('add_staff')) # Redirect to add_staff route
        else:
            return render_template('admin/staff.html', form=form, staff_members=staff_members)

    return render_template('admin/staff.html', form=form, staff_members=staff_members)

@app.route('/admin/manage_resources', methods=['GET', 'POST'])
@login_required
def manage_resources():
    print(f"Current user role in manage_resources: {current_user.role}")
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    form = ResourceForm()
    if form.validate_on_submit():
        name = form.name.data
        quantity = form.quantity.data

        # Logic to add resource to the database
        # Example:
        # new_resource = Resource(name=name, quantity=quantity)
        # db.session.add(new_resource)
        # db.session.commit()

        flash('Resource added successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/manage_resources.html', form=form)

@app.route('/admin/manage_pricing', methods=['GET', 'POST'])
@login_required
def manage_pricing():
    print(f"Current user role in manage_pricing: {current_user.role}")
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    form = PricingForm()
    if form.validate_on_submit():
        service = form.service.data
        price = form.price.data

        # Logic to update pricing in the database
        # Example:
        # pricing = Pricing.query.filter_by(service=service).first()
        # if pricing:
        #     pricing.price = price
        #     db.session.commit()
        # else:
        #     new_pricing = Pricing(service=service, price=price)
        #     db.session.add(new_pricing)
        #     db.session.commit()

        flash('Pricing updated successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/manage_pricing.html', form=form)

@app.route('/admin/manage_inventory', methods=['GET', 'POST'])
@login_required
def manage_inventory():
    print(f"Current user role in manage_inventory: {current_user.role}")
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    form = InventoryForm()
    if form.validate_on_submit():
        item = form.item.data
        quantity = form.quantity.data

        # Logic to update inventory in the database
        # Example:
        # inventory = Inventory.query.filter_by(item=item).first()
        # if inventory:
        #     inventory.quantity = quantity
        #     db.session.commit()
        # else:
        #     new_inventory = Inventory(item=item, quantity=quantity)
        #     db.session.add(new_inventory)
        #     db.session.commit()

        flash('Inventory updated successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/manage_inventory.html', form=form)

@app.route('/admin/edit_doctor/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_doctor(id):
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    doctor = User.query.get_or_404(id)
    form = AddDoctorForm(obj=doctor)
    if form.validate_on_submit():
        doctor.name = form.name.data
        doctor.email = form.email.data
        doctor.specialization = form.specialization.data
        if form.password.data:
            doctor.set_password(form.password.data)
        db.session.commit()
        flash('Doctor updated successfully!')
        return redirect(url_for('add_doctor'))  # Redirect to add_doctor

    return render_template('admin/edit_doctor.html', form=form, doctor=doctor)

@app.route('/admin/delete_doctor/<int:id>', methods=['POST'])
@login_required
def admin_delete_doctor(id):
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    doctor = User.query.get_or_404(id)
    db.session.delete(doctor)
    db.session.commit()
    flash('Doctor deleted successfully!')
    return redirect(url_for('add_doctor'))  # Redirect to add_doctor

@app.route('/admin/edit_staff/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_staff(id):
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    staff = User.query.get_or_404(id)
    form = AddStaffForm(obj=staff)  # Use AddStaffForm to edit
    if form.validate_on_submit():
        staff.name = form.name.data
        staff.email = form.email.data
        staff.position = form.position.data
        db.session.commit()
        flash('Staff updated successfully!')
        return redirect(url_for('add_staff'))  # Redirect to add_staff
    return render_template('admin/edit_staff.html', form=form, staff=staff)

@app.route('/admin/delete_staff/<int:id>', methods=['POST'])
@login_required
def admin_delete_staff(id):
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    staff = User.query.get_or_404(id)
    db.session.delete(staff)
    db.session.commit()
    flash('Staff deleted successfully!')
    return redirect(url_for('add_staff'))  # Redirect to add_staff

@app.route('/search_doctors', methods=['GET', 'POST'])
@login_required
def search_doctors():
    if current_user.role != 'patient':
        return "You are not authorized to access this page."
    form = DoctorSearchForm()
    doctors = User.query.filter_by(role='doctor').all()  # Query all doctors by default
    if form.validate_on_submit():
        search_term = form.search_term.data
        search_by = form.search_by.data
        if search_by == 'name':
            doctors = User.query.filter(User.name.ilike(f'%{search_term}%'), User.role == 'doctor').all()
        elif search_by == 'specialization':
            doctors = User.query.filter(User.specialization.ilike(f'%{search_term}%'), User.role == 'doctor').all()
    return render_template('patient/search_doctors.html', form=form, doctors=doctors)

def create_test_users():
    # Create test patient
    if not User.query.filter_by(email='danijela@gmail.com').first():
        patient = User(
            email='danijela@gmail.com',
            name='Danijela',
            role='patient'
        )
        patient.set_password('X#Kfv8$}Vj$#]]:')
        db.session.add(patient)

    # Create test doctor
    if not User.query.filter_by(email='milica@gmail.com').first():
        doctor = User(
            email='milica@gmail.com',
            name='Milica',
            role='doctor',
            specialization='General Practitioner'
        )
        doctor.set_password("be35v+'h=KjnSn")
        db.session.add(doctor)

    # Create admin user
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(
            email='admin@example.com',
            name='Admin',
            role='admin'
        )
        admin.set_password('passwordpassword')
        db.session.add(admin)

    # Create additional test patients
    if not User.query.filter_by(email='jovan@gmail.com').first():
        patient = User(
            email='jovan@gmail.com',
            name='Jovan',
            role='patient'
        )
        patient.set_password('password123')
        db.session.add(patient)

    if not User.query.filter_by(email='ana@gmail.com').first():
        patient = User(
            email='ana@gmail.com',
            name='Ana',
            role='patient'
        )
        patient.set_password('password123')
        db.session.add(patient)

    if not User.query.filter_by(email='marko@gmail.com').first():
        patient = User(
            email='marko@gmail.com',
            name='Marko',
            role='patient'
        )
        patient.set_password('password123')
        db.session.add(patient)

    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_test_users()
        app.run(debug=True)