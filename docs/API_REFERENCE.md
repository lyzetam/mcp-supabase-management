# API Reference

Complete documentation for all Supabase Management MCP tools.

## Organizations

### list_organizations

List all Supabase organizations accessible with your token.

**Parameters:** None

**Returns:** Array of organization objects

**Example:**
```
list_organizations()
```

**Response:**
```json
[
  {
    "id": "org_abc123xyz",
    "name": "My Organization",
    "billing_email": "billing@example.com"
  }
]
```

---

## Projects

### list_projects

List all Supabase projects across all organizations.

**Parameters:** None

**Returns:** Array of project objects

**Example:**
```
list_projects()
```

**Response:**
```json
[
  {
    "id": "forjadxkmzabhidnkwyh",
    "organization_id": "org_abc123",
    "name": "quantum-trades",
    "region": "us-east-1",
    "status": "ACTIVE_HEALTHY",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### get_project

Get details for a specific project.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID (e.g., `forjadxkmzabhidnkwyh`) |

**Returns:** Project object with full configuration

**Example:**
```
get_project(project_ref="forjadxkmzabhidnkwyh")
```

**Response:**
```json
{
  "id": "forjadxkmzabhidnkwyh",
  "name": "quantum-trades",
  "organization_id": "org_abc123",
  "region": "us-east-1",
  "status": "ACTIVE_HEALTHY",
  "database": {
    "host": "db.forjadxkmzabhidnkwyh.supabase.co",
    "version": "15.1.0"
  }
}
```

---

### create_project

Create a new Supabase project.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | string | Yes | Project name |
| `organization_id` | string | Yes | Organization ID |
| `region` | string | No | AWS region (default: `us-east-1`) |
| `db_password` | string | No | Database password (auto-generated if not provided) |

**Available Regions:**
- `us-east-1` (N. Virginia)
- `us-west-1` (N. California)
- `eu-west-1` (Ireland)
- `eu-west-2` (London)
- `eu-central-1` (Frankfurt)
- `ap-southeast-1` (Singapore)
- `ap-northeast-1` (Tokyo)
- `ap-south-1` (Mumbai)
- `sa-east-1` (Sao Paulo)

**Returns:** Created project object

**Example:**
```
create_project(
  name="my-new-app",
  organization_id="org_abc123xyz",
  region="us-east-1"
)
```

**Response:**
```json
{
  "id": "njfjihorcqllcwularcq",
  "name": "my-new-app",
  "organization_id": "org_abc123xyz",
  "region": "us-east-1",
  "status": "COMING_UP"
}
```

**Note:** Project initialization takes 30-60 seconds. Status changes to `ACTIVE_HEALTHY` when ready.

---

### delete_project

Delete a Supabase project permanently.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |
| `confirm` | boolean | Yes | Must be `true` to confirm deletion |

**Returns:** Success status

**Example:**
```
delete_project(
  project_ref="njfjihorcqllcwularcq",
  confirm=true
)
```

**Response:**
```json
{
  "status": "success"
}
```

**Warning:** This action is irreversible. All data, configurations, and resources will be permanently deleted.

---

### get_api_keys

Get API keys for a project.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |

**Returns:** Array of API key objects

**Example:**
```
get_api_keys(project_ref="forjadxkmzabhidnkwyh")
```

**Response:**
```json
[
  {
    "name": "anon",
    "api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  {
    "name": "service_role",
    "api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
]
```

**Key Types:**
- `anon` - Public key for client-side use. Respects Row Level Security.
- `service_role` - Secret key for server-side use. Bypasses RLS.

---

### get_project_url

Get the API URL for a project.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |

**Returns:** Project URL object

**Example:**
```
get_project_url(project_ref="forjadxkmzabhidnkwyh")
```

**Response:**
```json
{
  "url": "https://forjadxkmzabhidnkwyh.supabase.co"
}
```

---

## Database

### list_tables

List all tables in the project database.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |

**Returns:** Array of table objects

**Example:**
```
list_tables(project_ref="forjadxkmzabhidnkwyh")
```

**Response:**
```json
[
  {
    "schema": "public",
    "name": "users",
    "owner": "postgres"
  },
  {
    "schema": "public",
    "name": "posts",
    "owner": "postgres"
  }
]
```

**Note:** Excludes system tables from `pg_catalog`, `information_schema`, and `supabase_migrations`.

---

### execute_sql

Execute a SQL query on the project database.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |
| `query` | string | Yes | SQL query to execute |

**Returns:** Query results

**Example - SELECT:**
```
execute_sql(
  project_ref="forjadxkmzabhidnkwyh",
  query="SELECT id, email FROM users LIMIT 5"
)
```

**Response:**
```json
[
  {"id": "uuid-1", "email": "user1@example.com"},
  {"id": "uuid-2", "email": "user2@example.com"}
]
```

**Example - CREATE TABLE:**
```
execute_sql(
  project_ref="forjadxkmzabhidnkwyh",
  query="CREATE TABLE posts (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), title TEXT NOT NULL)"
)
```

**Example - INSERT:**
```
execute_sql(
  project_ref="forjadxkmzabhidnkwyh",
  query="INSERT INTO posts (title) VALUES ('Hello World') RETURNING *"
)
```

**Supported Operations:**
- SELECT, INSERT, UPDATE, DELETE
- CREATE/ALTER/DROP TABLE
- CREATE/DROP INDEX
- GRANT/REVOKE permissions
- RLS policies
- Functions and triggers

---

### list_extensions

List installed PostgreSQL extensions.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |

**Returns:** Array of extension objects

**Example:**
```
list_extensions(project_ref="forjadxkmzabhidnkwyh")
```

**Response:**
```json
[
  {"name": "plpgsql", "version": "1.0"},
  {"name": "uuid-ossp", "version": "1.1"},
  {"name": "pgcrypto", "version": "1.3"},
  {"name": "vector", "version": "0.5.1"}
]
```

---

### list_migrations

List applied database migrations.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |

**Returns:** Array of migration records

**Example:**
```
list_migrations(project_ref="forjadxkmzabhidnkwyh")
```

**Response:**
```json
[
  {
    "version": "20240115103000",
    "name": "create_users_table",
    "executed_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### generate_types

Generate TypeScript types from database schema.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |

**Returns:** TypeScript type definitions

**Example:**
```
generate_types(project_ref="forjadxkmzabhidnkwyh")
```

**Response:**
```typescript
export type Json = string | number | boolean | null | { [key: string]: Json } | Json[]

export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          created_at: string
        }
        Insert: {
          id?: string
          email: string
          created_at?: string
        }
        Update: {
          id?: string
          email?: string
          created_at?: string
        }
      }
    }
  }
}
```

---

## Branches

### list_branches

List database branches for a project.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |

**Returns:** Array of branch objects

**Example:**
```
list_branches(project_ref="forjadxkmzabhidnkwyh")
```

**Response:**
```json
[
  {
    "id": "branch_abc123",
    "name": "feature-auth",
    "git_branch": "feature/auth-system",
    "status": "ACTIVE",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### create_branch

Create a new database branch.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |
| `branch_name` | string | Yes | Name for the branch |
| `git_branch` | string | No | Associated git branch name |

**Returns:** Created branch object

**Example:**
```
create_branch(
  project_ref="forjadxkmzabhidnkwyh",
  branch_name="feature-auth",
  git_branch="feature/auth-system"
)
```

**Response:**
```json
{
  "id": "branch_abc123",
  "name": "feature-auth",
  "git_branch": "feature/auth-system",
  "status": "CREATING"
}
```

---

### delete_branch

Delete a database branch.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `branch_id` | string | Yes | Branch ID (not project_ref) |

**Returns:** Success status

**Example:**
```
delete_branch(branch_id="branch_abc123")
```

---

### reset_branch

Reset a database branch to match production.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `branch_id` | string | Yes | Branch ID to reset |

**Returns:** Success status

**Example:**
```
reset_branch(branch_id="branch_abc123")
```

---

## Edge Functions

### list_functions

List edge functions for a project.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |

**Returns:** Array of function objects

**Example:**
```
list_functions(project_ref="forjadxkmzabhidnkwyh")
```

**Response:**
```json
[
  {
    "id": "func_123",
    "slug": "send-email",
    "name": "send-email",
    "status": "ACTIVE",
    "verify_jwt": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### get_function

Get details for a specific edge function.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |
| `function_slug` | string | Yes | Function slug/name |

**Returns:** Function object with configuration

**Example:**
```
get_function(
  project_ref="forjadxkmzabhidnkwyh",
  function_slug="send-email"
)
```

---

### deploy_function

Deploy an edge function.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |
| `function_slug` | string | Yes | Function slug/name |
| `code` | string | Yes | Function code (TypeScript/JavaScript) |
| `verify_jwt` | boolean | No | Require JWT verification (default: `true`) |

**Returns:** Deployed function object

**Example:**
```
deploy_function(
  project_ref="forjadxkmzabhidnkwyh",
  function_slug="hello-world",
  code="""
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  return new Response(JSON.stringify({ message: "Hello!" }), {
    headers: { "Content-Type": "application/json" }
  })
})
""",
  verify_jwt=false
)
```

---

## Secrets

### list_secrets

List secrets for a project (names only, values are not returned).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |

**Returns:** Array of secret name objects

**Example:**
```
list_secrets(project_ref="forjadxkmzabhidnkwyh")
```

**Response:**
```json
[
  {"name": "STRIPE_SECRET_KEY"},
  {"name": "SENDGRID_API_KEY"}
]
```

---

### set_secrets

Create or update project secrets.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |
| `secrets` | array | Yes | Array of `{name, value}` objects |

**Returns:** Success status

**Example:**
```
set_secrets(
  project_ref="forjadxkmzabhidnkwyh",
  secrets=[
    {"name": "STRIPE_SECRET_KEY", "value": "sk_live_..."},
    {"name": "SENDGRID_API_KEY", "value": "SG...."}
  ]
)
```

---

### delete_secrets

Delete project secrets.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |
| `secret_names` | array | Yes | Array of secret names to delete |

**Returns:** Success status

**Example:**
```
delete_secrets(
  project_ref="forjadxkmzabhidnkwyh",
  secret_names=["OLD_API_KEY", "DEPRECATED_SECRET"]
)
```

---

## Logs

### get_logs

Get project logs for a specific service.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_ref` | string | Yes | Project reference ID |
| `service` | string | No | Service name (default: `api`) |
| `limit` | integer | No | Number of entries (default: `100`) |

**Available Services:**

| Service | Description |
|---------|-------------|
| `api` | PostgREST API requests |
| `auth` | Authentication events (login, signup, token refresh) |
| `db` | Database queries and errors |
| `realtime` | Real-time subscription events |
| `storage` | File storage operations |
| `functions` | Edge function invocations |

**Returns:** Array of log entries

**Example:**
```
get_logs(
  project_ref="forjadxkmzabhidnkwyh",
  service="auth",
  limit=50
)
```

**Response:**
```json
[
  {
    "timestamp": "2024-01-15T10:30:00Z",
    "event_message": "User signed in",
    "metadata": {
      "user_id": "uuid-123",
      "method": "password"
    }
  }
]
```

---

## Error Codes

| HTTP Status | Error | Description |
|-------------|-------|-------------|
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Invalid or expired token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Supabase server error |

**Error Response Format:**
```
API Error (401): {"message": "Invalid access token"}
```
