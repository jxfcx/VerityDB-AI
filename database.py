"""
VerityDB AI- Database Setup

Creates a local SQLite database and stores
fictional government department records.
"""

import sqlite3

# Connect to a local SQLite database.
# If the database doesn't exist, SQLite creates it.
connection = sqlite3.connect("verity.db")

# A cursor lets us execute SQL commands
cursor = connection.cursor()

# Create the departments table if it doesn't exist.
cursor.execute("""
CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL UNIQUE
    )
""")

cursor.executemany("""
INSERT OR IGNORE INTO departments
(department_id, department_name)
VALUES (?, ?)
""", [
    (1, "Licensing"),
    (2, "Permits"),
    (3, "Public Utilities")
])

# Enable foreign key enforcement for this connection.
cursor.execute("PRAGMA foreign_keys = ON")

# Create the applications table.
cursor.execute("""
CREATE TABLE IF NOT EXISTS applications (
    application_id INTEGER PRIMARY KEY,
    applicant_name TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    submission_date TEXT NOT NULL,
    
    FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
)
""")

# Insert fictional government applications
cursor.executemany("""
INSERT OR IGNORE INTO applications
(application_id, applicant_name, department_id, status, submission_date)
VALUES (?, ?, ?, ?, ?)
""", [
    (101, "John Smith", 1, "Pending", "2026-09-10"),
    (102, "Anthony Wilson", 2, "Approved", "2026-09-15"),
    (103, "Sofia Martinez", 1, "Pending", "2026-09-20"),
    (104, "Alex Garcia", 3, "Rejected", "2026-09-22"),
    (105, "Daniel Johnson", 2, "Pending", "2026-10-01"),
    (106, "Isabella Torres", 3, "Approved", "2026-10-05")
])

# Save our database changes
connection.commit()

#Retrieve the departments to verify the data.
cursor.execute("SELECT * FROM departments")

for row in cursor.fetchall():
    print(row)

# Retrieve applications with their department names.
# JOIN combines related information from two tables

cursor.execute("""
SELECT
    applications.application_id,
    applications.applicant_name,
    departments.department_name,
    applications.status
FROM applications
JOIN departments
    ON applications.department_id = departments.department_id
""")

print("\nGOVERNMENT APPLICATIONS:")

for row in cursor.fetchall():
    print(row)

# Close the connection when finishedc
connection.close()