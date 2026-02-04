# mcp-supabase-management

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCP server and LangChain tools for the Supabase Management API -- manage projects, databases, edge functions, secrets, and branches across all your Supabase organizations.

## Features

24 tools across 7 categories:

| Category | Tools | Description |
|----------|-------|-------------|
| Organizations | `list_organizations` | List all organizations |
| Projects | `list_projects`, `get_project`, `create_project`, `delete_project`, `get_api_keys`, `get_project_url` | Full project lifecycle management |
| Database | `list_tables`, `execute_sql`, `list_extensions`, `list_migrations`, `generate_types` | SQL execution, schema inspection, TypeScript type generation |
| Branches | `list_branches`, `create_branch`, `delete_branch`, `reset_branch` | Database branching for development workflows |
| Functions | `list_functions`, `get_function`, `deploy_function` | Edge function management and deployment |
| Secrets | `list_secrets`, `set_secrets`, `delete_secrets` | Project secret management |
| Logs | `get_logs` | Access logs for API, Auth, DB, Realtime, Storage, and Functions |

## Installation

```bash
# Core library
pip install .

# With MCP server support
pip install ".[mcp]"

# With LangChain tools
pip install ".[langchain]"

# Everything
pip install ".[all]"
```

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_ACCESS_TOKEN` | Yes | _(none)_ | Supabase Management API access token (`sbp_*` prefix). Get one at [supabase.com/dashboard/account/tokens](https://supabase.com/dashboard/account/tokens) |

### `.env` Example

```bash
SUPABASE_ACCESS_TOKEN=sbp_your_token_here
```

## Quick Start

### As MCP Server

```bash
mcp-supabase-management
```

Add to Claude Code (`~/.claude.json`):

```json
{
  "mcpServers": {
    "supabase-management": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-supabase-management", "run", "mcp-supabase-management"],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "sbp_your_token_here"
      }
    }
  }
}
```

### As LangChain Tools

```python
from mcp_supabase_management.langchain_tools import TOOLS, supabase_list_projects, supabase_execute_sql

# Use all 24 tools with an agent
agent = create_react_agent(llm, TOOLS)

# Or use individual tools
print(supabase_list_projects.invoke({}))
print(supabase_execute_sql.invoke({
    "project_ref": "your_project_ref",
    "query": "SELECT * FROM users LIMIT 10",
}))
```

### As Python Library

```python
from mcp_supabase_management.client import SupabaseManagementClient
from mcp_supabase_management.operations import projects, database

client = SupabaseManagementClient(access_token="sbp_...")
all_projects = projects.list_projects(client)
result = database.execute_sql(client, "project_ref", "SELECT 1")
```

## Error Handling

The server returns structured error messages:

```json
{
  "error": "API Error (401): Invalid access token"
}
```

Common errors:
- `401` - Invalid or expired access token
- `404` - Project or resource not found
- `422` - Invalid request parameters
- `429` - Rate limit exceeded

## License

MIT
