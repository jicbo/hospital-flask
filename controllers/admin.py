from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import User, db, Pricing, Inventory
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

@bp.route('/admin/manage_pricing', methods=['GET', 'POST'])
@login_required
def manage_pricing():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    form = PricingForm()
    if form.validate_on_submit():
        pricing = Pricing(
            service=form.service.data,
            price=form.price.data
        )
        db.session.add(pricing)
        db.session.commit()
        return redirect(url_for('admin.manage_pricing'))
    
    pricing_list = Pricing.query.all()
    return render_template('admin/manage_pricing.html', form=form, pricing_list=pricing_list)

@bp.route('/admin/edit_pricing/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_pricing(id):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    pricing = Pricing.query.get_or_404(id)
    form = PricingForm(obj=pricing)
    if form.validate_on_submit():
        pricing.service = form.service.data
        pricing.price = form.price.data
        db.session.commit()
        return redirect(url_for('admin.manage_pricing'))
    
    return render_template('admin/edit_pricing.html', form=form, pricing=pricing)

@bp.route('/admin/delete_pricing/<int:id>', methods=['POST'])
@login_required
def delete_pricing(id):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    pricing = Pricing.query.get_or_404(id)
    db.session.delete(pricing)
    db.session.commit()
    return redirect(url_for('admin.manage_pricing'))

@bp.route('/admin/manage_inventory', methods=['GET', 'POST'])
@login_required
def manage_inventory():
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    form = InventoryForm()
    if form.validate_on_submit():
        item_name = form.item_name.data
        quantity = form.quantity.data
        inventory_item = Inventory.query.filter_by(item_name=item_name).first()
        if inventory_item:
            inventory_item.quantity = quantity
        else:
            inventory_item = Inventory(item_name=item_name, quantity=quantity)
            db.session.add(inventory_item)
        db.session.commit()
        flash('Inventory updated successfully!')
        return redirect(url_for('admin.manage_inventory'))
    inventory = Inventory.query.all()
    return render_template('admin/manage_inventory.html', form=form, inventory=inventory)

@bp.route('/admin/edit_inventory/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_inventory(id):
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    inventory_item = Inventory.query.get_or_404(id)
    form = InventoryForm(obj=inventory_item)
    if form.validate_on_submit():
        inventory_item.item_name = form.item_name.data
        inventory_item.quantity = form.quantity.data
        db.session.commit()
        flash('Inventory item updated successfully!')
        return redirect(url_for('admin.manage_inventory'))
    return render_template('admin/edit_inventory.html', form=form, inventory_item=inventory_item)

@bp.route('/admin/delete_inventory/<int:id>', methods=['POST'])
@login_required
def delete_inventory(id):
    if current_user.role != 'admin':
        return "You are not authorized to access this page."
    inventory_item = Inventory.query.get_or_404(id)
    db.session.delete(inventory_item)
    db.session.commit()
    flash('Inventory item deleted successfully!')
    return redirect(url_for('admin.manage_inventory'))

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