from implementation.db import SQLiteAdapter, ValidationError
import os
import json

def run_verification():
    db_path = "mcp_lab.db"
    if not os.path.exists(db_path):
        print("Database not found. Run init_db.py first.")
        return

    adapter = SQLiteAdapter(db_path)
    
    print("--- 1. Testing list_tables ---")
    tables = adapter.list_tables()
    print(f"Tables: {tables}")

    print("\n--- 2. Testing search (A1 students) ---")
    students = adapter.search("students", filters={"cohort": "A1"})
    print(json.dumps(students, indent=2))

    print("\n--- 3. Testing aggregate (Avg grade) ---")
    avg_grade = adapter.aggregate("enrollments", "AVG", "grade")
    print(json.dumps(avg_grade, indent=2))

    import time
    unique_email = f"eve_{int(time.time())}@example.com"
    try:
        new_student = adapter.insert("students", {"name": "Eve Adams", "cohort": "C3", "email": unique_email})
        print(f"Inserted: {new_student}")
    except ValidationError as e:
        print(f"Insert failed: {e}")

    print("\n--- 5. Testing error handling (Invalid table) ---")
    try:
        adapter.search("non_existent_table")
    except ValidationError as e:
        print(f"Caught expected error: {e}")

if __name__ == "__main__":
    run_verification()
