"""
Task 04 · Update, Delete & Data Integrity [Hard]

Databases aren't just for storing — managing and maintaining data is equally important

Goal
Build a student grade management system — insert, update, delete, and validate data.

Create grades.db with a students table: id, name, subject, score, grade TEXT
Insert 15 students with various scores (mix them between 40-100)
Write a function assign_grade(score) that returns A/B/C/D/F based on score
UPDATE all rows — set the grade column using your function
DELETE all students who scored below 50 — they didn't pass
Add a new column passed BOOLEAN using ALTER TABLE — set it based on score >= 50
Query: show count of students per grade, ordered from A to F
Handle the case where a student name is entered twice — check before inserting
"""

import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MySQL server
try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conn.cursor()
    print("Connected to MySQL server successfully!")
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    exit(1)
    
# Create students database and table
cursor.execute("CREATE DATABASE IF NOT EXISTS grades_db")
cursor.execute("USE grades_db")

# Drop table if it already exists to start fresh
cursor.execute("DROP TABLE IF EXISTS students") # Start with a clean slate each time

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    subject VARCHAR(100) NOT NULL,
    score INT NOT NULL,
    grade CHAR(1)
)
""")

# Function to assign grade based on score
def assign_grade(score):
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'

# inser function to insert student data with grade assignment and duplicate name check
def insert_student(name, subject, score):
    grade = assign_grade(score)
    
    # Check for duplicate name
    cursor.execute("SELECT COUNT(*) FROM students WHERE name = %s", (name,))
    if cursor.fetchone()[0] > 0: # If a student with the same name already exists
        print(f"Student with name '{name}' already exists. Skipping insertion.")
        return
    
    cursor.execute("INSERT INTO students (name, subject, score, grade) VALUES (%s, %s, %s, %s)", 
                   (name, subject, score, grade))
    conn.commit()
    print(f"Inserted student: {name}, Subject: {subject}, Score: {score}, Grade: {grade}")

# Insert 15 students with various scores
students_data = [
    ("Alice", "Math", 95),
    ("Bob", "Science", 82),
    ("Charlie", "History", 76),
    ("David", "Math", 65),
    ("Eve", "Science", 55),
    ("Frank", "History", 45),
    ("Grace", "Math", 88),
    ("Heidi", "Science", 92),
    ("Ivan", "History", 70),
    ("Judy", "Math", 60),
    ("Karl", "Science", 50),
    ("Leo", "History", 40),
    ("Mallory", "Math", 85),
    ("Nina", "Science", 78),
    ("Oscar", "History", 68)
]

# Insert students into the database
for s in students_data:
    insert_student(*s)
    
# update all rows to set the grade column using the assign_grade function
cursor.execute("SELECT id, score FROM students")
students = cursor.fetchall()
for student_id, score in students:
    grade = assign_grade(score)
    cursor.execute("UPDATE students SET grade = %s WHERE id = %s", (grade, student_id))
    print(f"Updated student ID {student_id} with grade {grade}")
conn.commit()

# Add a new column passed BOOLEAN using ALTER TABLE — set it based on score >= 50
cursor.execute("ALTER TABLE students ADD COLUMN passed BOOLEAN")
# Update passed column based on score
cursor.execute("UPDATE students SET passed = (score >= 50)") # Set passed to True if score >= 50, else False
cursor.execute("SELECT name, passed FROM students")
students = cursor.fetchall()
for name, passed in students:
    print(f"Updated student {name} with passed status {passed}")
conn.commit()

# Delete all students who scored below 50 — they didn't pass
cursor.execute("DELETE FROM students WHERE score < 50")
conn.commit()

# Query: show count of students per grade, ordered from A to F
cursor.execute("""
SELECT grade, COUNT(*) as count
FROM students
GROUP BY grade
ORDER BY FIELD(grade, 'A', 'B', 'C', 'D', 'F')
""")
grade_counts = cursor.fetchall()
for grade, count in grade_counts:
    print(f"Grade: {grade}, Count: {count}")

# Final data check
cursor.execute("SELECT * FROM students")
print("\nFinal Data:")
for row in cursor.fetchall():
    print(row)

# Close the connection
cursor.close()
conn.close()