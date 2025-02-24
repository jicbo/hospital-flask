from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import User, db
from forms import AddDoctorForm, AddStaffForm, ResourceForm, PricingForm, InventoryForm

bp = Blueprint('admin', __name__)

@bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return "You are not authorized to access this page."

    total_patients = User.query.filter_by(role='patient').count()
    total_doctors = User.query.filter_by(role='doctor').count()
    total_staff = User.query.filter(User.role.in_(['staff', 'nurse'])).count()
    available_resources = "To be implemented"

    return render_template('admin/dashboard.html', total_patients=total_patients,
                           total_doctors=total_doctors, total_staff=total_staff,
                           available_resources=available_resources)

@bp.route('/admin/add_doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    form = AddDoctorForm()
    if request.method == 'POST':
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
            new_doctor.role = 'doctor'
            new_doctor.name = name
            new_doctor.specialization = specialization
            db.session.add(new_doctor)
            db.session.commit()
            flash('Doctor added successfully!')
            return redirect(url_for('admin.add_doctor'))
        else:
            return render_template('admin/doctors.html', form=form, doctors=User.query.filter_by(role='doctor').all())

    doctors = User.query.filter_by(role='doctor').all()
    return render_template('admin/doctors.html', form=form, doctors=doctors)

@bp.route('/admin/add_staff', methods=['GET', 'POST'])
@login_required
def add_staff():
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
            new_staff.set_password("defaultpassword")
            new_staff.role = 'staff'
            new_staff.position = position
            new_staff.name = name
            db.session.add(new_staff)
            db.session.commit()
            flash('Staff added successfully!')
            return redirect(url_for('admin.add_staff'))
        else:
            return render_template('admin/staff.html', form=form, staff_members=staff_members)

    return render_template('admin/staff.html', form=form, staff_members=staff_members)

@bp.route('/admin/manage_resources', methods=['GET', 'POST'])
@login_required
def manage_resources():
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    form = ResourceForm()
    if form.validate_on_submit():
        name = form.name.data
        quantity = form.quantity.data
        # Logic to add resource to the database
        flash('Resource added successfully!')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/manage_resources.html', form=form)

@bp.route('/admin/manage_pricing', methods=['GET', 'POST'])
@login_required
def manage_pricing():
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    form = PricingForm()
    if form.validate_on_submit():
        service = form.service.data
        price = form.price.data
        # Logic to update pricing in the database
        flash('Pricing updated successfully!')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/manage_pricing.html', form=form)

@bp.route('/admin/manage_inventory', methods=['GET', 'POST'])
@login_required
def manage_inventory():
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    form = InventoryForm()
    if form.validate_on_submit():
        item = form.item.data
        quantity = form.quantity.data
        # Logic to update inventory in the database
        flash('Inventory updated successfully!')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/manage_inventory.html', form=form)

@bp.route('/admin/edit_doctor/<int:id>', methods=['GET', 'POST'])
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
        return redirect(url_for('admin.add_doctor'))
    return render_template('admin/edit_doctor.html', form=form, doctor=doctor)

@bp.route('/admin/delete_doctor/<int:id>', methods=['POST'])
@login_required
def admin_delete_doctor(id):
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    doctor = User.query.get_or_404(id)
    db.session.delete(doctor)
    db.session.commit()
    flash('Doctor deleted successfully!')
    return redirect(url_for('admin.add_doctor'))

@bp.route('/admin/edit_staff/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_staff(id):
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    staff = User.query.get_or_404(id)
    form = AddStaffForm(obj=staff)
    if form.validate_on_submit():
        staff.name = form.name.data
        staff.email = form.email.data
        staff.position = form.position.data
        db.session.commit()
        flash('Staff updated successfully!')
        return redirect(url_for('admin.add_staff'))
    return render_template('admin/edit_staff.html', form=form, staff=staff)

@bp.route('/admin/delete_staff/<int:id>', methods=['POST'])
@login_required
def admin_delete_staff(id):
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    staff = User.query.get_or_404(id)
    db.session.delete(staff)
    db.session.commit()
    flash('Staff deleted successfully!')
    return redirect(url_for('admin.add_staff'))