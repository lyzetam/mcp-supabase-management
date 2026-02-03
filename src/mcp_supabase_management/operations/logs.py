"""Log operations."""

from __future__ import annotations

from ..client import SupabaseManagementClient


def get_logs(
    client: SupabaseManagementClient,
    project_ref: str,
    service: str = "api",
    limit: int = 100,
) -> list:
    """Get project logs.

    Args:
        service: One of api, auth, db, realtime, storage, functions.
        limit: Number of log entries to retrieve.

    Returns:
        List of log entries.
    """
    return client.request(
        "GET",
        f"/projects/{project_ref}/analytics/endpoints/logs.all",
        params={"product": service, "limit": limit},
    )
