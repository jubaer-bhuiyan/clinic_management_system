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

## 📞 Support & Contact

### Project Maintainer
- **Name:** Jubaer Ahamed Bhuiyan
- **Email:** jubaerahamed4444@gmail.com
- **Location:** IUBAT - International University of Business Agriculture and Technology
  4 Embankment Drive Road, Sector-10, Uttara Model Town, Dhaka-1230, Bangladesh

### Social Links
- **LinkedIn:** [Jubaer Ahamed Bhuiyan](https://www.linkedin.com/in/jubaer-ahamed-bhuiyan)
- **Research:** [ResearchGate](https://www.researchgate.net/profile/Jubaer-Bhuiyan)
- **ORCID:** [0009-0009-7673-1102](https://orcid.org/0009-0009-7673-1102)
- **Twitter:** [@JubaerAhamed3](https://twitter.com/JubaerAhamed3)

### Additional Profiles
- **Facebook:** [bhuiyan.jubaer](https://facebook.com/bhuiyan.jubaer)
- **Instagram:** [jubaer.bhuiyan](https://instagram.com/jubaer.bhuiyan)

For technical support and inquiries, please feel free to reach out through any of the above channels.
Timezone: UTC +06:00 (Bangladesh Standard Time) 