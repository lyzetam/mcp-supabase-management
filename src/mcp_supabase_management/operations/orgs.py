"""Organization operations."""

from __future__ import annotations

from ..client import SupabaseManagementClient


def list_organizations(client: SupabaseManagementClient) -> list:
    """List all Supabase organizations.

    Returns:
        List of organization dicts.
    """
    return client.request("GET", "/organizations")
