import sqlite3
import os

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cohort TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    instructor TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    grade REAL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);
"""

SEED_SQL = """
INSERT OR IGNORE INTO students (name, cohort, email) VALUES 
('Alice Smith', 'A1', 'alice@example.com'),
('Bob Jones', 'A1', 'bob@example.com'),
('Charlie Brown', 'B2', 'charlie@example.com'),
('David Wilson', 'B2', 'david@example.com');

INSERT OR IGNORE INTO courses (title, instructor) VALUES 
('Intro to Python', 'Prof. Python'),
('Advanced Databases', 'Dr. SQL'),
('Web Development', 'Ms. JS');

INSERT OR IGNORE INTO enrollments (student_id, course_id, grade) VALUES 
(1, 1, 95.0),
(1, 2, 88.0),
(2, 1, 75.5),
(3, 3, 92.0),
(4, 2, 85.0);
"""

def create_database(db_path="mcp_lab.db"):
    """
    1. Open SQLite database file.
    2. Execute schema SQL.
    3. Execute seed SQL.
    4. Commit.
    5. Return database path.
    """
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.executescript(SEED_SQL)
        conn.commit()
        print(f"Database initialized at {os.path.abspath(db_path)}")
        return db_path
    finally:
        conn.close()

if __name__ == "__main__":
    create_database()
