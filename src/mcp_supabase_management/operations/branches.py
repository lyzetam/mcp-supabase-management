"""Branch operations."""

from __future__ import annotations

from ..client import SupabaseManagementClient


def list_branches(client: SupabaseManagementClient, project_ref: str) -> list:
    """List database branches for a project.

    Returns:
        List of branch dicts.
    """
    return client.request("GET", f"/projects/{project_ref}/branches")


def create_branch(
    client: SupabaseManagementClient,
    project_ref: str,
    branch_name: str,
    git_branch: str | None = None,
) -> dict:
    """Create a new database branch.

    Returns:
        Created branch dict.
    """
    data = {"branch_name": branch_name}
    if git_branch:
        data["git_branch"] = git_branch
    return client.request("POST", f"/projects/{project_ref}/branches", data=data)


def delete_branch(client: SupabaseManagementClient, branch_id: str) -> dict:
    """Delete a database branch.

    Returns:
        Status dict.
    """
    return client.request("DELETE", f"/branches/{branch_id}")


def reset_branch(client: SupabaseManagementClient, branch_id: str) -> dict:
    """Reset a database branch to match production.

    Returns:
        Status dict.
    """
    return client.request("POST", f"/branches/{branch_id}/reset")
