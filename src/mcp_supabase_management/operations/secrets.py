"""Secrets operations."""

from __future__ import annotations

from ..client import SupabaseManagementClient


def list_secrets(client: SupabaseManagementClient, project_ref: str) -> list:
    """List project secrets (names only).

    Returns:
        List of secret dicts.
    """
    return client.request("GET", f"/projects/{project_ref}/secrets")


def set_secrets(
    client: SupabaseManagementClient,
    project_ref: str,
    secrets: list[dict],
) -> dict:
    """Create or update project secrets.

    Args:
        secrets: List of {name, value} dicts.

    Returns:
        Status dict.
    """
    return client.request("POST", f"/projects/{project_ref}/secrets", data=secrets)


def delete_secrets(
    client: SupabaseManagementClient,
    project_ref: str,
    secret_names: list[str],
) -> dict:
    """Delete project secrets.

    Returns:
        Status dict.
    """
    return client.request(
        "DELETE",
        f"/projects/{project_ref}/secrets",
        data=secret_names,
    )
