# Clinical Appointment Management System (CAMS) 🏥

A modern, comprehensive solution for clinical appointment and healthcare management.

## 🌟 Overview

CAMS is a sophisticated healthcare management solution designed to streamline clinical operations while ensuring data security and system reliability. It provides a complete suite of tools for managing appointments, patient records, staff, and administrative tasks.

## ✨ Key Features

### Recent Updates
- **Staff Approval System**: New system for tracking and approving staff changes
- **Enhanced Doctor Search**: Advanced filtering and modern UI for finding doctors
- **Improved User Interface**: Modern Bootstrap 5 components and responsive design

### Core Features
- Multi-role user management (Admin/Doctor/Staff/Patient)
- Smart appointment scheduling with conflict prevention
- Digital health records management
- Real-time messaging system
- Comprehensive reporting and analytics
- Role-based access control
- Change approval workflow

## 🛠️ Technical Stack

### Backend
- Django 4.2.23
- Python 3.13+
- SQLite3
- Custom middleware
- RESTful API

### Frontend
- HTML5 & CSS3
- JavaScript (ES6+)
- Bootstrap 5.3
- Font Awesome 6.0
- Responsive design

### Dependencies
- django-crispy-forms 2.1
- crispy-bootstrap5
- python-dateutil 2.8.2
- Pillow 10.2.0
- django-widget-tweaks 1.5.0
- django-cleanup 8.0.0
- django-environ 0.11.2
- django-filter 23.5
- django-debug-toolbar 4.3.0

## 🚀 Installation

1. Clone and setup:
   ```bash
   git clone https://github.com/your-username/clinic_management_system.git
   cd clinic_management_system
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Configure database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. Run server:
   ```bash
   python manage.py runserver
   ```

Access at: http://localhost:8000

## 👥 User Roles

### Admin
- System configuration
- User management
- Change approval
- Analytics & reporting

### Doctor
- Appointment management
- Patient records
- Availability updates
- Messaging

### Staff
- Patient registration
- Appointment booking
- Record management
- Change requests

### Patient
- Book appointments
- View medical history
- Message doctors
- Search doctors

## 🔒 Security

- Role-based access control
- Staff change approval system
- Form validation
- CSRF protection
- XSS prevention
- SQL injection guards
- Regular security audits

## 📝 License

Proprietary software. All rights reserved.

## 📞 Support

- Email: support@cams.com
- Hours: Monday-Friday, 9:00 AM - 5:00 PM EST 