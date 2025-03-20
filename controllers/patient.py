from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Appointment, MedicalRecord, Prescription, User, db
from forms import AppointmentForm, DoctorSearchForm
from datetime import time, datetime, timedelta

bp = Blueprint('patient', __name__)

@bp.route('/profile')
@login_required
def profile():
    now = datetime.now()
    appointments = Appointment.query.filter_by(patient_id=current_user.id).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    medical_records = MedicalRecord.query.filter_by(patient_id=current_user.id).all()
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id).all()
    return render_template('patient/profile.html', appointments=appointments, medical_records=medical_records, prescriptions=prescriptions, now=now)

@bp.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if current_user.role != 'patient':
        return "You are not authorized to access this page."
    
    tomorrow = datetime.now().date() + timedelta(days=1)
    form = AppointmentForm()
    form.doctor.choices = [(doctor.id, f"{doctor.name} ({doctor.specialization})") 
                          for doctor in User.query.filter_by(role='doctor').all()]
    
    # Get date and doctor from form data or request
    selected_date = request.form.get('date') or form.date.data
    selected_doctor = request.form.get('doctor') or form.doctor.data
    
    if selected_date and selected_doctor:
        try:
            # Convert string date to date object if needed
            if isinstance(selected_date, str):
                selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            selected_doctor = int(selected_doctor)
            
            # Set the form data
            form.date.data = selected_date
            form.doctor.data = selected_doctor
            
            booked_times = Appointment.get_scheduled_times(selected_date, selected_doctor)
            available_times = [
                time(hour, minute) 
                for hour in range(8, 16) 
                for minute in range(0, 60, 10) 
                if time(hour, minute) not in booked_times
            ]
            form.time.choices = [(t.strftime('%H:%M'), t.strftime('%H:%M')) for t in sorted(available_times)]
        except (ValueError, TypeError):
            form.time.choices = []
    
    # Only process final submission if time is selected
    if form.validate_on_submit() and form.time.data and 'submit' in request.form:
        appointment_time = datetime.strptime(form.time.data, '%H:%M').time()
        appointment = Appointment(
            appointment_date=selected_date,
            appointment_time=appointment_time,
            patient_id=current_user.id,
            doctor_id=selected_doctor
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Your appointment has been booked!', 'success')
        return redirect(url_for('patient.profile'))
    
    return render_template('patient/appointments.html', form=form, now=datetime.now(), timedelta=timedelta)

@bp.route('/book_appointment/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def book_doctor_appointment(doctor_id):
    if current_user.role != 'patient':
        return "You are not authorized to access this page."
    
    form = AppointmentForm()
    doctor = db.session.get(User, doctor_id)
    form.doctor.choices = [(doctor_id, f"{doctor.name} ({doctor.specialization})")]
    form.doctor.data = doctor_id  # Pre-select the doctor
    
    # Get date from form data or request
    selected_date = request.form.get('date') or form.date.data
    
    if selected_date:
        try:
            # Convert string date to date object if needed
            if isinstance(selected_date, str):
                selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            
            form.date.data = selected_date
            booked_times = Appointment.get_scheduled_times(selected_date, doctor_id)
            available_times = [
                time(hour, minute) 
                for hour in range(8, 16) 
                for minute in range(0, 60, 10) 
                if time(hour, minute) not in booked_times
            ]
            form.time.choices = [(t.strftime('%H:%M'), t.strftime('%H:%M')) for t in sorted(available_times)]
        except (ValueError, TypeError):
            form.time.choices = []
    
    if form.validate_on_submit() and 'submit' in request.form and form.time.data:
        appointment_time = datetime.strptime(form.time.data, '%H:%M').time()
        appointment = Appointment(
            appointment_date=selected_date,
            appointment_time=appointment_time,
            patient_id=current_user.id,
            doctor_id=doctor_id
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Your appointment has been booked!', 'success')
        return redirect(url_for('patient.profile'))
    
    return render_template('patient/appointments.html', form=form, now=datetime.now(), timedelta=timedelta)

@bp.route('/search_doctors', methods=['GET', 'POST'])
@login_required
def search_doctors():
    if current_user.role != 'patient':
        return "You are not authorized to access this page."
    form = DoctorSearchForm()
    doctors = User.query.filter_by(role='doctor').all()
    if form.validate_on_submit():
        search_term = form.search_term.data
        search_by = form.search_by.data
        if search_by == 'name':
            doctors = User.query.filter(User.name.ilike(f'%{search_term}%'), User.role == 'doctor').all()
        elif search_by == 'specialization':
            doctors = User.query.filter(User.specialization.ilike(f'%{search_term}%'), User.role == 'doctor').all()
    return render_template('patient/search_doctors.html', form=form, doctors=doctors)
