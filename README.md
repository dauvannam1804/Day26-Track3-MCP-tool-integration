# Lab: SQLite Database MCP Server with FastMCP

This project implements a Model Context Protocol (MCP) server that exposes a SQLite database through various tools and resources. It is built using the [FastMCP](https://gofastmcp.com/) framework.

## Features

### Core Tools
- **`search`**: Search records with support for filtering, column selection, and sorting.
- **`insert`**: Safely insert new records into the database.
- **`aggregate`**: Perform calculations like `COUNT`, `AVG`, `SUM`, `MIN`, and `MAX`.

### MCP Resources
- **`schema://database`**: Exposes the full database schema as JSON.
- **`schema://table/{table_name}`**: Exposes the schema for a specific table.

### Bonus Features Implemented
1.  **Pagination & Rich Metadata**: `search` results include `total_count`, `has_more`, `limit`, and `offset`.
2.  **Authentication (SSE/HTTP)**: API Key protection for network-based transports via `X-API-Key` header.
3.  **Database Abstraction**: Uses an interface (`DatabaseAdapter`) to support future database types (e.g., PostgreSQL).
4.  **Health Check Tool**: A `health_check` tool to verify server and database status.

---

## Getting Started

### 1. Prerequisites
- [uv](https://github.com/astral-sh/uv) (recommended) or Python 3.10+
- SQLite3 (usually built-in with Python)

### 2. Installation
Clone the repository and install dependencies:
```bash
uv sync
```

### 3. Initialize the Database
This script creates the `mcp_lab.db` file and populates it with seed data (`students`, `courses`, `enrollments`).
```bash
uv run python -m implementation.init_db
```

### 4. Verify the Implementation
Run the verification script to test the database adapter logic:
```bash
uv run python -m implementation.verify_server
```
You can also run the automated test suite:
```bash
uv run pytest
```

---

## Running the MCP Server

### A. Standard Stdio (Default)
Ideal for use with local MCP clients like Gemini CLI or Claude Code.
```bash
uv run python -m implementation.mcp_server
```

### B. SSE Transport with Authentication (Bonus)
To run as a network service with API Key protection:
```bash
export MCP_API_KEY=your-secret-key
uv run python -m implementation.mcp_server sse
```
*Note: Clients must then include the header `X-API-Key: your-secret-key`.*

---

## Client Configuration Examples

### Gemini CLI
```bash
gemini mcp add sqlite-lab $(which python3) $(pwd)/implementation/mcp_server.py --description "SQLite Lab Server"
```

### Claude Code
Add to your `~/.mcp.json`:
```json
{
  "mcpServers": {
    "sqlite-lab": {
      "command": "uv",
      "args": ["run", "--project", "/absolute/path/to/project", "python", "-m", "implementation.mcp_server"]
    }
  }
}
```

### Antigravity / Gemini CLI (mcp_config.json)
Antigravity and Gemini CLI often share the same configuration format. Create or update your `mcp_config.json`:
```json
{
  "mcpServers": {
    "sqlite-lab": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/home/namdv/workspace/Day26-Track3-MCP-tool-integration",
        "python",
        "-m",
        "implementation.mcp_server"
      ]
    }
  }
}
```
*Note: Make sure to replace the path with your actual project path.*

---

## Project Structure
- `implementation/db.py`: Core logic and database adapter.
- `implementation/init_db.py`: Database setup and seeding.
- `implementation/mcp_server.py`: FastMCP server definition.
- `implementation/verify_server.py`: Manual verification script.
- `implementation/tests/`: Automated test suite.
- `mcp_lab.db`: SQLite database file (generated after init).
