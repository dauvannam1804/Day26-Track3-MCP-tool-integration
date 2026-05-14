import sqlite3
import re
from typing import List, Dict, Any, Optional, Protocol
from abc import ABC, abstractmethod

class ValidationError(Exception):
    """Raised when a request cannot be safely executed."""

class DatabaseAdapter(ABC):
    @abstractmethod
    def list_tables(self) -> List[str]:
        pass

    @abstractmethod
    def get_table_schema(self, table: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def search(self, table: str, columns: Optional[List[str]] = None, filters: Optional[Dict[str, Any]] = None, limit: int = 20, offset: int = 0, order_by: Optional[str] = None, descending: bool = False) -> Dict[str, Any]:
        pass

    @abstractmethod
    def insert(self, table: str, values: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def aggregate(self, table: str, metric: str, column: Optional[str] = None, filters: Optional[Dict[str, Any]] = None, group_by: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

class SQLiteAdapter(DatabaseAdapter):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def list_tables(self) -> List[str]:
        with self.connect() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            return [row["name"] for row in cursor.fetchall()]

    def get_table_schema(self, table: str) -> List[Dict[str, Any]]:
        self._validate_identifier(table)
        with self.connect() as conn:
            cursor = conn.execute(f"PRAGMA table_info({table})")
            return [dict(row) for row in cursor.fetchall()]

    def _validate_identifier(self, identifier: str):
        if not identifier or not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
            raise ValidationError(f"Invalid identifier: {identifier}")

    def search(self, table: str, columns: Optional[List[str]] = None, filters: Optional[Dict[str, Any]] = None, limit: int = 20, offset: int = 0, order_by: Optional[str] = None, descending: bool = False) -> Dict[str, Any]:
        self._validate_identifier(table)
        if order_by:
            self._validate_identifier(order_by)
        
        col_clause = "*"
        if columns:
            for col in columns:
                self._validate_identifier(col)
            col_clause = ", ".join(columns)

        # Base query for count
        count_query = f"SELECT COUNT(*) as total FROM {table}"
        
        # Base query for data
        data_query = f"SELECT {col_clause} FROM {table}"
        
        params = []
        where_clause = ""

        if filters:
            where_clauses = []
            for col, val in filters.items():
                self._validate_identifier(col)
                where_clauses.append(f"{col} = ?")
                params.append(val)
            where_clause = " WHERE " + " AND ".join(where_clauses)

        count_query += where_clause
        data_query += where_clause

        if order_by:
            data_query += f" ORDER BY {order_by} {'DESC' if descending else 'ASC'}"

        data_query += f" LIMIT ? OFFSET ?"
        data_params = params + [limit, offset]

        with self.connect() as conn:
            try:
                # Get total count for pagination bonus
                total_count = conn.execute(count_query, params).fetchone()["total"]
                
                # Get data
                cursor = conn.execute(data_query, data_params)
                rows = [dict(row) for row in cursor.fetchall()]
                
                return {
                    "metadata": {
                        "total_count": total_count,
                        "limit": limit,
                        "offset": offset,
                        "has_more": total_count > (offset + limit)
                    },
                    "data": rows
                }
            except sqlite3.OperationalError as e:
                raise ValidationError(f"Database error: {e}")

    def insert(self, table: str, values: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_identifier(table)
        if not values:
            raise ValidationError("Empty insert request")

        cols = []
        placeholders = []
        params = []
        for col, val in values.items():
            self._validate_identifier(col)
            cols.append(col)
            placeholders.append("?")
            params.append(val)

        query = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"

        with self.connect() as conn:
            try:
                cursor = conn.execute(query, params)
                conn.commit()
                row_id = cursor.lastrowid
                return {"id": row_id, **values}
            except sqlite3.IntegrityError as e:
                raise ValidationError(f"Integrity error: {e}")
            except sqlite3.OperationalError as e:
                raise ValidationError(f"Database error: {e}")

    def aggregate(self, table: str, metric: str, column: Optional[str] = None, filters: Optional[Dict[str, Any]] = None, group_by: Optional[str] = None) -> List[Dict[str, Any]]:
        allowed_metrics = ["COUNT", "AVG", "SUM", "MIN", "MAX"]
        if metric.upper() not in allowed_metrics:
            raise ValidationError(f"Unsupported metric: {metric}")

        self._validate_identifier(table)
        if column:
            self._validate_identifier(column)
        if group_by:
            self._validate_identifier(group_by)

        agg_col = column if column else "*"
        select_clause = f"{metric.upper()}({agg_col}) AS result"
        if group_by:
            select_clause = f"{group_by}, {select_clause}"

        query = f"SELECT {select_clause} FROM {table}"
        params = []

        if filters:
            where_clauses = []
            for col, val in filters.items():
                self._validate_identifier(col)
                where_clauses.append(f"{col} = ?")
                params.append(val)
            query += " WHERE " + " AND ".join(where_clauses)

        if group_by:
            query += f" GROUP BY {group_by}"

        with self.connect() as conn:
            try:
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
            except sqlite3.OperationalError as e:
                raise ValidationError(f"Database error: {e}")

# Note: PostgreSQLAdapter could be implemented here following the same DatabaseAdapter interface.
