from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db
from forms import LoginForm, RegistrationForm

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor.doctor_dashboard'))
        return redirect(url_for('patient.profile'))

    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        name = f"{first_name} {last_name}"

        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('auth.register'))

        new_user = User()
        new_user.email = email
        new_user.set_password(password)
        new_user.role = 'patient'
        new_user.name = name
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('patient.profile'))
    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor.doctor_dashboard'))
        return redirect(url_for('patient.profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if user.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif user.role == 'doctor':
                return redirect(url_for('doctor.doctor_dashboard'))
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid email or password')
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
