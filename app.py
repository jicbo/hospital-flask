from flask import Flask, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from datetime import datetime
import os
import logging
from models import User, db  # Import the models and db
from sqlalchemy import exc

from controllers.admin import bp as admin_bp
from controllers.patient import bp as patient_bp
from controllers.doctor import bp as doctor_bp
from controllers.auth import bp as auth_bp

# Initialize Flask app and config first
app = Flask(__name__)
app.config.from_object('config.Config')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
db.init_app(app)

# Initialize login manager after database
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(auth_bp)

def check_and_create_tables():
    try:
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        required_tables = ['users', 'appointments', 'medical_records', 'prescriptions', 'inventory']
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            logger.info(f"Missing tables: {missing_tables}")
            logger.info("Creating missing tables...")
            db.create_all()
            return True
        else:
            logger.info("All required tables exist")
            return False
    except Exception as e:
        logger.error(f"Error checking tables: {e}")
        return False

# Initialize the application
with app.app_context():
    try:
        tables_created = check_and_create_tables()
        if tables_created:
            admin = User.query.filter_by(email='admin@example.com').first()
            if not admin:
                create_test_users()
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        if app.debug:
            raise

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'patient':
            return redirect(url_for('patient.profile'))
    return render_template('index.html')

# Error handlers
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f'Server Error: {error}')
    return jsonify(error=str(error)), 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f'Unhandled Exception: {str(e)}')
    if isinstance(e, exc.SQLAlchemyError):
        db.session.rollback()
    return jsonify(error=str(e)), 500

def create_test_users():
    try:
        # Create admin user
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                email='admin@example.com',
                name='Admin',
                role='admin'
            )
            admin.set_password('passwordpassword')
            db.session.add(admin)

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

        # Create test patient
        if not User.query.filter_by(email='danijela@gmail.com').first():
            patient = User(
                email='danijela@gmail.com',
                name='Danijela',
                role='patient'
            )
            patient.set_password('X#Kfv8$}Vj$#]]:')
            db.session.add(patient)

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
        logger.info("Test users created successfully.")
    except Exception as e:
        logger.error(f"Error creating test users: {e}")

if __name__ == '__main__':
    app.run(debug=True)