from flask import Blueprint, render_template, request, redirect, session
from config import get_db_connection

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin-dashboard")
def admin_dashboard():

    if "user_id" not in session or session.get("role") != "admin":
        return "Access Denied"

    return render_template("admin_dashboard.html")

@admin_bp.route("/view-allocations")
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

@admin_bp.route("/view-reports")
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

@admin_bp.route('/create_hostel', methods=['GET', 'POST'])
def create_hostel():
    if request.method == 'POST':
        hostelname = request.form['hostelname']
        location = request.form['location']
        capacity = request.form['capacity']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO hostels (hostel_name, location, capacity) VALUES (%s, %s, %s)",
            (hostelname, location, capacity)
        )

        connection.commit()
        cursor.close()
        connection.close()

        return "Hostel Created Successfully!"

    return render_template('create_hostel.html')

@admin_bp.route('/create_room', methods=['GET', 'POST'])
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
               (hostel_id, room_number, capacity, current_occupancy) 
               VALUES (%s, %s, %s, %s)""",
            (hostelid, room_no, capacity, 0)
        )

        connection.commit()
        return "Room Created Successfully!"

    return render_template('create_room.html', hostels=hostels)

@admin_bp.route('/view_students')
def view_students():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get only students
    cursor.execute("SELECT * FROM users WHERE role = 'student'")
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('view_students.html', students=students)


@admin_bp.route('/reset-admin')
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


    