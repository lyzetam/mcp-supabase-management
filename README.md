# Supabase Management MCP Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Unified MCP server for the Supabase Management API. Manage all your Supabase projects from Claude Code.

## Features

- **Organizations** - List organizations
- **Projects** - Create, list, get, delete projects; retrieve API keys
- **Database** - Execute SQL, list tables, view extensions and migrations
- **Branches** - Create, list, delete, reset database branches
- **Edge Functions** - List, inspect, deploy functions
- **Secrets** - List, set, delete project secrets
- **Logs** - Access logs for all services (API, Auth, DB, Realtime, Storage, Functions)
- **TypeScript** - Generate types from database schema

## Quick Start

```bash
# Clone and install
cd ~/dev/mcp-supabase-management
uv venv && source .venv/bin/activate
uv pip install -e .

# Set your token
export SUPABASE_ACCESS_TOKEN="sbp_your_token_here"

# Test it works
mcp-supabase-management
```

## Installation

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Supabase Management API token ([get one here](https://supabase.com/dashboard/account/tokens))

### Setup

```bash
cd ~/dev/mcp-supabase-management
uv venv
source .venv/bin/activate
uv pip install -e .
```

### Claude Code Configuration

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "supabase-management": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "/Users/zz/dev/mcp-supabase-management", "run", "mcp-supabase-management"],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "sbp_your_token_here"
      }
    }
  }
}
```

## Usage

### List All Projects

```
list_projects()
```

### Execute SQL on Any Project

```
execute_sql(
  project_ref="forjadxkmzabhidnkwyh",
  query="SELECT * FROM users LIMIT 10"
)
```

### Create a New Project

```
create_project(
  name="my-new-app",
  organization_id="org_abc123",
  region="us-east-1"
)
```

### Get API Keys

```
get_api_keys(project_ref="forjadxkmzabhidnkwyh")
```

### Deploy Edge Function

```
deploy_function(
  project_ref="forjadxkmzabhidnkwyh",
  function_slug="hello-world",
  code="Deno.serve(() => new Response('Hello!'))"
)
```

## Project References

| Project | Reference ID | HTTP MCP |
|---------|--------------|----------|
| Quantum | `forjadxkmzabhidnkwyh` | `supabase-quantum` |
| Phoenix | `zzdwykxtcxcahxtzojtw` | `supabase-phoenix` |
| Zeroed | `njfjihorcqllcwularcq` | `supabase-zeroed` |
| Bible | `rehpmoxczibgkwcawelo` | `supabase-bible` |

## Architecture

Two types of Supabase MCPs work together:

### Management MCP (this server)

Uses the Supabase Management API for cross-project operations:
- Create/delete projects
- Execute SQL on any project
- Manage secrets, branches, edge functions
- Access logs across all services

### Project HTTP MCPs

Official Supabase MCPs for project-specific features:
- `search_docs` - Search project documentation
- `list_tables`, `execute_sql` - Database operations
- Real-time subscriptions

Both are configured globally in `~/.claude.json` for full coverage.

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design and data flow |
| [User Guide](docs/USER_GUIDE.md) | Step-by-step tutorials |
| [API Reference](docs/API_REFERENCE.md) | Complete tool documentation |
| [Runbook](docs/RUNBOOK.md) | Operational procedures |

## Available Tools

| Category | Tools |
|----------|-------|
| Organizations | `list_organizations` |
| Projects | `list_projects`, `get_project`, `create_project`, `delete_project`, `get_api_keys`, `get_project_url` |
| Database | `list_tables`, `execute_sql`, `list_extensions`, `list_migrations`, `generate_types` |
| Branches | `list_branches`, `create_branch`, `delete_branch`, `reset_branch` |
| Functions | `list_functions`, `get_function`, `deploy_function` |
| Secrets | `list_secrets`, `set_secrets`, `delete_secrets` |
| Logs | `get_logs` |

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT
