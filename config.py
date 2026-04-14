import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Musagagob246@",
        database="smart_hostel_db"
    )