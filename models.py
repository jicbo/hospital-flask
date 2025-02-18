from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='patient', nullable=False)  # role: admin, doctor, patient
    appointments = db.relationship('Appointment', backref='doctor', lazy=True, foreign_keys='Appointment.doctor_id')  # Specify foreign key
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy=True)
    name = db.Column(db.String(64), index=True)
    specialization = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True)  # Staff

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name}>'

class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_record.id'))
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_appointments')
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Appointment {self.id}>'

class MedicalRecord(db.Model):
    __tablename__ = 'medical_record'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<MedicalRecord {self.id}>'

class MedicalReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    report = db.Column(db.Text)

class Prescription(db.Model):
    __tablename__ = 'prescription'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    medication = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Prescription {self.id}>'