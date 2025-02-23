from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime
import os
from models import User, db  # Import the models and db

from views.admin import bp as admin_bp
from views.patient import bp as patient_bp
from views.doctor import bp as doctor_bp
from views.auth import bp as auth_bp

app = Flask(__name__)
app.config.from_object('config.Config')  # Load configuration from config.py

# Initialize the database with the app
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Register blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(auth_bp)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

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