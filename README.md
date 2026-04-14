Smart Hostel Management System

Overview

The Smart Hostel Management System is a web-based application built using Flask and MySQL that helps manage hostel operations efficiently. It provides functionalities for both students and administrators, including room allocation, hostel management, and theft reporting.

This system was designed to simplify hostel processes such as registration, room assignment, and monitoring student activities.

---

Features

Student Features

- Register an account
- Login securely
- Apply for hostel accommodation
- View room allocation details
- Report theft incidents

Admin Features

- Admin dashboard
- Create hostels
- Create and manage rooms
- View student records
- View room allocations
- View theft reports
- Reset admin password

---

System Architecture

The project follows a modular Flask structure using Blueprints:

project/
│
├── app.py
├── config.py
│
├── routes/
│   ├── auth.py
│   ├── student.py
│   └── admin.py
│
├── templates/
├── static/
└── requirements.txt

---

Technologies Used

- Backend: Flask (Python)
- Database: MySQL
- Frontend: HTML, CSS
- Authentication: Werkzeug Security (Password Hashing)
- Version Control: Git & GitHub

---

Authentication & Security

- Passwords are securely hashed using:
  - "generate_password_hash()"
  - "check_password_hash()"
- Session-based authentication is used to manage user login
- Role-based access control (Admin / Student)

---
Database Structure

Main tables used:

- "users" → authentication (login details)
- "students" → student profiles
- "hostels" → hostel information
- "rooms" → room details and capacity
- "allocations" → room assignments
- "theft_reports" → reported incidents

---

How to Run the Project

1. Clone the Repository

git clone https://github.com/yourusername/smart-hostel-system.git
cd smart-hostel-system

---

2. Create Virtual Environment

python -m venv venv

Activate:

venv\Scripts\activate   # Windows

---

3. Install Dependencies

pip install -r requirements.txt

---

4. Setup Database

- Create a MySQL database
- Import your SQL file (if provided)
- Update database connection in:

config.py

---

5. Run the Application

python app.py

Then open:

http://127.0.0.1:5000

---

Usage Flow

1. Register as a student
2. Login
3. Apply for hostel
4. View allocation
5. Report theft (if needed)

Admin can:

- Manage hostels and rooms
- Monitor allocations
- View reports

---

Important Notes

- Ensure MySQL server is running
- Do not upload "venv/" to GitHub
- Make sure ".gitignore" is properly configured

---

Future Improvements

- Improved UI/UX design
- Email/SMS notifications
- Room allocation optimization
- Admin approval system
- Deployment to cloud (Render / Railway)

---

Author

Musa Galiwango

---

License

This project is for academic and educational purposes.