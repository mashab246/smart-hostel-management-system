from flask import Blueprint, render_template, request, redirect, session, flash
from config import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

# Home
@auth_bp.route("/")
def home():
    return "Smart Hostel System Backend Running"


# Register
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == 'POST':

        reg_no = request.form['reg_no'].strip()
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        program = request.form['program']
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form['gender']

        #Hash password
        hashed_password = generate_password_hash(password)

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            #Check if reg_no already exists
            cursor.execute("SELECT * FROM users WHERE reg_no = %s", (reg_no,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Registration number already exists!", "error")
                return redirect('/register')

            #Insert into users table (authentication)
            cursor.execute("""
                INSERT INTO users (reg_no, password_hash, role)
                VALUES (%s, %s, %s)
            """, (reg_no, hashed_password, "student"))

            connection.commit()

            #Get newly created user id
            user_id = cursor.lastrowid

            #Insert into students table (profile)
            cursor.execute("""
                INSERT INTO students 
                (user_id, first_name, last_name, program, email, phone, gender)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, first_name, last_name, program, email, phone, gender))

            connection.commit()

            flash("Account created successfully!", "success")
            return redirect('/login')

        except Exception as e:
            connection.rollback()
            print(e)
            flash("Error creating account.", "error")

        finally:
            cursor.close()
            connection.close()

    return render_template('register.html')


# Login
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        reg_no = request.form["reg_no"].strip().lower()
        password = request.form["password"]
        selected_role = request.form["role"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE LOWER(reg_no)=LOWER(%s)", (reg_no,))
        user = cursor.fetchone()

        if user:

            if user["role"] == selected_role and check_password_hash(user["password_hash"], password):

                session["user_id"] = user["id"]
                session["role"] = user["role"]

                if user["role"] == "admin":
                    return redirect("/admin-dashboard")
                else:
                    return redirect("/student-dashboard")

            else:
                return "Invalid credentials or role selected "
        else:
            return "User not found"

    return render_template("login.html")


# Logout
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")