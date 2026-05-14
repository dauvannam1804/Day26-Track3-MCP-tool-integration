from fastmcp import FastMCP
from implementation.db import SQLiteAdapter, ValidationError
import json
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Create the server object.
mcp = FastMCP("SQLite Lab MCP Server")

# --- Bonus: Authentication Middleware for SSE/HTTP ---
class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Only enforce auth for HTTP/SSE paths, not during local stdio testing if possible
        # However, Starlette middleware applies to all HTTP requests.
        # MCP Inspector and clients using SSE will send HTTP requests.
        
        api_key = os.environ.get("MCP_API_KEY")
        if api_key:
            auth_header = request.headers.get("X-API-Key")
            if auth_header != api_key:
                return Response("Unauthorized: Invalid or missing X-API-Key", status_code=401)
        
        return await call_next(request)

# Add the middleware to the FastMCP server
mcp.add_middleware(APIKeyMiddleware)

# Initialize database adapter
db_path = os.path.join(os.path.dirname(__file__), "..", "mcp_lab.db")
adapter = SQLiteAdapter(db_path)

@mcp.tool(name="search")
def search(table: str, filters: dict = None, columns: list = None, limit: int = 20, offset: int = 0, order_by: str = None, descending: bool = False):
    """Search records in a table with pagination and metadata."""
    try:
        results = adapter.search(table, columns, filters, limit, offset, order_by, descending)
        return json.dumps(results, indent=2)
    except ValidationError as e:
        return f"Error: {str(e)}"

@mcp.tool(name="insert")
def insert(table: str, values: dict):
    """Insert a new record into a table."""
    try:
        result = adapter.insert(table, values)
        return json.dumps(result, indent=2)
    except ValidationError as e:
        return f"Error: {str(e)}"

@mcp.tool(name="aggregate")
def aggregate(table: str, metric: str, column: str = None, filters: dict = None, group_by: str = None):
    """Perform aggregate calculations."""
    try:
        results = adapter.aggregate(table, metric, column, filters, group_by)
        return json.dumps(results, indent=2)
    except ValidationError as e:
        return f"Error: {str(e)}"

@mcp.resource("schema://database")
def database_schema() -> str:
    """Get the full database schema."""
    tables = adapter.list_tables()
    schema = {}
    for table in tables:
        schema[table] = adapter.get_table_schema(table)
    return json.dumps(schema, indent=2)

@mcp.resource("schema://table/{table_name}")
def table_schema(table_name: str) -> str:
    """Get the schema for a specific table."""
    try:
        schema = adapter.get_table_schema(table_name)
        return json.dumps(schema, indent=2)
    except ValidationError as e:
        return f"Error: {str(e)}"

@mcp.tool()
def health_check():
    """Check if the database connection is healthy."""
    try:
        tables = adapter.list_tables()
        return f"Healthy. Connected to {db_path}. Found {len(tables)} tables."
    except Exception as e:
        return f"Unhealthy: {str(e)}"

if __name__ == "__main__":
    mcp.run()
