#!/usr/bin/env python3
"""
Supabase MCP Server (Unified)

Combines Management API + Project-level operations:
- Organization & project management
- Database operations (tables, SQL, migrations)
- Edge functions
- Secrets & configuration
- Logs & monitoring
"""

import asyncio
import json
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Configuration
SUPABASE_ACCESS_TOKEN = os.environ.get("SUPABASE_ACCESS_TOKEN", "")
MANAGEMENT_API = "https://api.supabase.com/v1"


class SupabaseClient:
    """Unified client for Supabase Management + Project APIs."""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.management = httpx.AsyncClient(
            base_url=MANAGEMENT_API,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    def _project_client(self, project_ref: str, service_key: str) -> httpx.AsyncClient:
        """Create a client for project-level API calls."""
        return httpx.AsyncClient(
            base_url=f"https://{project_ref}.supabase.co",
            headers={
                "apikey": service_key,
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        params: dict | None = None,
    ) -> dict | list:
        """Make a Management API request."""
        response = await self.management.request(
            method=method,
            url=endpoint,
            json=data,
            params=params,
        )
        response.raise_for_status()
        if response.status_code == 204:
            return {"status": "success"}
        return response.json()

    # ==================== ORGANIZATIONS ====================

    async def list_organizations(self) -> list:
        """List all organizations."""
        return await self.request("GET", "/organizations")

    # ==================== PROJECTS ====================

    async def list_projects(self) -> list:
        """List all projects."""
        return await self.request("GET", "/projects")

    async def get_project(self, project_ref: str) -> dict:
        """Get project details."""
        return await self.request("GET", f"/projects/{project_ref}")

    async def create_project(
        self,
        name: str,
        organization_id: str,
        region: str = "us-east-1",
        db_password: str | None = None,
    ) -> dict:
        """Create a new project."""
        import secrets
        data = {
            "name": name,
            "organization_id": organization_id,
            "region": region,
            "db_pass": db_password or secrets.token_urlsafe(24),
        }
        return await self.request("POST", "/projects", data=data)

    async def delete_project(self, project_ref: str) -> dict:
        """Delete a project."""
        return await self.request("DELETE", f"/projects/{project_ref}")

    async def get_api_keys(self, project_ref: str) -> list:
        """Get API keys for a project."""
        return await self.request("GET", f"/projects/{project_ref}/api-keys")

    async def get_project_url(self, project_ref: str) -> dict:
        """Get project URL."""
        return {"url": f"https://{project_ref}.supabase.co"}

    # ==================== DATABASE ====================

    async def list_tables(self, project_ref: str) -> list:
        """List all tables in the project database."""
        query = """
        SELECT
            schemaname as schema,
            tablename as name,
            tableowner as owner
        FROM pg_tables
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'supabase_migrations')
        ORDER BY schemaname, tablename
        """
        result = await self.execute_sql(project_ref, query)
        return result

    async def execute_sql(self, project_ref: str, query: str) -> dict:
        """Execute SQL query via Management API."""
        return await self.request(
            "POST",
            f"/projects/{project_ref}/database/query",
            data={"query": query},
        )

    async def list_extensions(self, project_ref: str) -> list:
        """List installed PostgreSQL extensions."""
        query = """
        SELECT extname as name, extversion as version
        FROM pg_extension
        ORDER BY extname
        """
        return await self.execute_sql(project_ref, query)

    async def list_migrations(self, project_ref: str) -> list:
        """List applied migrations."""
        query = """
        SELECT version, name, executed_at
        FROM supabase_migrations.schema_migrations
        ORDER BY executed_at DESC
        """
        try:
            return await self.execute_sql(project_ref, query)
        except Exception:
            return {"error": "No migrations table found"}

    # ==================== BRANCHES ====================

    async def list_branches(self, project_ref: str) -> list:
        """List database branches."""
        return await self.request("GET", f"/projects/{project_ref}/branches")

    async def create_branch(
        self,
        project_ref: str,
        branch_name: str,
        git_branch: str | None = None,
    ) -> dict:
        """Create a database branch."""
        data = {"branch_name": branch_name}
        if git_branch:
            data["git_branch"] = git_branch
        return await self.request("POST", f"/projects/{project_ref}/branches", data=data)

    async def delete_branch(self, branch_id: str) -> dict:
        """Delete a database branch."""
        return await self.request("DELETE", f"/branches/{branch_id}")

    async def reset_branch(self, branch_id: str) -> dict:
        """Reset a database branch to match production."""
        return await self.request("POST", f"/branches/{branch_id}/reset")

    # ==================== EDGE FUNCTIONS ====================

    async def list_functions(self, project_ref: str) -> list:
        """List edge functions."""
        return await self.request("GET", f"/projects/{project_ref}/functions")

    async def get_function(self, project_ref: str, function_slug: str) -> dict:
        """Get edge function details."""
        return await self.request("GET", f"/projects/{project_ref}/functions/{function_slug}")

    async def deploy_function(
        self,
        project_ref: str,
        function_slug: str,
        code: str,
        verify_jwt: bool = True,
    ) -> dict:
        """Deploy an edge function."""
        return await self.request(
            "POST",
            f"/projects/{project_ref}/functions/{function_slug}",
            data={
                "body": code,
                "verify_jwt": verify_jwt,
            },
        )

    # ==================== SECRETS ====================

    async def list_secrets(self, project_ref: str) -> list:
        """List project secrets (names only)."""
        return await self.request("GET", f"/projects/{project_ref}/secrets")

    async def set_secrets(self, project_ref: str, secrets: list[dict]) -> dict:
        """Create or update project secrets."""
        return await self.request("POST", f"/projects/{project_ref}/secrets", data=secrets)

    async def delete_secrets(self, project_ref: str, secret_names: list[str]) -> dict:
        """Delete project secrets."""
        return await self.request(
            "DELETE",
            f"/projects/{project_ref}/secrets",
            data=secret_names,
        )

    # ==================== LOGS ====================

    async def get_logs(
        self,
        project_ref: str,
        service: str = "api",
        limit: int = 100,
    ) -> list:
        """Get project logs."""
        # Services: api, auth, db, realtime, storage, functions
        return await self.request(
            "GET",
            f"/projects/{project_ref}/analytics/endpoints/logs.all",
            params={"product": service, "limit": limit},
        )

    # ==================== TYPESCRIPT TYPES ====================

    async def generate_types(self, project_ref: str) -> dict:
        """Generate TypeScript types from database schema."""
        return await self.request(
            "GET",
            f"/projects/{project_ref}/types/typescript",
        )


# ==================== MCP SERVER ====================

app = Server("supabase")


def get_client() -> SupabaseClient:
    """Get Supabase client instance."""
    if not SUPABASE_ACCESS_TOKEN:
        raise ValueError("SUPABASE_ACCESS_TOKEN environment variable not set")
    return SupabaseClient(SUPABASE_ACCESS_TOKEN)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        # ==================== ORGANIZATIONS ====================
        Tool(
            name="list_organizations",
            description="List all Supabase organizations",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),

        # ==================== PROJECTS ====================
        Tool(
            name="list_projects",
            description="List all Supabase projects across all organizations",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_project",
            description="Get details for a specific Supabase project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                },
                "required": ["project_ref"],
            },
        ),
        Tool(
            name="create_project",
            description="Create a new Supabase project",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Project name"},
                    "organization_id": {"type": "string", "description": "Organization ID"},
                    "region": {"type": "string", "description": "Region (default: us-east-1)"},
                    "db_password": {"type": "string", "description": "Database password (auto-generated if not provided)"},
                },
                "required": ["name", "organization_id"],
            },
        ),
        Tool(
            name="delete_project",
            description="Delete a Supabase project (DESTRUCTIVE)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                    "confirm": {"type": "boolean", "description": "Must be true to confirm deletion"},
                },
                "required": ["project_ref", "confirm"],
            },
        ),
        Tool(
            name="get_api_keys",
            description="Get API keys (anon, service_role) for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                },
                "required": ["project_ref"],
            },
        ),
        Tool(
            name="get_project_url",
            description="Get the API URL for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                },
                "required": ["project_ref"],
            },
        ),

        # ==================== DATABASE ====================
        Tool(
            name="list_tables",
            description="List all tables in a project's database",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                },
                "required": ["project_ref"],
            },
        ),
        Tool(
            name="execute_sql",
            description="Execute a SQL query on a project's database",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                    "query": {"type": "string", "description": "SQL query to execute"},
                },
                "required": ["project_ref", "query"],
            },
        ),
        Tool(
            name="list_extensions",
            description="List installed PostgreSQL extensions",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                },
                "required": ["project_ref"],
            },
        ),
        Tool(
            name="list_migrations",
            description="List applied database migrations",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                },
                "required": ["project_ref"],
            },
        ),
        Tool(
            name="generate_types",
            description="Generate TypeScript types from database schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                },
                "required": ["project_ref"],
            },
        ),

        # ==================== BRANCHES ====================
        Tool(
            name="list_branches",
            description="List database branches for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                },
                "required": ["project_ref"],
            },
        ),
        Tool(
            name="create_branch",
            description="Create a new database branch",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                    "branch_name": {"type": "string", "description": "Name for the new branch"},
                    "git_branch": {"type": "string", "description": "Associated git branch name"},
                },
                "required": ["project_ref", "branch_name"],
            },
        ),
        Tool(
            name="delete_branch",
            description="Delete a database branch",
            inputSchema={
                "type": "object",
                "properties": {
                    "branch_id": {"type": "string", "description": "Branch ID to delete"},
                },
                "required": ["branch_id"],
            },
        ),
        Tool(
            name="reset_branch",
            description="Reset a database branch to match production",
            inputSchema={
                "type": "object",
                "properties": {
                    "branch_id": {"type": "string", "description": "Branch ID to reset"},
                },
                "required": ["branch_id"],
            },
        ),

        # ==================== EDGE FUNCTIONS ====================
        Tool(
            name="list_functions",
            description="List edge functions for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                },
                "required": ["project_ref"],
            },
        ),
        Tool(
            name="get_function",
            description="Get details for a specific edge function",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                    "function_slug": {"type": "string", "description": "Function slug/name"},
                },
                "required": ["project_ref", "function_slug"],
            },
        ),
        Tool(
            name="deploy_function",
            description="Deploy an edge function",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                    "function_slug": {"type": "string", "description": "Function slug/name"},
                    "code": {"type": "string", "description": "Function code (TypeScript/JavaScript)"},
                    "verify_jwt": {"type": "boolean", "description": "Require JWT verification (default: true)"},
                },
                "required": ["project_ref", "function_slug", "code"],
            },
        ),

        # ==================== SECRETS ====================
        Tool(
            name="list_secrets",
            description="List secrets for a project (names only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                },
                "required": ["project_ref"],
            },
        ),
        Tool(
            name="set_secrets",
            description="Create or update project secrets",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                    "secrets": {
                        "type": "array",
                        "description": "Array of {name, value} objects",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "value": {"type": "string"},
                            },
                        },
                    },
                },
                "required": ["project_ref", "secrets"],
            },
        ),
        Tool(
            name="delete_secrets",
            description="Delete project secrets",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                    "secret_names": {
                        "type": "array",
                        "description": "Names of secrets to delete",
                        "items": {"type": "string"},
                    },
                },
                "required": ["project_ref", "secret_names"],
            },
        ),

        # ==================== LOGS ====================
        Tool(
            name="get_logs",
            description="Get project logs (api, auth, db, realtime, storage, functions)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_ref": {"type": "string", "description": "Project reference ID"},
                    "service": {"type": "string", "description": "Service: api, auth, db, realtime, storage, functions"},
                    "limit": {"type": "integer", "description": "Number of log entries (default: 100)"},
                },
                "required": ["project_ref"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        client = get_client()
        result: Any = None

        # Organizations
        if name == "list_organizations":
            result = await client.list_organizations()

        # Projects
        elif name == "list_projects":
            result = await client.list_projects()
        elif name == "get_project":
            result = await client.get_project(arguments["project_ref"])
        elif name == "create_project":
            result = await client.create_project(
                name=arguments["name"],
                organization_id=arguments["organization_id"],
                region=arguments.get("region", "us-east-1"),
                db_password=arguments.get("db_password"),
            )
        elif name == "delete_project":
            if not arguments.get("confirm"):
                return [TextContent(type="text", text="ERROR: Must set confirm=true to delete a project")]
            result = await client.delete_project(arguments["project_ref"])
        elif name == "get_api_keys":
            result = await client.get_api_keys(arguments["project_ref"])
        elif name == "get_project_url":
            result = await client.get_project_url(arguments["project_ref"])

        # Database
        elif name == "list_tables":
            result = await client.list_tables(arguments["project_ref"])
        elif name == "execute_sql":
            result = await client.execute_sql(arguments["project_ref"], arguments["query"])
        elif name == "list_extensions":
            result = await client.list_extensions(arguments["project_ref"])
        elif name == "list_migrations":
            result = await client.list_migrations(arguments["project_ref"])
        elif name == "generate_types":
            result = await client.generate_types(arguments["project_ref"])

        # Branches
        elif name == "list_branches":
            result = await client.list_branches(arguments["project_ref"])
        elif name == "create_branch":
            result = await client.create_branch(
                project_ref=arguments["project_ref"],
                branch_name=arguments["branch_name"],
                git_branch=arguments.get("git_branch"),
            )
        elif name == "delete_branch":
            result = await client.delete_branch(arguments["branch_id"])
        elif name == "reset_branch":
            result = await client.reset_branch(arguments["branch_id"])

        # Functions
        elif name == "list_functions":
            result = await client.list_functions(arguments["project_ref"])
        elif name == "get_function":
            result = await client.get_function(arguments["project_ref"], arguments["function_slug"])
        elif name == "deploy_function":
            result = await client.deploy_function(
                project_ref=arguments["project_ref"],
                function_slug=arguments["function_slug"],
                code=arguments["code"],
                verify_jwt=arguments.get("verify_jwt", True),
            )

        # Secrets
        elif name == "list_secrets":
            result = await client.list_secrets(arguments["project_ref"])
        elif name == "set_secrets":
            result = await client.set_secrets(arguments["project_ref"], arguments["secrets"])
        elif name == "delete_secrets":
            result = await client.delete_secrets(arguments["project_ref"], arguments["secret_names"])

        # Logs
        elif name == "get_logs":
            result = await client.get_logs(
                project_ref=arguments["project_ref"],
                service=arguments.get("service", "api"),
                limit=arguments.get("limit", 100),
            )

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    except httpx.HTTPStatusError as e:
        error_body = e.response.text
        return [TextContent(type="text", text=f"API Error ({e.response.status_code}): {error_body}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


def main():
    """Run the MCP server."""
    asyncio.run(stdio_server(app))


if __name__ == "__main__":
    main()
