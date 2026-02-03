"""Project operations."""

from __future__ import annotations

import secrets as stdlib_secrets
from typing import Any

from ..client import SupabaseManagementClient


def list_projects(client: SupabaseManagementClient) -> list:
    """List all Supabase projects across all organizations.

    Returns:
        List of project dicts.
    """
    return client.request("GET", "/projects")


def get_project(client: SupabaseManagementClient, project_ref: str) -> dict:
    """Get details for a specific Supabase project.

    Returns:
        Project details dict.
    """
    return client.request("GET", f"/projects/{project_ref}")


def create_project(
    client: SupabaseManagementClient,
    name: str,
    organization_id: str,
    region: str = "us-east-1",
    db_password: str | None = None,
) -> dict:
    """Create a new Supabase project.

    Returns:
        Created project dict.
    """
    data = {
        "name": name,
        "organization_id": organization_id,
        "region": region,
        "db_pass": db_password or stdlib_secrets.token_urlsafe(24),
    }
    return client.request("POST", "/projects", data=data)


def delete_project(client: SupabaseManagementClient, project_ref: str) -> dict:
    """Delete a Supabase project.

    Returns:
        Status dict.
    """
    return client.request("DELETE", f"/projects/{project_ref}")


def get_api_keys(client: SupabaseManagementClient, project_ref: str) -> list:
    """Get API keys (anon, service_role) for a project.

    Returns:
        List of API key dicts.
    """
    return client.request("GET", f"/projects/{project_ref}/api-keys")


def get_project_url(client: SupabaseManagementClient, project_ref: str) -> dict:
    """Get the API URL for a project.

    Returns:
        Dict with url key.
    """
    return {"url": f"https://{project_ref}.supabase.co"}
