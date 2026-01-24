# Architecture

## Overview

The Supabase Management MCP provides a unified interface for managing multiple Supabase projects through Claude Code. It wraps the Supabase Management API and exposes operations as MCP tools.

## System Context

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Claude Code                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     MCP Client                               │   │
│  └──────────────────────────┬──────────────────────────────────┘   │
│                             │                                        │
│         ┌───────────────────┼───────────────────┐                   │
│         │                   │                   │                   │
│         ▼                   ▼                   ▼                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│  │ supabase-   │    │ supabase-   │    │ supabase-   │            │
│  │ management  │    │ quantum     │    │ phoenix     │  ...       │
│  │ (stdio)     │    │ (HTTP)      │    │ (HTTP)      │            │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘            │
│         │                  │                  │                     │
└─────────┼──────────────────┼──────────────────┼─────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ Management  │    │ Project API │    │ Project API │
   │ API         │    │ (quantum)   │    │ (phoenix)   │
   │ api.supa... │    │ forjad...   │    │ zzdwyk...   │
   └─────────────┘    └─────────────┘    └─────────────┘
```

## Components

### MCP Server (`src/server.py`)

The main entry point that:
- Initializes the MCP server with stdio transport
- Registers all available tools
- Routes tool calls to the appropriate client methods
- Handles errors and formats responses

### Supabase Client (`SupabaseClient`)

A unified async client that wraps the Management API:

```python
class SupabaseClient:
    def __init__(self, access_token: str):
        self.management = httpx.AsyncClient(
            base_url="https://api.supabase.com/v1",
            headers={"Authorization": f"Bearer {access_token}"}
        )
```

**Responsibilities:**
- Authentication with Management API token
- HTTP request/response handling
- Error transformation
- Timeout management (60s default)

## Data Flow

### Tool Execution Flow

```
1. Claude Code invokes tool
   │
   ▼
2. MCP Server receives call_tool()
   │
   ├── Validates arguments
   ├── Gets SupabaseClient instance
   │
   ▼
3. Client method executes
   │
   ├── Builds HTTP request
   ├── Sends to Management API
   ├── Parses response
   │
   ▼
4. Result returned as TextContent
   │
   ├── JSON-formatted for success
   └── Error message for failures
```

### Authentication Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Claude Code    │     │  MCP Server     │     │  Supabase API   │
│                 │     │                 │     │                 │
│  Starts MCP     │────▶│  Reads env var  │     │                 │
│  with env vars  │     │  SUPABASE_      │     │                 │
│                 │     │  ACCESS_TOKEN   │     │                 │
│                 │     │        │        │     │                 │
│  Calls tool     │────▶│  Creates client │────▶│  Validates      │
│                 │     │  with Bearer    │     │  token          │
│                 │     │  auth header    │     │                 │
│  Receives       │◀────│  Returns        │◀────│  Returns data   │
│  result         │     │  formatted JSON │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## API Endpoints

The Management API endpoints used:

| Category | Endpoint | Methods |
|----------|----------|---------|
| Organizations | `/organizations` | GET |
| Projects | `/projects`, `/projects/{ref}` | GET, POST, DELETE |
| API Keys | `/projects/{ref}/api-keys` | GET |
| Database | `/projects/{ref}/database/query` | POST |
| Branches | `/projects/{ref}/branches`, `/branches/{id}` | GET, POST, DELETE |
| Functions | `/projects/{ref}/functions`, `/projects/{ref}/functions/{slug}` | GET, POST |
| Secrets | `/projects/{ref}/secrets` | GET, POST, DELETE |
| Logs | `/projects/{ref}/analytics/endpoints/logs.all` | GET |
| Types | `/projects/{ref}/types/typescript` | GET |

## MCP Architecture

### Dual MCP Strategy

Two complementary MCP types provide complete Supabase coverage:

| MCP Type | Transport | Scope | Use Case |
|----------|-----------|-------|----------|
| Management | stdio (local) | All projects | Admin operations, cross-project queries |
| Project HTTP | HTTP (remote) | Single project | Real-time, project-specific features |

### Why Both?

**Management MCP advantages:**
- Single token for all projects
- Cross-project operations
- Administrative tasks (create/delete projects)
- No per-project configuration needed

**Project HTTP MCP advantages:**
- Official Supabase implementation
- Additional features (search_docs)
- Direct project API access
- Potentially lower latency

## Error Handling

### Error Categories

| HTTP Status | Meaning | Action |
|-------------|---------|--------|
| 401 | Invalid/expired token | Refresh token |
| 403 | Insufficient permissions | Check token scope |
| 404 | Resource not found | Verify project_ref |
| 422 | Invalid parameters | Check input |
| 429 | Rate limited | Retry with backoff |
| 500+ | Server error | Retry or report |

### Error Response Format

```python
try:
    result = await client.method()
    return TextContent(text=json.dumps(result))
except httpx.HTTPStatusError as e:
    return TextContent(text=f"API Error ({e.response.status_code}): {e.response.text}")
except Exception as e:
    return TextContent(text=f"Error: {str(e)}")
```

## Security Considerations

### Token Storage

- Token passed via environment variable
- Never logged or exposed in responses
- Stored in Claude Code config (user-managed)

### Permissions

The Management API token scope determines available operations:
- Read-only tokens: List, get operations only
- Full access tokens: All operations including create/delete

### Sensitive Operations

Destructive operations require confirmation:

```python
if name == "delete_project":
    if not arguments.get("confirm"):
        return TextContent(text="ERROR: Must set confirm=true")
```

## Performance

### Timeouts

- Default timeout: 60 seconds
- SQL queries may take longer for complex operations
- Consider query optimization for large datasets

### Connection Pooling

The `httpx.AsyncClient` maintains connection pooling:
- Reuses TCP connections
- Handles keep-alive automatically
- Single client instance per MCP session

## Future Considerations

### Potential Enhancements

1. **Caching** - Cache project lists, reduce API calls
2. **Batch Operations** - Multiple SQL queries in one call
3. **Streaming** - Stream large query results
4. **Webhooks** - React to project events

### Known Limitations

1. No real-time subscriptions (use HTTP MCPs)
2. Edge function deployment requires full code (no incremental)
3. Log access limited to recent entries
4. No direct file storage operations
