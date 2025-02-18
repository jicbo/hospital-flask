from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateTimeField, TextAreaField, SelectField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional, Length, NumberRange
from models import User

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class DoctorRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    specialization = StringField('Specialization', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, email):
        doctor = Doctor.query.filter_by(email=email.data).first()
        if doctor is not None:
            raise ValidationError('Please use a different email address.')

class AppointmentForm(FlaskForm):
    date = DateField('Appointment Date', format='%Y-%m-%d', validators=[DataRequired()])
    hours = IntegerField('Hours', validators=[DataRequired(), NumberRange(min=8, max=20)])
    minutes = IntegerField('Minutes', validators=[DataRequired(), NumberRange(min=0, max=59)])
    notes = TextAreaField('Notes')
    doctor = SelectField('Doctor', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Book Appointment')

class MedicalRecordForm(FlaskForm):
    report = TextAreaField('Medical Report', validators=[DataRequired()])
    submit = SubmitField('Add Medical Record')

class MedicalReportForm(FlaskForm):
    report = TextAreaField('Report', validators=[DataRequired()])
    submit = SubmitField('Add Medical Report')

class PrescriptionForm(FlaskForm):
    patient = SelectField('Patient', coerce=int, validators=[DataRequired()])
    medication = StringField('Medication', validators=[DataRequired()])
    dosage = StringField('Dosage', validators=[DataRequired()])
    instructions = TextAreaField('Instructions', validators=[DataRequired()])
    submit = SubmitField('Issue Prescription')

class DoctorSearchForm(FlaskForm):
    search_term = StringField('Search', validators=[Optional()])
    search_by = SelectField('Search By', choices=[('name', 'Name'), ('specialization', 'Specialization')], validators=[DataRequired()])
    submit = SubmitField('Search')

class AddDoctorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    specialization = StringField('Specialization', validators=[DataRequired()])
    submit = SubmitField('Add Doctor')

class AddStaffForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    position = StringField('Position', validators=[DataRequired()])
    submit = SubmitField('Add Staff')

class ResourceForm(FlaskForm):
    name = StringField('Resource Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Resource')

class PricingForm(FlaskForm):
    service = StringField('Service Name', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Price')

class InventoryForm(FlaskForm):
    item = StringField('Item Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Inventory')

class DoctorAppointmentForm(FlaskForm):
    date = DateField('Appointment Date', format='%Y-%m-%d', validators=[DataRequired()])
    hours = IntegerField('Hours', validators=[DataRequired(), NumberRange(min=8, max=20)])
    minutes = IntegerField('Minutes', validators=[DataRequired(), NumberRange(min=0, max=59)])
    patient = SelectField('Patient', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Schedule Appointment')