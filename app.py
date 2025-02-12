from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from models import User, Appointment, MedicalRecord, db  # Import the models and db
from forms import LoginForm, RegistrationForm, AddDoctorForm, AddStaffForm, ResourceForm, PricingForm, InventoryForm, AppointmentForm
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
        name = form.name.data

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
    return render_template('patient/profile.html') # Example

@app.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    print(f"Current user role: {current_user.role}")  # Check current user's role
    if current_user.role != 'patient':
        return "You are not authorized to access this page."

    form = AppointmentForm()
    doctors = User.query.filter_by(role='doctor').all()
    form.doctor.choices = [(doctor.id, doctor.name) for doctor in doctors]

    if form.validate_on_submit():
        appointment_time = form.date.data
        doctor_id = form.doctor.data
        notes = form.notes.data

        new_appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=doctor_id,
            appointment_time=appointment_time,
            notes=notes  # Save notes to the appointment
        )
        db.session.add(new_appointment)
        db.session.commit()
        flash('Appointment booked successfully!')
        return redirect(url_for('profile'))

    return render_template('patient/appointments.html', form=form, doctors=doctors)

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist

        # Create default admin user
        admin_email = "admin@example.com"
        if not User.query.filter_by(email=admin_email).first():
            admin_password = "password"  # Replace with a strong password
            hashed_password = generate_password_hash(admin_password)
            admin = User(email=admin_email, password_hash=hashed_password, role='admin', name='Admin')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created.")

        app.run(debug=True)