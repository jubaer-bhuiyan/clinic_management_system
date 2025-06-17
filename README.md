# Clinical Appointment Management System (CAMS)

A comprehensive web-based system for managing clinical appointments, patient records, and medical staff.

## Author
**Developed by:** Jubaer Ahamed Bhuiyan  
**Copyright:** © 2025 All rights reserved.

## About
The Clinical Appointment Management System (CAMS) is a sophisticated healthcare management solution designed to streamline the process of managing medical appointments, patient records, and clinical staff. This system provides an efficient way to handle day-to-day operations in a clinical setting.

## Features
- **User Management**
  - Multi-user role system (Admin, Doctors, Staff, Patients)
  - Secure authentication and authorization
  - Role-based access control
  - Profile management for all users

- **Appointment System**
  - Easy appointment scheduling
  - Real-time availability checking
  - Appointment status tracking
  - Email notifications
  - Appointment history

- **Patient Management**
  - Complete patient records
  - Medical history tracking
  - Appointment history
  - Document uploads
  - Profile management

- **Doctor Management**
  - Doctor profiles and specializations
  - Schedule management
  - Patient assignment
  - Appointment tracking
  - Record management

- **Staff Management**
  - Staff profiles and roles
  - Task assignment
  - Schedule management
  - Access control

- **Admin Features**
  - System configuration
  - User management
  - Access control
  - Analytics and reports
  - Backup and restore

## Technical Stack
- **Backend Framework:** Django 4.2.23
- **Frontend Technologies:**
  - HTML5
  - CSS3
  - JavaScript
  - Bootstrap 4.5.2
  - jQuery 3.5.1
- **Database:** SQLite3
- **Additional Libraries:**
  - python-dateutil 2.8.2
  - Pillow 10.2.0
  - Font Awesome 5.15.4

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/CAMS.git
   cd CAMS
   ```

2. Create and activate virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the database:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application:
   - Main site: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

## Usage Guide

### Admin Portal
- Access via /admin with superuser credentials
- Manage users, roles, and permissions
- Configure system settings
- Generate reports
- Monitor system activity

### Doctor Interface
- View and manage appointments
- Access patient records
- Update medical histories
- Manage schedule
- Generate prescriptions

### Staff Interface
- Schedule appointments
- Manage patient records
- Handle registration
- Update patient information
- Generate reports

### Patient Portal
- Book appointments
- View medical history
- Update personal information
- Track appointment status
- Download reports

## Security Features
- Secure authentication system
- Role-based access control
- Password encryption
- Session management
- CSRF protection
- XSS prevention
- SQL injection protection

## Best Practices
- Follow PEP 8 coding standards
- Regular database backups
- Secure password storage
- Input validation
- Error logging
- Clean code architecture

## License
This project is proprietary software.  
Copyright © 2025 Jubaer Ahamed Bhuiyan. All rights reserved.

No part of this software may be reproduced, distributed, or transmitted in any form or by any means without the prior written permission of the author.

## Contact
For any inquiries about this project, please contact:
- **Name:** Jubaer Ahamed Bhuiyan
- **Role:** Developer & Project Owner
- **Copyright:** © 2025 All rights reserved