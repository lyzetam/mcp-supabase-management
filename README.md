# Supabase Management MCP Server

MCP server for the Supabase Management API. Create projects, manage API keys, execute SQL, and more.

## Features

- **Organizations**: List organizations
- **Projects**: Create, list, get, delete projects
- **API Keys**: Retrieve anon and service_role keys
- **Database**: Execute SQL queries
- **Branches**: Create, list, delete database branches
- **Edge Functions**: List and inspect functions
- **Secrets**: Manage project secrets

## Installation

```bash
cd ~/dev/mcp-supabase-management
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Configuration

Set the `SUPABASE_ACCESS_TOKEN` environment variable with your Management API token.

Get a token from: https://supabase.com/dashboard/account/tokens

### Claude Code Configuration

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "supabase-management": {
      "command": "uv",
      "args": ["--directory", "~/dev/mcp-supabase-management", "run", "mcp-supabase-management"],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "sbp_your_token_here"
      }
    }
  }
}
```

Or fetch from AWS Secrets Manager dynamically.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_organizations` | List all organizations |
| `list_projects` | List all projects |
| `get_project` | Get project details |
| `create_project` | Create a new project |
| `delete_project` | Delete a project (requires confirmation) |
| `get_api_keys` | Get project API keys |
| `execute_sql` | Run SQL on project database |
| `list_branches` | List database branches |
| `create_branch` | Create a database branch |
| `delete_branch` | Delete a database branch |
| `list_functions` | List edge functions |
| `get_function` | Get function details |
| `list_secrets` | List project secrets |
| `set_secrets` | Create/update secrets |
| `delete_secrets` | Delete secrets |

## Usage Examples

### Create a Project

```
create_project(
  name="my-app",
  organization_id="your-org-id",
  region="us-east-1"
)
```

### Get API Keys

```
get_api_keys(project_ref="abcdefghijklmnop")
```

### Execute SQL

```
execute_sql(
  project_ref="abcdefghijklmnop",
  query="SELECT * FROM users LIMIT 10"
)
```

## Project References

| Project | Reference ID | HTTP MCP |
|---------|--------------|----------|
| Quantum | `abcdefghijklmnopqrst` | `supabase-quantum` |
| Phoenix | `zzdwykxtcxcahxtzojtw` | `supabase-phoenix` |
| Zeroed | `tsrqponmlkjihgfedcba` | `supabase-zeroed` |
| Bible | `rehpmoxczibgkwcawelo` | `supabase-bible` |

## MCP Architecture

Two types of Supabase MCPs work together:

1. **Management MCP** (`supabase-management`) - Uses Management API for cross-project operations:
   - Create/delete projects
   - Execute SQL on any project
   - Manage secrets, branches, edge functions
   - List all organizations and projects

2. **Project HTTP MCPs** (`supabase-*`) - Official Supabase MCPs for project-specific features:
   - `search_docs` - Search project documentation
   - `list_tables`, `execute_sql` - Database operations
   - Project-scoped tooling
