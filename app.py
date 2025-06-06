from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from datetime import datetime
import os
from models import User, db

from controllers.admin import bp as admin_bp
from controllers.patient import bp as patient_bp
from controllers.doctor import bp as doctor_bp
from controllers.auth import bp as auth_bp

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

app.register_blueprint(admin_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(auth_bp)

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor.doctor_dashboard'))
        elif current_user.role == 'patient':
            return redirect(url_for('patient.profile'))
    return redirect(url_for('auth.login'))

def create_admin_account():
    try:
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                email='admin@example.com',
                name='Admin',
                role='admin'
            )
            admin.set_password('passwordpassword')
            db.session.add(admin)

        db.session.commit()
    except Exception as e:
        print(f"Error creating test users: {e}")

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            create_admin_account()
            app.run(debug=True)
        except Exception as e:
            print(f"Error during app initialization: {e}")