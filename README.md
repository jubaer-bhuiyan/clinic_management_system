
# 🏥 Clinic Management System

A Django-based web application designed to simplify the management of clinic operations, including appointments, doctors, patients, and user roles.

## 📌 Overview

The **Clinic Management System** helps streamline everyday clinic functions with a clean web interface and user-role-based access. It supports patient registration, appointment booking, doctor management, and admin functionalities.

## ✨ Key Features

- 🔐 **User Authentication:** Login and secure session management for admin and staff roles.
- 👨‍⚕️ **Doctor Management:** Add, update, and manage doctors.
- 🗓️ **Appointment Scheduling:** Book, update, and cancel appointments.
- 🧑‍💼 **Admin Dashboard:** Central access to manage users, doctors, and appointments.
- 📄 **Patient Records:** Maintain patient profiles and booking history.

## ⚙️ Technologies Used

- **Framework:** Django (Python)
- **Frontend:** HTML5, CSS3 (Bootstrap may be used)
- **Database:** SQLite3
- **Tools:** Git, VS Code

## 🛠️ Setup Instructions

Follow these steps to run the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/jubaer-bhuiyan/clinic_management_system.git
cd clinic_management_system
```

### 2. Create a Virtual Environment
```bash
python -m venv env
env\Scripts\activate   # For Windows
# source env/bin/activate  # For Mac/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

> If `requirements.txt` is not present, manually install Django:
```bash
pip install django
```

### 4. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the Development Server
```bash
python manage.py runserver
```

Open your browser and visit:  
👉 `http://127.0.0.1:8000/`

---

## 🗃️ Project Structure

```
clinic_management_system/
│
├── clinic_app/             # Core Django app
├── clinic_management/      # Project settings
├── db.sqlite3              # Default SQLite DB
├── manage.py               # Django CLI
└── templates/              # HTML templates
```

---

## 🧪 Testing

You can write and run tests using Django's built-in test framework:

```bash
python manage.py test
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙋‍♂️ Author

**Md. Jubaer Bhuiyan**  
GitHub: [@jubaer-bhuiyan](https://github.com/jubaer-bhuiyan)
