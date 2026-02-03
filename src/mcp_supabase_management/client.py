"""Supabase Management API client with both sync and async methods."""

from __future__ import annotations

import os
from typing import Any

import httpx

MANAGEMENT_API = "https://api.supabase.com/v1"


class SupabaseManagementClient:
    """Client for the Supabase Management API.

    Provides both sync (for LangChain tools / operations) and async
    (for MCP server) methods via httpx.

    Reads credentials from environment variables by default:
    - SUPABASE_ACCESS_TOKEN (required)
    """

    def __init__(self, access_token: str | None = None) -> None:
        self.access_token = (
            access_token or os.environ.get("SUPABASE_ACCESS_TOKEN", "")
        ).strip()
        if not self.access_token:
            raise ValueError("SUPABASE_ACCESS_TOKEN environment variable not set")

        self._headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Sync HTTP helpers (used by operations / LangChain tools)
    # ------------------------------------------------------------------

    def _sync_client(self) -> httpx.Client:
        return httpx.Client(
            base_url=MANAGEMENT_API,
            headers=self._headers,
            timeout=60.0,
        )

    def request(
        self,
        method: str,
        endpoint: str,
        data: Any | None = None,
        params: dict | None = None,
    ) -> dict | list:
        """Make a synchronous Management API request."""
        with self._sync_client() as client:
            response = client.request(
                method=method,
                url=endpoint,
                json=data,
                params=params,
            )
            response.raise_for_status()
            if response.status_code == 204:
                return {"status": "success"}
            return response.json()

    # ------------------------------------------------------------------
    # Async HTTP helpers (used by MCP server)
    # ------------------------------------------------------------------

    def _async_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=MANAGEMENT_API,
            headers=self._headers,
            timeout=60.0,
        )

    async def arequest(
        self,
        method: str,
        endpoint: str,
        data: Any | None = None,
        params: dict | None = None,
    ) -> dict | list:
        """Make an asynchronous Management API request."""
        async with self._async_client() as client:
            response = await client.request(
                method=method,
                url=endpoint,
                json=data,
                params=params,
            )
            response.raise_for_status()
            if response.status_code == 204:
                return {"status": "success"}
            return response.json()
