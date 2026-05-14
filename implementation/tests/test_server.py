import pytest
import json
import os
from implementation.db import SQLiteAdapter, ValidationError

@pytest.fixture
def adapter():
    db_path = "test_mcp.db"
    # Ensure a fresh DB for tests
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3_connect(db_path)
    conn.execute("CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, cohort TEXT)")
    conn.execute("INSERT INTO students (name, cohort) VALUES ('Test Student', 'T1')")
    conn.commit()
    conn.close()
    
    yield SQLiteAdapter(db_path)
    
    if os.path.exists(db_path):
        os.remove(db_path)

def sqlite3_connect(path):
    import sqlite3
    return sqlite3.connect(path)

def test_search_valid(adapter):
    results = adapter.search("students", filters={"cohort": "T1"})
    assert len(results) == 1
    assert results[0]["name"] == "Test Student"

def test_search_invalid_table(adapter):
    with pytest.raises(ValidationError):
        adapter.search("ghost_table")

def test_insert_valid(adapter):
    new_data = {"name": "New Student", "cohort": "T2"}
    result = adapter.insert("students", new_data)
    assert result["id"] is not None
    assert result["name"] == "New Student"

def test_aggregate_valid(adapter):
    result = adapter.aggregate("students", "COUNT")
    assert result[0]["result"] == 1

def test_sql_injection_prevention(adapter):
    # This should fail validation because of the space or special characters
    with pytest.raises(ValidationError):
        adapter.search("students; DROP TABLE students;")
