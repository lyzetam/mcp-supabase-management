"""Database operations."""

from __future__ import annotations

from typing import Any

from ..client import SupabaseManagementClient


def execute_sql(client: SupabaseManagementClient, project_ref: str, query: str) -> Any:
    """Execute a SQL query via the Management API.

    Returns:
        Query result (dict or list).
    """
    return client.request(
        "POST",
        f"/projects/{project_ref}/database/query",
        data={"query": query},
    )


def list_tables(client: SupabaseManagementClient, project_ref: str) -> Any:
    """List all tables in a project's database.

    Returns:
        Query result with schema, name, owner.
    """
    query = """
    SELECT
        schemaname as schema,
        tablename as name,
        tableowner as owner
    FROM pg_tables
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'supabase_migrations')
    ORDER BY schemaname, tablename
    """
    return execute_sql(client, project_ref, query)


def list_extensions(client: SupabaseManagementClient, project_ref: str) -> Any:
    """List installed PostgreSQL extensions.

    Returns:
        Query result with name, version.
    """
    query = """
    SELECT extname as name, extversion as version
    FROM pg_extension
    ORDER BY extname
    """
    return execute_sql(client, project_ref, query)


def list_migrations(client: SupabaseManagementClient, project_ref: str) -> Any:
    """List applied database migrations.

    Returns:
        Query result or error dict if no migrations table.
    """
    query = """
    SELECT version, name, executed_at
    FROM supabase_migrations.schema_migrations
    ORDER BY executed_at DESC
    """
    try:
        return execute_sql(client, project_ref, query)
    except Exception:
        return {"error": "No migrations table found"}


def generate_types(client: SupabaseManagementClient, project_ref: str) -> Any:
    """Generate TypeScript types from database schema.

    Returns:
        TypeScript type definitions.
    """
    return client.request("GET", f"/projects/{project_ref}/types/typescript")
