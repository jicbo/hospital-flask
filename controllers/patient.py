from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Appointment, MedicalRecord, Prescription, User, db
from forms import AppointmentForm, DoctorSearchForm  # Add DoctorSearchForm import
from datetime import time, datetime

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
    form = AppointmentForm()
    form.doctor.choices = [(doctor.id, f"{doctor.name} ({doctor.specialization})") for doctor in User.query.filter_by(role='doctor').all()]
    if form.validate_on_submit():
        appointment_time = time(hour=form.hours.data, minute=form.minutes.data)
        existing_appointment = Appointment.query.filter_by(doctor_id=form.doctor.data, appointment_date=form.date.data, appointment_time=appointment_time).first()
        if existing_appointment:
            flash('This time slot is already taken. Please choose a different time.', 'danger')
        else:
            appointment = Appointment(
                appointment_date=form.date.data,
                appointment_time=appointment_time,
                patient_id=current_user.id,
                doctor_id=form.doctor.data,
                notes=form.notes.data
            )
            db.session.add(appointment)
            db.session.commit()
            flash('Your appointment has been booked!', 'success')
            return redirect(url_for('patient.profile'))
    return render_template('patient/appointments.html', form=form)

@bp.route('/book_appointment/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def book_doctor_appointment(doctor_id):
    if current_user.role != 'patient':
        return "You are not authorized to access this page."
    form = AppointmentForm()
    form.doctor.choices = [(doctor_id, f"{db.session.get(User, doctor_id).name} ({db.session.get(User, doctor_id).specialization})")]
    if form.validate_on_submit():
        appointment_time = time(hour=form.hours.data, minute=form.minutes.data)
        appointment = Appointment(
            appointment_date=form.date.data,
            appointment_time=appointment_time,
            patient_id=current_user.id,
            doctor_id=doctor_id
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Your appointment has been booked!', 'success')
        return redirect(url_for('patient.profile'))
    elif request.method == 'POST':
        print(form.errors)
    return render_template('patient/appointments.html', form=form)

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
