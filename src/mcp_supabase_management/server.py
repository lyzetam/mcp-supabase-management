"""Supabase MCP Server — backward-compatible thin wrappers delegating to async client.

Keeps original tool names (list_organizations, execute_sql, etc.) for MCP compatibility.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .client import SupabaseManagementClient

app = Server("supabase")

# Lazy-init client to defer env-var check until first tool call.
_client: SupabaseManagementClient | None = None


def _get_client() -> SupabaseManagementClient:
    global _client
    if _client is None:
        _client = SupabaseManagementClient()
    return _client


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        # Organizations
        Tool(
            name="list_organizations",
            description="List all Supabase organizations",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        # Projects
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
        # Database
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
        # Branches
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
        # Edge Functions
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
        # Secrets
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
        # Logs
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
    """Handle tool calls — delegates to async client methods."""
    try:
        client = _get_client()
        result: Any = None

        # Organizations
        if name == "list_organizations":
            result = await client.arequest("GET", "/organizations")

        # Projects
        elif name == "list_projects":
            result = await client.arequest("GET", "/projects")
        elif name == "get_project":
            result = await client.arequest("GET", f"/projects/{arguments['project_ref']}")
        elif name == "create_project":
            import secrets as stdlib_secrets
            data = {
                "name": arguments["name"],
                "organization_id": arguments["organization_id"],
                "region": arguments.get("region", "us-east-1"),
                "db_pass": arguments.get("db_password") or stdlib_secrets.token_urlsafe(24),
            }
            result = await client.arequest("POST", "/projects", data=data)
        elif name == "delete_project":
            if not arguments.get("confirm"):
                return [TextContent(type="text", text="ERROR: Must set confirm=true to delete a project")]
            result = await client.arequest("DELETE", f"/projects/{arguments['project_ref']}")
        elif name == "get_api_keys":
            result = await client.arequest("GET", f"/projects/{arguments['project_ref']}/api-keys")
        elif name == "get_project_url":
            result = {"url": f"https://{arguments['project_ref']}.supabase.co"}

        # Database
        elif name == "list_tables":
            query = """
            SELECT schemaname as schema, tablename as name, tableowner as owner
            FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'supabase_migrations')
            ORDER BY schemaname, tablename
            """
            result = await client.arequest("POST", f"/projects/{arguments['project_ref']}/database/query", data={"query": query})
        elif name == "execute_sql":
            result = await client.arequest("POST", f"/projects/{arguments['project_ref']}/database/query", data={"query": arguments["query"]})
        elif name == "list_extensions":
            query = "SELECT extname as name, extversion as version FROM pg_extension ORDER BY extname"
            result = await client.arequest("POST", f"/projects/{arguments['project_ref']}/database/query", data={"query": query})
        elif name == "list_migrations":
            try:
                query = "SELECT version, name, executed_at FROM supabase_migrations.schema_migrations ORDER BY executed_at DESC"
                result = await client.arequest("POST", f"/projects/{arguments['project_ref']}/database/query", data={"query": query})
            except Exception:
                result = {"error": "No migrations table found"}
        elif name == "generate_types":
            result = await client.arequest("GET", f"/projects/{arguments['project_ref']}/types/typescript")

        # Branches
        elif name == "list_branches":
            result = await client.arequest("GET", f"/projects/{arguments['project_ref']}/branches")
        elif name == "create_branch":
            data = {"branch_name": arguments["branch_name"]}
            if arguments.get("git_branch"):
                data["git_branch"] = arguments["git_branch"]
            result = await client.arequest("POST", f"/projects/{arguments['project_ref']}/branches", data=data)
        elif name == "delete_branch":
            result = await client.arequest("DELETE", f"/branches/{arguments['branch_id']}")
        elif name == "reset_branch":
            result = await client.arequest("POST", f"/branches/{arguments['branch_id']}/reset")

        # Functions
        elif name == "list_functions":
            result = await client.arequest("GET", f"/projects/{arguments['project_ref']}/functions")
        elif name == "get_function":
            result = await client.arequest("GET", f"/projects/{arguments['project_ref']}/functions/{arguments['function_slug']}")
        elif name == "deploy_function":
            result = await client.arequest(
                "POST",
                f"/projects/{arguments['project_ref']}/functions/{arguments['function_slug']}",
                data={"body": arguments["code"], "verify_jwt": arguments.get("verify_jwt", True)},
            )

        # Secrets
        elif name == "list_secrets":
            result = await client.arequest("GET", f"/projects/{arguments['project_ref']}/secrets")
        elif name == "set_secrets":
            result = await client.arequest("POST", f"/projects/{arguments['project_ref']}/secrets", data=arguments["secrets"])
        elif name == "delete_secrets":
            result = await client.arequest("DELETE", f"/projects/{arguments['project_ref']}/secrets", data=arguments["secret_names"])

        # Logs
        elif name == "get_logs":
            result = await client.arequest(
                "GET",
                f"/projects/{arguments['project_ref']}/analytics/endpoints/logs.all",
                params={"product": arguments.get("service", "api"), "limit": arguments.get("limit", 100)},
            )

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    except httpx.HTTPStatusError as e:
        error_body = e.response.text
        return [TextContent(type="text", text=f"API Error ({e.response.status_code}): {error_body}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def run_server():
    """Run the MCP server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main():
    """Run the MCP server."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
