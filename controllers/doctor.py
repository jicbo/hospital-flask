from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Appointment, MedicalRecord, Prescription, User, db
from forms import MedicalRecordForm, DoctorSearchForm, PrescriptionForm, EditPrescriptionForm
from datetime import time, datetime

bp = Blueprint('doctor', __name__)

@bp.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        return "You are not authorized to access this page."
    now = datetime.now()
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    upcoming_appointments = [appointment for appointment in appointments if datetime.combine(appointment.appointment_date, appointment.appointment_time) >= now]
    past_appointments = [appointment for appointment in appointments if datetime.combine(appointment.appointment_date, appointment.appointment_time) < now]
    return render_template('doctor/dashboard.html', upcoming_appointments=upcoming_appointments, past_appointments=past_appointments)

@bp.route('/doctor/add_report/<int:appointment_id>', methods=['GET', 'POST'])
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
            appointment.medical_record_id = medical_record.id
            db.session.commit()
            flash('Medical report added successfully!')
            return redirect(url_for('doctor.doctor_dashboard'))
        else:
            flash('Please enter a medical report.')
    return render_template('doctor/medical_report.html', appointment=appointment)

@bp.route('/doctor/add_medical_record/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def add_medical_record(patient_id):
    if current_user.role != 'doctor':
        return "You are not authorized to access this page."
    form = MedicalRecordForm()
    if form.validate_on_submit():
        medical_record = MedicalRecord(
            patient_id=patient_id,
            report=form.report.data
        )
        db.session.add(medical_record)
        db.session.commit()
        flash('Medical record added successfully!')
        return redirect(url_for('doctor.patient_profile', patient_id=patient_id))
    return render_template('doctor/add_medical_record.html', form=form, patient_id=patient_id)

@bp.route('/doctor/search_patients', methods=['GET', 'POST'])
@login_required
def search_patients():
    if current_user.role != 'doctor':
        return "You are not authorized to access this page."
    form = DoctorSearchForm()
    patients = User.query.filter_by(role='patient').all()
    if form.validate_on_submit():
        search_term = form.search_term.data
        search_by = form.search_by.data
        if search_by == 'name':
            patients = User.query.filter(User.name.ilike(f'%{search_term}%'), User.role == 'patient').all()
        elif search_by == 'id':
            try:
                patient_id = int(search_term)
                patients = User.query.filter(User.id == patient_id, User.role == 'patient').all()
            except ValueError:
                flash('Please enter a valid ID number', 'error')
                patients = []
    return render_template('doctor/search_patients.html', form=form, patients=patients)

@bp.route('/doctor/issue_prescription', methods=['GET', 'POST'])
@login_required
def issue_prescription():
    if current_user.role != 'doctor':
        return "You are not authorized to access this page."
    form = PrescriptionForm()
    form.patient.choices = [(patient.id, patient.name) for patient in User.query.filter_by(role='patient').all()]
    patient_id = request.args.get('patient_id', type=int)
    if patient_id:
        form.patient.data = patient_id
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
        return redirect(url_for('doctor.patient_profile', patient_id=form.patient.data))
    return render_template('doctor/issue_prescription.html', form=form)

@bp.route('/doctor/patient_profile/<int:patient_id>', methods=['GET'])
def patient_profile(patient_id):
    patient = User.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()
    medical_records = MedicalRecord.query.filter_by(patient_id=patient_id).all()
    prescriptions = Prescription.query.filter_by(patient_id=patient_id).all()
    return render_template('doctor/patient_profile.html', patient=patient, appointments=appointments, medical_records=medical_records, prescriptions=prescriptions)

@bp.route('/doctor/edit_medical_record/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_medical_record(record_id):
    if current_user.role != 'doctor':
        return "You are not authorized to access this page."
    medical_record = MedicalRecord.query.get_or_404(record_id)
    form = MedicalRecordForm(obj=medical_record)
    if form.validate_on_submit():
        medical_record.report = form.report.data
        db.session.commit()
        flash('Medical record updated successfully!')
        return redirect(url_for('doctor.patient_profile', patient_id=medical_record.patient_id))
    return render_template('doctor/edit_medical_record.html', form=form, medical_record=medical_record)

@bp.route('/doctor/delete_medical_record/<int:record_id>', methods=['POST'])
@login_required
def delete_medical_record(record_id):
    if current_user.role != 'doctor':
        return "You are not authorized to access this page."
    medical_record = MedicalRecord.query.get_or_404(record_id)
    patient_id = medical_record.patient_id
    db.session.delete(medical_record)
    db.session.commit()
    flash('Medical record deleted successfully!')
    return redirect(url_for('doctor.patient_profile', patient_id=patient_id))

@bp.route('/doctor/edit_prescription/<int:prescription_id>', methods=['GET', 'POST'])
@login_required
def edit_prescription(prescription_id):
    if current_user.role != 'doctor':
        return "You are not authorized to access this page."
    prescription = Prescription.query.get_or_404(prescription_id)
    form = EditPrescriptionForm(obj=prescription)
    if form.validate_on_submit():
        prescription.medication = form.medication.data
        prescription.dosage = form.dosage.data
        prescription.instructions = form.instructions.data
        db.session.commit()
        flash('Prescription updated successfully!')
        return redirect(url_for('doctor.patient_profile', patient_id=prescription.patient_id))
    else:
        if request.method == 'POST':
            print(form.errors)
    return render_template('doctor/edit_prescription.html', form=form, prescription=prescription)

@bp.route('/doctor/delete_prescription/<int:prescription_id>', methods=['POST'])
@login_required
def delete_prescription(prescription_id):
    if current_user.role != 'doctor':
        return "You are not authorized to access this page."
    prescription = Prescription.query.get_or_404(prescription_id)
    patient_id = prescription.patient_id
    db.session.delete(prescription)
    db.session.commit()
    flash('Prescription deleted successfully!')
    return redirect(url_for('doctor.patient_profile', patient_id=patient_id))
