# Hospital Management System

This is a school project for a Hospital Management System built with [Flask](https://flask.palletsprojects.com/) and plain HTML. The application allows administrators, doctors, and patients to manage hospital operations efficiently.

## Features

- User authentication and role-based access (admin, doctor, patient)
- Admin dashboard for managing doctors, staff, inventory, and pricing
- Doctor dashboard for managing appointments, patient records, and prescriptions
- Patient portal for booking appointments, viewing medical records, and prescriptions
- Inventory and pricing management
- Responsive UI with Bootstrap

## Getting Started

1. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```
   python app.py
   ```

3. **Access the app:**
   Open [http://localhost:5000](http://localhost:5000) in your browser.

## Default Admin Login

- Email: `admin@example.com`
- Password: `passwordpassword`

## Project Structure

- `app.py` – Main application entry point
- `models.py` – Database models
- `forms.py` – WTForms definitions
- `controllers/` – Blueprints for admin, doctor, patient and auth routes
- `templates/` – HTML templates
