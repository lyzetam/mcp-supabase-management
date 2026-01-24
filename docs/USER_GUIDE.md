# User Guide

Step-by-step tutorials for common Supabase operations using the Management MCP.

## Prerequisites

Before starting, ensure you have:

1. Claude Code installed and configured
2. Supabase Management MCP added to `~/.claude.json`
3. Valid `SUPABASE_ACCESS_TOKEN` configured

## Getting Started

### Find Your Organization ID

Before creating projects, you need your organization ID.

**Goal:** Get the organization ID for project creation.

1. Call `list_organizations()`
2. Find your organization in the response
3. Copy the `id` field

**Example response:**
```json
[
  {
    "id": "org_abc123xyz",
    "name": "My Organization"
  }
]
```

### List All Projects

**Goal:** See all Supabase projects across your organizations.

1. Call `list_projects()`
2. Review the project list

**Example response:**
```json
[
  {
    "id": "forjadxkmzabhidnkwyh",
    "name": "quantum-trades",
    "organization_id": "org_abc123",
    "region": "us-east-1",
    "status": "ACTIVE_HEALTHY"
  }
]
```

## Project Management

### Create a New Project

**Goal:** Create a new Supabase project for your application.

1. Get your organization ID (see above)
2. Choose a region (us-east-1, eu-west-1, ap-southeast-1, etc.)
3. Call `create_project()`:

```
create_project(
  name="my-new-app",
  organization_id="org_abc123xyz",
  region="us-east-1"
)
```

4. Wait for project initialization (usually 30-60 seconds)
5. Note the `id` (project reference) from the response

**Tip:** The database password is auto-generated. Store it securely if needed.

### Get Project Details

**Goal:** View configuration and status for a specific project.

1. Call `get_project()` with the project reference:

```
get_project(project_ref="forjadxkmzabhidnkwyh")
```

2. Review the response for status, region, and configuration

### Get API Keys

**Goal:** Retrieve anon and service_role keys for your application.

1. Call `get_api_keys()`:

```
get_api_keys(project_ref="forjadxkmzabhidnkwyh")
```

2. The response includes:
   - `anon` key - For client-side use (respects RLS)
   - `service_role` key - For server-side use (bypasses RLS)

**Warning:** Never expose the service_role key in client-side code.

### Delete a Project

**Goal:** Permanently delete a project and all its data.

1. Ensure you have backups if needed
2. Call `delete_project()` with confirmation:

```
delete_project(
  project_ref="forjadxkmzabhidnkwyh",
  confirm=true
)
```

**Warning:** This action is irreversible. All data will be lost.

## Database Operations

### List Tables

**Goal:** See all tables in your database.

1. Call `list_tables()`:

```
list_tables(project_ref="forjadxkmzabhidnkwyh")
```

2. Review the table list with schema and owner information

### Execute SQL Queries

**Goal:** Run SQL queries against your database.

1. Call `execute_sql()` with your query:

```
execute_sql(
  project_ref="forjadxkmzabhidnkwyh",
  query="SELECT * FROM users WHERE active = true LIMIT 10"
)
```

**Common queries:**

```sql
-- Count rows in a table
SELECT COUNT(*) FROM users;

-- Check table structure
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'users';

-- Create a table
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  content TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
```

### View Extensions

**Goal:** See installed PostgreSQL extensions.

1. Call `list_extensions()`:

```
list_extensions(project_ref="forjadxkmzabhidnkwyh")
```

**Common extensions:**
- `uuid-ossp` - UUID generation
- `pgcrypto` - Cryptographic functions
- `pg_stat_statements` - Query statistics
- `vector` - pgvector for embeddings

### Generate TypeScript Types

**Goal:** Create TypeScript types from your database schema.

1. Call `generate_types()`:

```
generate_types(project_ref="forjadxkmzabhidnkwyh")
```

2. Copy the output to your project's `types/supabase.ts`

## Database Branches

### List Branches

**Goal:** View all database branches for a project.

```
list_branches(project_ref="forjadxkmzabhidnkwyh")
```

### Create a Branch

**Goal:** Create a database branch for development/testing.

```
create_branch(
  project_ref="forjadxkmzabhidnkwyh",
  branch_name="feature-auth",
  git_branch="feature/auth-system"
)
```

**Use cases:**
- Test migrations before production
- Develop features in isolation
- Preview environments

### Reset a Branch

**Goal:** Reset a branch to match production data.

1. Get the branch ID from `list_branches()`
2. Call `reset_branch()`:

```
reset_branch(branch_id="branch_abc123")
```

### Delete a Branch

**Goal:** Remove a branch when no longer needed.

```
delete_branch(branch_id="branch_abc123")
```

## Edge Functions

### List Functions

**Goal:** See all edge functions in a project.

```
list_functions(project_ref="forjadxkmzabhidnkwyh")
```

### Get Function Details

**Goal:** View configuration for a specific function.

```
get_function(
  project_ref="forjadxkmzabhidnkwyh",
  function_slug="send-email"
)
```

### Deploy a Function

**Goal:** Deploy a new or updated edge function.

```
deploy_function(
  project_ref="forjadxkmzabhidnkwyh",
  function_slug="hello-world",
  code="""
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  const { name } = await req.json()
  return new Response(
    JSON.stringify({ message: `Hello ${name}!` }),
    { headers: { "Content-Type": "application/json" } }
  )
})
""",
  verify_jwt=true
)
```

**Parameters:**
- `verify_jwt=true` - Requires valid Supabase JWT (default)
- `verify_jwt=false` - Publicly accessible

## Secrets Management

### List Secrets

**Goal:** See all secret names configured for a project.

```
list_secrets(project_ref="forjadxkmzabhidnkwyh")
```

**Note:** Only names are returned, not values.

### Set Secrets

**Goal:** Create or update secrets for edge functions.

```
set_secrets(
  project_ref="forjadxkmzabhidnkwyh",
  secrets=[
    {"name": "STRIPE_SECRET_KEY", "value": "sk_live_..."},
    {"name": "SENDGRID_API_KEY", "value": "SG...."}
  ]
)
```

### Delete Secrets

**Goal:** Remove secrets from a project.

```
delete_secrets(
  project_ref="forjadxkmzabhidnkwyh",
  secret_names=["OLD_API_KEY", "DEPRECATED_SECRET"]
)
```

## Logs and Monitoring

### Get Service Logs

**Goal:** View logs for debugging and monitoring.

```
get_logs(
  project_ref="forjadxkmzabhidnkwyh",
  service="api",
  limit=100
)
```

**Available services:**
| Service | Description |
|---------|-------------|
| `api` | PostgREST API requests |
| `auth` | Authentication events |
| `db` | Database queries and errors |
| `realtime` | Real-time subscriptions |
| `storage` | File storage operations |
| `functions` | Edge function invocations |

**Troubleshooting tips:**
- Check `auth` logs for login issues
- Check `db` logs for query errors
- Check `functions` logs for edge function failures

## Common Workflows

### Set Up a New Project

1. Create project: `create_project(name, org_id, region)`
2. Get API keys: `get_api_keys(project_ref)`
3. Create tables: `execute_sql(project_ref, create_table_sql)`
4. Enable RLS: `execute_sql(project_ref, enable_rls_sql)`
5. Generate types: `generate_types(project_ref)`

### Debug an Issue

1. Check logs: `get_logs(project_ref, service="api")`
2. Query database: `execute_sql(project_ref, debug_query)`
3. Review function logs: `get_logs(project_ref, service="functions")`

### Deploy Changes

1. Create branch: `create_branch(project_ref, "staging")`
2. Test migrations on branch
3. Reset if needed: `reset_branch(branch_id)`
4. Delete branch after merge: `delete_branch(branch_id)`

## Troubleshooting

### "Invalid access token"

**Cause:** Token expired or incorrect.

**Solution:**
1. Generate new token at https://supabase.com/dashboard/account/tokens
2. Update `SUPABASE_ACCESS_TOKEN` in `~/.claude.json`
3. Restart Claude Code

### "Project not found"

**Cause:** Incorrect project reference or deleted project.

**Solution:**
1. Run `list_projects()` to get correct references
2. Verify project exists in Supabase dashboard

### "Permission denied"

**Cause:** Token lacks required permissions.

**Solution:**
1. Check token scope in Supabase dashboard
2. Generate new token with required permissions

### SQL Errors

**Cause:** Invalid SQL syntax or permissions.

**Solution:**
1. Test query in Supabase SQL Editor first
2. Check table/column names
3. Verify RLS policies if accessing as authenticated user
