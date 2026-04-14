from flask import Blueprint, render_template, request, redirect, session
from config import get_db_connection

student_bp = Blueprint("student", __name__)


@student_bp.route("/student-dashboard")
def student_dashboard():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("student_dashboard.html")


@student_bp.route("/dashboard")
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

    return render_template("student_dashboard.html", student=student)

#allocation page
@student_bp.route("/apply", methods=["GET", "POST"])
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
@student_bp.route("/my-allocation")
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
@student_bp.route("/report-theft", methods=["GET", "POST"])
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
