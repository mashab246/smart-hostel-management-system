from flask import Flask, render_template, request, redirect, session, flash
from config import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "your_secret_key_here"
@app.route("/")
def home():
    return "Smart Hostel System Backend Running"

#regiter API
@app.route('/register', methods=['GET', 'POST'])
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

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

#login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        reg_no = request.form["reg_no"].strip().lower()
        password = request.form["password"]
        selected_role = request.form["role"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
         
        cursor.execute("SELECT * FROM users WHERE LOWER(reg_no) = LOWER(%s)", (reg_no,))
        user = cursor.fetchone()
        
        print("User from DB:", user)

        if user:
            if user["role"] == selected_role and check_password_hash(user["password_hash"], password):

                session["user_id"] = user["id"]
                session["role"] = user["role"]

                if user["role"] == "admin":
                    return redirect("/admin-dashboard")
                else:
                    return redirect("/student-dashboard")

            else:
                return "Invalid credentials or role selected"

        else:
            return "User not found"

    return render_template("login.html")

@app.route("/student-dashboard")
def student_dashboard():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("student_dashboard.html")

#user dashboard
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT students.*
        FROM students
        JOIN users ON students.user_id = users.id
        WHERE users.id = %s
    """, (session["user_id"],))

    student = cursor.fetchone()

    return render_template("student_dashboard.html")

#logout logic12
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

#allocation page
@app.route("/apply", methods=["GET", "POST"])
def apply_hostel():

    if "user_id" not in session:
        return redirect("/login")

    # If GET request → show button
    if request.method == "GET":
        return """
            <h2>Apply for Hostel</h2>
            <form method="POST">
                <button type="submit">Confirm Application</button>
            </form>
            <br>
            <a href="/dashboard">Back</a>
        """

    # If POST request → process allocation
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
            SELECT id FROM students
            WHERE user_id = %s
        """, (session["user_id"],))

    student = cursor.fetchone()
    student_id = student["id"]

    # Check existing allocation
    cursor.execute("""
        SELECT * FROM allocations 
        WHERE student_id=%s AND allocation_status='active'
    """, (student_id,))

    if cursor.fetchone():
        return "You already have a room."

    # Find available room
    cursor.execute("""
        SELECT * FROM rooms 
        WHERE current_occupancy < capacity 
        LIMIT 1
    """)
    room = cursor.fetchone()

    if not room:
        return "No rooms available."

    room_id = room["id"]

    # Insert allocation
    cursor.execute("""
        INSERT INTO allocations (student_id, room_id)
        VALUES (%s, %s)
    """, (student_id, room_id))

    # Update room occupancy
    cursor.execute("""
        UPDATE rooms
        SET current_occupancy = current_occupancy + 1
        WHERE id=%s
    """, (room_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return "Room allocated successfully!"

#view allocation page
@app.route("/my-allocation")
def my_allocation():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get student_id
    cursor.execute("""
        SELECT id 
        FROM students 
        WHERE user_id=%s
    """, (session["user_id"],))

    student = cursor.fetchone()

    if not student:
        return "Student profile not found."

    student_id = student["id"]

    # Get allocation details
    cursor.execute("""
        SELECT allocations.*, rooms.room_number, hostels.hostel_name
        FROM allocations
        JOIN rooms ON allocations.room_id = rooms.id
        JOIN hostels ON rooms.hostel_id = hostels.id
        WHERE allocations.student_id = %s
        AND allocations.allocation_status = 'active'
    """, (student_id,))

    allocation = cursor.fetchone()

    cursor.close()
    conn.close()

    if not allocation:
        return """
            <h2>No Room Assigned</h2>
            <a href="/dashboard">Back to Dashboard</a>
        """

    return f"""
        <h2>My Hostel Allocation</h2>
        <p><b>Hostel:</b> {allocation['hostel_name']}</p>
        <p><b>Room Number:</b> {allocation['room_number']}</p>
        <p><b>Status:</b> {allocation['allocation_status']}</p>
        <br>
        <a href="/dashboard">Back to Dashboard</a>
    """
#thefty report 
@app.route("/report-theft", methods=["GET", "POST"])
def report_theft():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get student_id
    cursor.execute("""
        SELECT id FROM students
        WHERE user_id=%s
    """, (session["user_id"],))

    student = cursor.fetchone()
    student_id = student["id"]

    if request.method == "GET":
        return render_template("report_theft.html")

    description = request.form["description"]

    # Get student's active room
    cursor.execute("""
        SELECT room_id FROM allocations
        WHERE student_id=%s
        AND allocation_status='active'
    """, (student_id,))

    allocation = cursor.fetchone()

    if not allocation:
        return "You must have a room to report theft."

    room_id = allocation["room_id"]

    # Insert theft report
    cursor.execute("""
        INSERT INTO theft_reports (student_id, room_id, description)
        VALUES (%s, %s, %s)
    """, (student_id, room_id, description))

    conn.commit()
    cursor.close()
    conn.close()

    return "Theft report submitted successfully!"

#admin dahboard
@app.route("/admin-dashboard")
def admin_dashboard():

    if "user_id" not in session or session.get("role") != "admin":
        return "Access Denied"

    return render_template("admin_dashboard.html")

@app.route("/view-allocations")
def view_allocations():

    if "user_id" not in session or session.get("role") != "admin":
        return "Access Denied"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT allocations.student_id,
               rooms.room_number,
               hostels.hostel_name,
               allocations.allocation_status
        FROM allocations
        JOIN rooms ON allocations.room_id = rooms.id
        JOIN hostels ON rooms.hostel_id = hostels.id
    """)

    allocations = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("view_allocations.html", allocations=allocations)

@app.route("/view-reports")
def view_reports():

    # Only admin allowed
    if "user_id" not in session or session.get("role") != "admin":
        return "Access Denied"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM theft_reports
        ORDER BY reported_on DESC
    """)

    reports = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("view_reports.html", reports=reports)

@app.route('/create_hostel', methods=['GET', 'POST'])
def create_hostel():
    if request.method == 'POST':
        hostelname = request.form['hostelname']
        location = request.form['location']
        capacity = request.form['capacity']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO hostels (hostelname, location, capacity) VALUES (%s, %s, %s)",
            (hostelname, location, capacity)
        )

        connection.commit()
        cursor.close()
        connection.close()

        return "Hostel Created Successfully!"

    return render_template('create_hostel.html')

@app.route('/create_room', methods=['GET', 'POST'])
def create_room():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM hostels")
    hostels = cursor.fetchall()

    if request.method == 'POST':
        room_no = request.form['room_no']
        hostelid = request.form['hostelid']
        capacity = request.form['capacity']

        cursor.execute(
            """INSERT INTO rooms 
               (hostelid, room_no, capacity, current_occupancy) 
               VALUES (%s, %s, %s, %s)""",
            (hostelid, room_no, capacity, 0)
        )

        connection.commit()
        return "Room Created Successfully!"

    return render_template('create_room.html', hostels=hostels)

@app.route('/view_students')
def view_students():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get only students
    cursor.execute("SELECT * FROM users WHERE role = 'student'")
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('view_students.html', students=students)


@app.route('/reset-admin')
def reset_admin():

    from werkzeug.security import generate_password_hash

    connection = get_db_connection()
    cursor = connection.cursor()

    new_password = generate_password_hash("Admin123")

    cursor.execute("""
        UPDATE users
        SET password_hash = %s
        WHERE reg_no = %s
    """, (new_password, "ADMIN001"))

    connection.commit()
    cursor.close()
    connection.close()

    return "Admin password reset successfully!"

if __name__ == "__main__":
    app.run(debug=True)