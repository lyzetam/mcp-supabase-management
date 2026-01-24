# Runbook

Operational procedures for managing Supabase projects via the Management MCP.

---

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Create New Project](#create-new-project)
3. [Database Migration](#database-migration)
4. [Deploy Edge Function](#deploy-edge-function)
5. [Rotate API Keys](#rotate-api-keys)
6. [Debug Production Issues](#debug-production-issues)
7. [Emergency: Delete Project](#emergency-delete-project)
8. [Token Rotation](#token-rotation)

---

## Initial Setup

### Purpose

Configure the Supabase Management MCP for first-time use.

### Prerequisites

- Claude Code installed
- Supabase account with at least one organization

### Steps

1. **Generate Management API token**
   ```
   Open: https://supabase.com/dashboard/account/tokens
   Click: Generate new token
   Name: "Claude Code MCP"
   Copy the token (starts with sbp_)
   ```

2. **Store token in AWS Secrets Manager** (recommended)
   ```
   aws secretsmanager create-secret \
     --name supabase/management-api \
     --secret-string '{"token":"sbp_your_token_here"}'
   ```

3. **Add MCP to Claude Code config**

   Edit `~/.claude.json`:
   ```json
   {
     "mcpServers": {
       "supabase-management": {
         "type": "stdio",
         "command": "uv",
         "args": ["--directory", "~/dev/mcp-supabase-management", "run", "mcp-supabase-management"],
         "env": {
           "SUPABASE_ACCESS_TOKEN": "sbp_your_token_here"
         }
       }
     }
   }
   ```

4. **Verify installation**
   ```
   Restart Claude Code
   Run: list_organizations()
   Expected: List of your organizations
   ```

### Rollback

Remove the MCP entry from `~/.claude.json` if issues occur.

### Contacts

- Supabase Support: https://supabase.com/support
- Token management: https://supabase.com/dashboard/account/tokens

---

## Create New Project

### Purpose

Provision a new Supabase project for an application.

### Prerequisites

- Valid Management API token
- Organization ID (run `list_organizations()` to find)

### Steps

1. **Get organization ID**
   ```
   list_organizations()
   ```
   Copy the `id` field.

2. **Create the project**
   ```
   create_project(
     name="my-app-name",
     organization_id="org_abc123",
     region="us-east-1"
   )
   ```
   Note the returned `id` (project reference).

3. **Wait for initialization**
   ```
   # Check status (repeat until ACTIVE_HEALTHY)
   get_project(project_ref="returned_project_id")
   ```
   Typically takes 30-60 seconds.

4. **Retrieve API keys**
   ```
   get_api_keys(project_ref="returned_project_id")
   ```
   Store keys securely.

5. **Store credentials in AWS Secrets Manager**
   ```
   aws secretsmanager create-secret \
     --name my-app/supabase \
     --secret-string '{
       "url": "https://project_ref.supabase.co",
       "anon_key": "eyJ...",
       "service_key": "eyJ..."
     }'
   ```

6. **Configure project HTTP MCP** (optional)

   Add to `~/.claude.json`:
   ```json
   "supabase-my-app": {
     "type": "http",
     "url": "https://mcp.supabase.com/mcp?project_ref=returned_project_id"
   }
   ```

### Verification

```
list_tables(project_ref="returned_project_id")
```
Should return empty array for new project.

### Rollback

```
delete_project(project_ref="returned_project_id", confirm=true)
```

---

## Database Migration

### Purpose

Apply schema changes to a Supabase database.

### Prerequisites

- Project reference ID
- SQL migration script

### Steps

1. **Create a branch for testing** (optional but recommended)
   ```
   create_branch(
     project_ref="abcdefghijklmnopqrst",
     branch_name="migration-test"
   )
   ```
   Note the returned `branch_id`.

2. **Apply migration to branch**
   ```
   execute_sql(
     project_ref="branch_project_ref",
     query="""
     CREATE TABLE posts (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       title TEXT NOT NULL,
       content TEXT,
       created_at TIMESTAMPTZ DEFAULT NOW()
     );

     ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

     CREATE POLICY "Users can read all posts"
       ON posts FOR SELECT
       USING (true);
     """
   )
   ```

3. **Verify migration**
   ```
   list_tables(project_ref="branch_project_ref")
   execute_sql(project_ref="branch_project_ref", query="SELECT * FROM posts LIMIT 1")
   ```

4. **Apply to production** (if branch test successful)
   ```
   execute_sql(
     project_ref="abcdefghijklmnopqrst",
     query="<same migration SQL>"
   )
   ```

5. **Clean up branch**
   ```
   delete_branch(branch_id="branch_abc123")
   ```

### Verification

```
list_migrations(project_ref="abcdefghijklmnopqrst")
list_tables(project_ref="abcdefghijklmnopqrst")
```

### Rollback

Prepare a rollback script before running migrations:
```
execute_sql(
  project_ref="abcdefghijklmnopqrst",
  query="DROP TABLE IF EXISTS posts CASCADE;"
)
```

---

## Deploy Edge Function

### Purpose

Deploy a new or updated edge function.

### Prerequisites

- Project reference ID
- Function code (TypeScript/Deno)

### Steps

1. **List existing functions**
   ```
   list_functions(project_ref="abcdefghijklmnopqrst")
   ```

2. **Deploy the function**
   ```
   deploy_function(
     project_ref="abcdefghijklmnopqrst",
     function_slug="my-function",
     code="""
   import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
   import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

   serve(async (req) => {
     const supabase = createClient(
       Deno.env.get('SUPABASE_URL')!,
       Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
     )

     const { data, error } = await supabase.from('users').select('*').limit(10)

     return new Response(JSON.stringify({ data, error }), {
       headers: { "Content-Type": "application/json" }
     })
   })
   """,
     verify_jwt=true
   )
   ```

3. **Set required secrets**
   ```
   set_secrets(
     project_ref="abcdefghijklmnopqrst",
     secrets=[
       {"name": "MY_API_KEY", "value": "secret_value"}
     ]
   )
   ```

4. **Verify deployment**
   ```
   get_function(
     project_ref="abcdefghijklmnopqrst",
     function_slug="my-function"
   )
   ```

5. **Test the function**
   ```bash
   curl -X POST \
     'https://abcdefghijklmnopqrst.supabase.co/functions/v1/my-function' \
     -H 'Authorization: Bearer <anon_key>' \
     -H 'Content-Type: application/json' \
     -d '{}'
   ```

### Verification

```
get_logs(
  project_ref="abcdefghijklmnopqrst",
  service="functions",
  limit=10
)
```

### Rollback

Redeploy previous version of the function code.

---

## Rotate API Keys

### Purpose

Rotate API keys after suspected compromise or as routine security.

### Prerequisites

- Project reference ID
- Access to update application configurations

### Steps

1. **Note current keys** (for comparison)
   ```
   get_api_keys(project_ref="abcdefghijklmnopqrst")
   ```

2. **Rotate keys via Supabase Dashboard**
   ```
   Open: https://supabase.com/dashboard/project/abcdefghijklmnopqrst/settings/api
   Click: Rotate on the key you want to rotate
   Confirm the rotation
   ```

   Note: The Management API does not support key rotation directly. Use the dashboard.

3. **Get new keys**
   ```
   get_api_keys(project_ref="abcdefghijklmnopqrst")
   ```

4. **Update AWS Secrets Manager**
   ```bash
   aws secretsmanager update-secret \
     --secret-id my-app/supabase \
     --secret-string '{
       "url": "https://abcdefghijklmnopqrst.supabase.co",
       "anon_key": "new_anon_key",
       "service_key": "new_service_key"
     }'
   ```

5. **Restart applications** to pick up new keys

### Verification

Test API access with new keys:
```bash
curl 'https://abcdefghijklmnopqrst.supabase.co/rest/v1/' \
  -H 'apikey: new_anon_key'
```

---

## Debug Production Issues

### Purpose

Diagnose and resolve issues in a production Supabase project.

### Prerequisites

- Project reference ID
- Symptoms or error messages

### Steps

1. **Check project status**
   ```
   get_project(project_ref="abcdefghijklmnopqrst")
   ```
   Verify status is `ACTIVE_HEALTHY`.

2. **Check API logs**
   ```
   get_logs(
     project_ref="abcdefghijklmnopqrst",
     service="api",
     limit=100
   )
   ```
   Look for 4xx/5xx errors.

3. **Check auth logs** (for authentication issues)
   ```
   get_logs(
     project_ref="abcdefghijklmnopqrst",
     service="auth",
     limit=100
   )
   ```

4. **Check database logs** (for query issues)
   ```
   get_logs(
     project_ref="abcdefghijklmnopqrst",
     service="db",
     limit=100
   )
   ```

5. **Run diagnostic queries**
   ```
   # Check for long-running queries
   execute_sql(
     project_ref="abcdefghijklmnopqrst",
     query="""
     SELECT pid, now() - pg_stat_activity.query_start AS duration, query
     FROM pg_stat_activity
     WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
     """
   )

   # Check table sizes
   execute_sql(
     project_ref="abcdefghijklmnopqrst",
     query="""
     SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
     FROM pg_catalog.pg_statio_user_tables
     ORDER BY pg_total_relation_size(relid) DESC
     LIMIT 10
     """
   )

   # Check connection count
   execute_sql(
     project_ref="abcdefghijklmnopqrst",
     query="SELECT count(*) FROM pg_stat_activity"
   )
   ```

6. **Check edge function logs** (if applicable)
   ```
   get_logs(
     project_ref="abcdefghijklmnopqrst",
     service="functions",
     limit=100
   )
   ```

### Common Issues

| Symptom | Check | Solution |
|---------|-------|----------|
| 401 errors | Auth logs | Verify JWT, check token expiry |
| 500 errors | API + DB logs | Check query errors, RLS policies |
| Slow responses | DB logs | Optimize queries, add indexes |
| Connection errors | Connection count | Increase pool size, check limits |

---

## Emergency: Delete Project

### Purpose

Permanently delete a project in an emergency (compromise, cost control).

### Prerequisites

- Project reference ID
- Confirmation of data backup status
- Authorization to delete

### Steps

1. **Export critical data** (if possible)
   ```
   execute_sql(
     project_ref="abcdefghijklmnopqrst",
     query="COPY users TO STDOUT WITH CSV HEADER"
   )
   ```

2. **Document project configuration**
   ```
   get_project(project_ref="abcdefghijklmnopqrst")
   list_secrets(project_ref="abcdefghijklmnopqrst")
   list_functions(project_ref="abcdefghijklmnopqrst")
   ```

3. **Delete the project**
   ```
   delete_project(
     project_ref="abcdefghijklmnopqrst",
     confirm=true
   )
   ```

4. **Update DNS/configurations** to remove references

5. **Notify stakeholders**

### Rollback

**NOT POSSIBLE.** Project deletion is permanent and irreversible.

### Post-Incident

- Document reason for deletion
- Update runbooks if process issues discovered
- Consider backup improvements

---

## Token Rotation

### Purpose

Rotate the Supabase Management API token for security.

### Prerequisites

- Access to Supabase dashboard
- Access to update Claude Code configuration

### Steps

1. **Generate new token**
   ```
   Open: https://supabase.com/dashboard/account/tokens
   Click: Generate new token
   Name: "Claude Code MCP (rotated YYYY-MM-DD)"
   Copy the new token
   ```

2. **Update AWS Secrets Manager**
   ```bash
   aws secretsmanager update-secret \
     --secret-id supabase/management-api \
     --secret-string '{"token":"sbp_new_token_here"}'
   ```

3. **Update Claude Code config**

   Edit `~/.claude.json`:
   ```json
   "env": {
     "SUPABASE_ACCESS_TOKEN": "sbp_new_token_here"
   }
   ```

4. **Restart Claude Code**

5. **Verify access**
   ```
   list_organizations()
   list_projects()
   ```

6. **Revoke old token**
   ```
   Open: https://supabase.com/dashboard/account/tokens
   Find the old token
   Click: Revoke
   ```

### Verification

All MCP operations should work with new token.

### Rollback

If new token doesn't work:
1. Re-enable old token (if not yet revoked)
2. Update config back to old token
3. Investigate new token permissions

---

## Contacts

| Role | Contact |
|------|---------|
| Supabase Support | https://supabase.com/support |
| API Status | https://status.supabase.com |
| Documentation | https://supabase.com/docs |
