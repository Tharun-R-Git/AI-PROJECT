# modules/database.py
import sqlite3
import pandas as pd
from modules import branch_mapper

DB_FILE = "placement_users.db"

def init_database():
    """Initializes all required tables in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # User table for login (Student or Admin)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        hashed_password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('student', 'admin'))
    )
    """)
    
    # Student profiles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_profiles (
        email TEXT PRIMARY KEY,
        roll_number TEXT,
        full_name TEXT,
        cgpa REAL,
        branch TEXT,
        class_10_perc REAL,
        class_12_perc REAL,
        year_gap INTEGER,
        backlogs INTEGER,
        FOREIGN KEY (email) REFERENCES users (email)
    )
    """)

    # Jobs table (for admin to post)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        job_description TEXT,
        criteria_json TEXT,  -- Store the extracted criteria as a JSON string
        posted_by_email TEXT,
        ctc TEXT,
        stipend TEXT,
        last_date TEXT,
        company_description TEXT,
        pdf_path TEXT  -- Path to uploaded PDF JD (optional)
    )
    """)
    
    # Add new columns to existing jobs table if they don't exist (for migration)
    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN ctc TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN stipend TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN last_date TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN company_description TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN pdf_path TEXT")
    except:
        pass

    # Eligibility mapping table (many-to-many)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eligibility (
        job_id INTEGER,
        student_email TEXT,
        PRIMARY KEY (job_id, student_email),
        FOREIGN KEY (job_id) REFERENCES jobs (job_id),
        FOREIGN KEY (student_email) REFERENCES student_profiles (email)
    )
    """)

    conn.commit()
    conn.close()

def add_user_and_profile(email, hashed_password, role, profile_data):
    """Adds a new user and their profile (if student) in a single transaction."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        # Add to users table
        cursor.execute("INSERT INTO users (email, hashed_password, role) VALUES (?, ?, ?)",
                       (email, hashed_password, role))
        
        # If student, add to profiles table
        if role == 'student':
            cursor.execute("""
            INSERT INTO student_profiles (email, roll_number, full_name, cgpa, branch, class_10_perc, class_12_perc, year_gap, backlogs)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email,
                profile_data['roll_number'],
                profile_data['full_name'],
                profile_data['cgpa'],
                profile_data['branch'],
                profile_data['class_10_perc'],
                profile_data['class_12_perc'],
                profile_data['year_gap'],
                profile_data['backlogs']
            ))
        
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        conn.rollback()
        return False, "This email is already registered."
    except Exception as e:
        conn.rollback()
        return False, f"An error occurred: {e}"
    finally:
        conn.close()

def get_user(email):
    """Fetches a user's login details (password, role)."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT hashed_password, role FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user  # Returns (hashed_password, role) or None

def get_students_matching_criteria(criteria):
    """
    Finds students who meet the criteria parsed from the JD.
    'criteria' is a dict, e.g.:
    {'cgpa': 7.5, 'branches': ['CSE', 'ECE'], 'backlogs': 0, 'year_gap': 1}
    """
    conn = sqlite3.connect(DB_FILE)
    
    # Base query
    query = "SELECT * FROM student_profiles WHERE "
    conditions = []
    params = []

    if 'cgpa' in criteria and criteria['cgpa'] is not None:
        conditions.append("cgpa >= ?")
        params.append(criteria['cgpa'])
        
    if 'backlogs' in criteria and criteria['backlogs'] is not None:
        conditions.append("backlogs <= ?")
        params.append(criteria['backlogs'])

    if 'year_gap' in criteria and criteria['year_gap'] is not None:
        conditions.append("year_gap <= ?")
        params.append(criteria['year_gap'])

    if 'branches' in criteria and criteria['branches']:
        # Normalize branch names to standard codes
        normalized_branches = branch_mapper.normalize_branch_list(criteria['branches'])
        if normalized_branches:
            placeholders = ', '.join('?' for _ in normalized_branches)
            conditions.append(f"branch IN ({placeholders})")
            params.extend(normalized_branches)

    if not conditions:
        return pd.DataFrame() # No criteria, return empty

    query += " AND ".join(conditions)
    
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        print(f"Error querying students: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def save_job_and_eligibility(company, jd, criteria_json, eligible_student_emails, admin_email, 
                            ctc=None, stipend=None, last_date=None, company_description=None, pdf_path=None):
    """Saves the job and links all eligible students to it."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        # 1. Save the job
        cursor.execute("""
        INSERT INTO jobs (company_name, job_description, criteria_json, posted_by_email, 
                         ctc, stipend, last_date, company_description, pdf_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company, jd, criteria_json, admin_email, ctc, stipend, last_date, company_description, pdf_path))
        
        job_id = cursor.lastrowid
        
        # 2. Link eligible students
        eligibility_data = [(job_id, email) for email in eligible_student_emails]
        cursor.executemany("INSERT INTO eligibility (job_id, student_email) VALUES (?, ?)", eligibility_data)
        
        conn.commit()
        return True, job_id
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_eligible_jobs_for_student(student_email):
    """Fetches all jobs a specific student is eligible for."""
    conn = sqlite3.connect(DB_FILE)
    query = """
    SELECT j.company_name, j.job_description, j.criteria_json, j.ctc, j.stipend, 
           j.last_date, j.company_description, j.pdf_path
    FROM jobs j
    JOIN eligibility e ON j.job_id = e.job_id
    WHERE e.student_email = ?
    ORDER BY j.job_id DESC
    """
    try:
        df = pd.read_sql_query(query, conn, params=(student_email,))
        return df
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return pd.DataFrame()
    finally:
        conn.close()