"""Edge function operations."""

from __future__ import annotations

from ..client import SupabaseManagementClient


def list_functions(client: SupabaseManagementClient, project_ref: str) -> list:
    """List edge functions for a project.

    Returns:
        List of function dicts.
    """
    return client.request("GET", f"/projects/{project_ref}/functions")


def get_function(
    client: SupabaseManagementClient, project_ref: str, function_slug: str
) -> dict:
    """Get details for a specific edge function.

    Returns:
        Function details dict.
    """
    return client.request(
        "GET", f"/projects/{project_ref}/functions/{function_slug}"
    )


def deploy_function(
    client: SupabaseManagementClient,
    project_ref: str,
    function_slug: str,
    code: str,
    verify_jwt: bool = True,
) -> dict:
    """Deploy an edge function.

    Returns:
        Deployment result dict.
    """
    return client.request(
        "POST",
        f"/projects/{project_ref}/functions/{function_slug}",
        data={
            "body": code,
            "verify_jwt": verify_jwt,
        },
    )
