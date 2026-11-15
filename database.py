import sqlite3
import os
import hashlib


# ============================================================
# AIZA ACADEMY ATTENDANCE MANAGEMENT SYSTEM
# Database Module
# Made by Shahbaz Ali Chandio
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_FILE = os.path.join(DATABASE_DIR, "academy_attendance.db")

os.makedirs(DATABASE_DIR, exist_ok=True)

DB_PATH = DATABASE_FILE


# ------------------------------------------------------------
# Database Connection
# ------------------------------------------------------------

def get_connection():
    connection = sqlite3.connect(DATABASE_FILE)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ------------------------------------------------------------
# Password Hash
# ------------------------------------------------------------

def hash_password(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ------------------------------------------------------------
# Initialize Database
# ------------------------------------------------------------

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    # ========================================================
    # USERS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            full_name TEXT NOT NULL,

            role TEXT NOT NULL,

            active INTEGER DEFAULT 1,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ========================================================
    # STUDENTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id TEXT UNIQUE NOT NULL,

            name TEXT NOT NULL,

            father_name TEXT,

            class_name TEXT NOT NULL,

            section TEXT,

            gender TEXT,

            date_of_birth TEXT,

            phone TEXT,

            parent_phone TEXT,

            address TEXT,

            admission_date TEXT,

            qr_code_path TEXT,

            active INTEGER DEFAULT 1,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ========================================================
    # ATTENDANCE
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id INTEGER NOT NULL,

            attendance_date TEXT NOT NULL,

            attendance_time TEXT,

            status TEXT NOT NULL,

            method TEXT,

            marked_by TEXT,

            remarks TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(student_id)
            REFERENCES students(id)
            ON DELETE CASCADE,

            UNIQUE(student_id, attendance_date)
        )
    """)

    # ========================================================
    # SETTINGS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (

            key TEXT PRIMARY KEY,

            value TEXT
        )
    """)

    # ========================================================
    # DEFAULT ADMIN
    # ========================================================

    admin_password = hash_password("admin123")

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (
            username,
            password,
            full_name,
            role
        )

        VALUES (?, ?, ?, ?)
    """, (
        "admin",
        admin_password,
        "System Administrator",
        "admin"
    ))

    # ========================================================
    # DEFAULT TEACHER
    # ========================================================

    teacher_password = hash_password("teacher123")

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (
            username,
            password,
            full_name,
            role
        )

        VALUES (?, ?, ?, ?)
    """, (
        "teacher",
        teacher_password,
        "Demo Teacher",
        "teacher"
    ))

    # ========================================================
    # DEFAULT SETTINGS
    # ========================================================

    default_settings = {

        "academy_name":
            "Aiza Academy Sakrand & Nawabshah",

        "developer":
            "Shahbaz Ali Chandio",

        "low_attendance_percentage":
            "75",

        "late_after_minutes":
            "30"
    }

    for key, value in default_settings.items():

        cursor.execute("""
            INSERT OR IGNORE INTO settings
            (
                key,
                value
            )

            VALUES (?, ?)
        """, (
            key,
            value
        ))

    connection.commit()

    connection.close()


# ------------------------------------------------------------
# Login
# ------------------------------------------------------------

def authenticate_user(username, password):

    connection = get_connection()

    cursor = connection.cursor()

    hashed = hash_password(password)

    cursor.execute("""
        SELECT
            id,
            username,
            full_name,
            role
        FROM users
        WHERE username = ?
        AND password = ?
        AND active = 1
    """, (
        username,
        hashed
    ))

    user = cursor.fetchone()

    connection.close()

    if user:

        return dict(user)

    return None


# ------------------------------------------------------------
# Add Student
# ------------------------------------------------------------

def add_student(
    student_id,
    name,
    father_name,
    class_name,
    section,
    gender,
    date_of_birth,
    phone,
    parent_phone,
    address,
    admission_date,
    qr_code_path
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO students
        (
            student_id,
            name,
            father_name,
            class_name,
            section,
            gender,
            date_of_birth,
            phone,
            parent_phone,
            address,
            admission_date,
            qr_code_path
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        name,
        father_name,
        class_name,
        section,
        gender,
        date_of_birth,
        phone,
        parent_phone,
        address,
        admission_date,
        qr_code_path
    ))

    connection.commit()

    student_database_id = cursor.lastrowid

    connection.close()

    return student_database_id


# ------------------------------------------------------------
# Find Student By Student ID
# ------------------------------------------------------------

def get_student_by_student_id(student_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM students
        WHERE student_id = ?
        AND active = 1
    """, (
        student_id,
    ))

    student = cursor.fetchone()

    connection.close()

    if student:

        return dict(student)

    return None


# ------------------------------------------------------------
# Get All Students
# ------------------------------------------------------------

def get_all_students():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM students
        WHERE active = 1
        ORDER BY class_name, name
    """)

    students = cursor.fetchall()

    connection.close()

    return [dict(student) for student in students]


# ------------------------------------------------------------
# Mark Attendance
# ------------------------------------------------------------

def mark_attendance(
    student_database_id,
    attendance_date,
    attendance_time,
    status,
    method,
    marked_by,
    remarks=""
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM attendance

        WHERE student_id = ?
        AND attendance_date = ?
    """, (
        student_database_id,
        attendance_date
    ))

    existing = cursor.fetchone()

    if existing:

        cursor.execute("""
            UPDATE attendance

            SET
                attendance_time = ?,
                status = ?,
                method = ?,
                marked_by = ?,
                remarks = ?

            WHERE id = ?
        """, (
            attendance_time,
            status,
            method,
            marked_by,
            remarks,
            existing["id"]
        ))

    else:

        cursor.execute("""
            INSERT INTO attendance
            (
                student_id,
                attendance_date,
                attendance_time,
                status,
                method,
                marked_by,
                remarks
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            student_database_id,
            attendance_date,
            attendance_time,
            status,
            method,
            marked_by,
            remarks
        ))

    connection.commit()

    connection.close()


# ------------------------------------------------------------
# Daily Attendance
# ------------------------------------------------------------

def get_daily_attendance(date):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT

            s.student_id,

            s.name,

            s.father_name,

            s.class_name,

            s.section,

            s.parent_phone,

            COALESCE(
                a.status,
                'Absent'
            ) AS status,

            a.attendance_time,

            a.method,

            a.marked_by

        FROM students s

        LEFT JOIN attendance a

        ON s.id = a.student_id

        AND a.attendance_date = ?

        WHERE s.active = 1

        ORDER BY
            s.class_name,
            s.section,
            s.name
    """, (
        date,
    ))

    records = cursor.fetchall()

    connection.close()

    return [dict(record) for record in records]


# ------------------------------------------------------------
# Student Attendance History
# ------------------------------------------------------------

def get_student_attendance(
    student_database_id,
    from_date,
    to_date
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT

            attendance_date,

            attendance_time,

            status,

            method,

            marked_by,

            remarks

        FROM attendance

        WHERE student_id = ?

        AND attendance_date
        BETWEEN ?
        AND ?

        ORDER BY attendance_date
    """, (
        student_database_id,
        from_date,
        to_date
    ))

    records = cursor.fetchall()

    connection.close()

    return [dict(record) for record in records]


# ------------------------------------------------------------
# Get Setting
# ------------------------------------------------------------

def get_setting(key):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT value
        FROM settings
        WHERE key = ?
    """, (
        key,
    ))

    result = cursor.fetchone()

    connection.close()

    if result:

        return result["value"]

    return None
# ============================================================
# STUDENT MANAGEMENT - ADDITIONAL FUNCTIONS
# ============================================================


# ------------------------------------------------------------
# Get Student By Database ID
# ------------------------------------------------------------

def get_student_by_id(student_database_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM students
        WHERE id = ?
        AND active = 1
    """, (
        student_database_id,
    ))

    student = cursor.fetchone()

    connection.close()

    if student:
        return dict(student)

    return None


# ------------------------------------------------------------
# Generate Next Student ID
# ------------------------------------------------------------

def generate_student_id():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT student_id
        FROM students
        ORDER BY id DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    connection.close()

    if not result:

        return "AA-0001"

    last_id = result["student_id"]

    try:

        number = int(
            last_id.split("-")[-1]
        )

        number += 1

    except (ValueError, IndexError):

        number = 1

    return f"AA-{number:04d}"


# ------------------------------------------------------------
# Update Student
# ------------------------------------------------------------

def update_student(
    student_database_id,
    name,
    father_name,
    class_name,
    section,
    gender,
    date_of_birth,
    phone,
    parent_phone,
    address,
    admission_date,
    qr_code_path=None
):

    connection = get_connection()

    cursor = connection.cursor()

    if qr_code_path is not None:

        cursor.execute("""
            UPDATE students

            SET
                name = ?,
                father_name = ?,
                class_name = ?,
                section = ?,
                gender = ?,
                date_of_birth = ?,
                phone = ?,
                parent_phone = ?,
                address = ?,
                admission_date = ?,
                qr_code_path = ?

            WHERE id = ?
        """, (
            name,
            father_name,
            class_name,
            section,
            gender,
            date_of_birth,
            phone,
            parent_phone,
            address,
            admission_date,
            qr_code_path,
            student_database_id
        ))

    else:

        cursor.execute("""
            UPDATE students

            SET
                name = ?,
                father_name = ?,
                class_name = ?,
                section = ?,
                gender = ?,
                date_of_birth = ?,
                phone = ?,
                parent_phone = ?,
                address = ?,
                admission_date = ?

            WHERE id = ?
        """, (
            name,
            father_name,
            class_name,
            section,
            gender,
            date_of_birth,
            phone,
            parent_phone,
            address,
            admission_date,
            student_database_id
        ))

    connection.commit()

    connection.close()


# ------------------------------------------------------------
# Deactivate Student
# ------------------------------------------------------------

def deactivate_student(student_database_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE students

        SET active = 0

        WHERE id = ?
    """, (
        student_database_id,
    ))

    connection.commit()

    connection.close()


# ------------------------------------------------------------
# Search Students
# ------------------------------------------------------------

def search_students(search_text=""):

    connection = get_connection()

    cursor = connection.cursor()

    search = f"%{search_text.strip()}%"

    cursor.execute("""
        SELECT *
        FROM students

        WHERE active = 1

        AND (
            student_id LIKE ?
            OR name LIKE ?
            OR father_name LIKE ?
            OR class_name LIKE ?
            OR section LIKE ?
            OR phone LIKE ?
            OR parent_phone LIKE ?
        )

        ORDER BY
            class_name,
            section,
            name
    """, (
        search,
        search,
        search,
        search,
        search,
        search,
        search
    ))

    students = cursor.fetchall()

    connection.close()

    return [
        dict(student)
        for student in students
    ]


# ------------------------------------------------------------
# Get Students By Class
# ------------------------------------------------------------

def get_students_by_class(class_name):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM students

        WHERE class_name = ?
        AND active = 1

        ORDER BY
            section,
            name
    """, (
        class_name,
    ))

    students = cursor.fetchall()

    connection.close()

    return [
        dict(student)
        for student in students
    ]


# ------------------------------------------------------------
# Get All Classes
# ------------------------------------------------------------

def get_all_classes():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT class_name
        FROM students
        WHERE active = 1
        ORDER BY class_name
    """)

    classes = cursor.fetchall()

    connection.close()

    return [
        row["class_name"]
        for row in classes
    ]


# ------------------------------------------------------------
# Count Students
# ------------------------------------------------------------

def get_student_count():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM students
        WHERE active = 1
    """)

    result = cursor.fetchone()

    connection.close()

    return result["total"]
# ------------------------------------------------------------
# Update Setting
# ------------------------------------------------------------

def update_setting(key, value):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
    """, (
        key,
        str(value)
    ))

    connection.commit()

    connection.close()
    # ------------------------------------------------------------
# Update Setting
# ------------------------------------------------------------

def update_setting(key, value):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
    """, (
        key,
        str(value)
    ))

    connection.commit()
    connection.close()
# ------------------------------------------------------------
# Update Setting
# ------------------------------------------------------------

def update_setting(key, value):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
    """, (
        key,
        value
    ))

    connection.commit()

    connection.close()