"""Tests for Supabase Management API operations using respx mocks."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from mcp_supabase_management.client import SupabaseManagementClient
from mcp_supabase_management.operations import (
    branches,
    database,
    functions,
    logs,
    orgs,
    projects,
    secrets,
)

BASE = "https://api.supabase.com/v1"


@pytest.fixture
def client():
    """SupabaseManagementClient with test token."""
    return SupabaseManagementClient(access_token="test-token-123")


# =============================================================================
# Organizations
# =============================================================================


@respx.mock
def test_list_organizations(client):
    respx.get(f"{BASE}/organizations").mock(
        return_value=httpx.Response(200, json=[{"id": "org-1", "name": "My Org"}])
    )
    result = orgs.list_organizations(client)
    assert len(result) == 1
    assert result[0]["id"] == "org-1"


# =============================================================================
# Projects
# =============================================================================


@respx.mock
def test_list_projects(client):
    respx.get(f"{BASE}/projects").mock(
        return_value=httpx.Response(200, json=[{"id": "proj-1", "name": "Test"}])
    )
    result = projects.list_projects(client)
    assert len(result) == 1
    assert result[0]["name"] == "Test"


@respx.mock
def test_get_project(client):
    respx.get(f"{BASE}/projects/abc123").mock(
        return_value=httpx.Response(200, json={"id": "abc123", "name": "My Project"})
    )
    result = projects.get_project(client, "abc123")
    assert result["id"] == "abc123"


@respx.mock
def test_create_project(client):
    respx.post(f"{BASE}/projects").mock(
        return_value=httpx.Response(201, json={"id": "new-proj", "name": "New"})
    )
    result = projects.create_project(client, "New", "org-1")
    assert result["name"] == "New"


@respx.mock
def test_delete_project(client):
    respx.delete(f"{BASE}/projects/abc123").mock(
        return_value=httpx.Response(204)
    )
    result = projects.delete_project(client, "abc123")
    assert result["status"] == "success"


@respx.mock
def test_get_api_keys(client):
    keys = [{"name": "anon", "api_key": "anon-key"}, {"name": "service_role", "api_key": "svc-key"}]
    respx.get(f"{BASE}/projects/abc123/api-keys").mock(
        return_value=httpx.Response(200, json=keys)
    )
    result = projects.get_api_keys(client, "abc123")
    assert len(result) == 2
    assert result[0]["name"] == "anon"


def test_get_project_url(client):
    result = projects.get_project_url(client, "abc123")
    assert result["url"] == "https://abc123.supabase.co"


# =============================================================================
# Database
# =============================================================================


@respx.mock
def test_execute_sql(client):
    respx.post(f"{BASE}/projects/abc123/database/query").mock(
        return_value=httpx.Response(200, json=[{"count": 42}])
    )
    result = database.execute_sql(client, "abc123", "SELECT count(*) FROM users")
    assert result == [{"count": 42}]


@respx.mock
def test_list_tables(client):
    rows = [{"schema": "public", "name": "users", "owner": "postgres"}]
    respx.post(f"{BASE}/projects/abc123/database/query").mock(
        return_value=httpx.Response(200, json=rows)
    )
    result = database.list_tables(client, "abc123")
    assert result[0]["name"] == "users"


@respx.mock
def test_list_extensions(client):
    rows = [{"name": "pgvector", "version": "0.5.1"}]
    respx.post(f"{BASE}/projects/abc123/database/query").mock(
        return_value=httpx.Response(200, json=rows)
    )
    result = database.list_extensions(client, "abc123")
    assert result[0]["name"] == "pgvector"


@respx.mock
def test_list_migrations(client):
    rows = [{"version": "20240101", "name": "init", "executed_at": "2024-01-01"}]
    respx.post(f"{BASE}/projects/abc123/database/query").mock(
        return_value=httpx.Response(200, json=rows)
    )
    result = database.list_migrations(client, "abc123")
    assert result[0]["version"] == "20240101"


@respx.mock
def test_list_migrations_no_table(client):
    respx.post(f"{BASE}/projects/abc123/database/query").mock(
        return_value=httpx.Response(400, json={"error": "relation does not exist"})
    )
    result = database.list_migrations(client, "abc123")
    assert "error" in result


@respx.mock
def test_generate_types(client):
    respx.get(f"{BASE}/projects/abc123/types/typescript").mock(
        return_value=httpx.Response(200, json={"types": "export interface Database {}"})
    )
    result = database.generate_types(client, "abc123")
    assert "types" in result


# =============================================================================
# Branches
# =============================================================================


@respx.mock
def test_list_branches(client):
    respx.get(f"{BASE}/projects/abc123/branches").mock(
        return_value=httpx.Response(200, json=[{"id": "br-1", "name": "dev"}])
    )
    result = branches.list_branches(client, "abc123")
    assert len(result) == 1


@respx.mock
def test_create_branch(client):
    respx.post(f"{BASE}/projects/abc123/branches").mock(
        return_value=httpx.Response(201, json={"id": "br-2", "name": "feature"})
    )
    result = branches.create_branch(client, "abc123", "feature")
    assert result["name"] == "feature"


@respx.mock
def test_create_branch_with_git_branch(client):
    respx.post(f"{BASE}/projects/abc123/branches").mock(
        return_value=httpx.Response(201, json={"id": "br-3", "name": "staging"})
    )
    result = branches.create_branch(client, "abc123", "staging", git_branch="staging")
    assert result["name"] == "staging"


@respx.mock
def test_delete_branch(client):
    respx.delete(f"{BASE}/branches/br-1").mock(
        return_value=httpx.Response(204)
    )
    result = branches.delete_branch(client, "br-1")
    assert result["status"] == "success"


@respx.mock
def test_reset_branch(client):
    respx.post(f"{BASE}/branches/br-1/reset").mock(
        return_value=httpx.Response(200, json={"status": "reset"})
    )
    result = branches.reset_branch(client, "br-1")
    assert "status" in result


# =============================================================================
# Edge Functions
# =============================================================================


@respx.mock
def test_list_functions(client):
    respx.get(f"{BASE}/projects/abc123/functions").mock(
        return_value=httpx.Response(200, json=[{"slug": "hello", "status": "ACTIVE"}])
    )
    result = functions.list_functions(client, "abc123")
    assert result[0]["slug"] == "hello"


@respx.mock
def test_get_function(client):
    respx.get(f"{BASE}/projects/abc123/functions/hello").mock(
        return_value=httpx.Response(200, json={"slug": "hello", "version": 3})
    )
    result = functions.get_function(client, "abc123", "hello")
    assert result["slug"] == "hello"


@respx.mock
def test_deploy_function(client):
    respx.post(f"{BASE}/projects/abc123/functions/hello").mock(
        return_value=httpx.Response(200, json={"slug": "hello", "version": 4})
    )
    result = functions.deploy_function(client, "abc123", "hello", "export default () => 'ok'")
    assert result["version"] == 4


# =============================================================================
# Secrets
# =============================================================================


@respx.mock
def test_list_secrets(client):
    respx.get(f"{BASE}/projects/abc123/secrets").mock(
        return_value=httpx.Response(200, json=[{"name": "MY_SECRET"}])
    )
    result = secrets.list_secrets(client, "abc123")
    assert result[0]["name"] == "MY_SECRET"


@respx.mock
def test_set_secrets(client):
    respx.post(f"{BASE}/projects/abc123/secrets").mock(
        return_value=httpx.Response(200, json={"status": "ok"})
    )
    result = secrets.set_secrets(client, "abc123", [{"name": "KEY", "value": "val"}])
    assert "status" in result


@respx.mock
def test_delete_secrets(client):
    respx.delete(f"{BASE}/projects/abc123/secrets").mock(
        return_value=httpx.Response(204)
    )
    result = secrets.delete_secrets(client, "abc123", ["MY_SECRET"])
    assert result["status"] == "success"


# =============================================================================
# Logs
# =============================================================================


@respx.mock
def test_get_logs(client):
    respx.get(f"{BASE}/projects/abc123/analytics/endpoints/logs.all").mock(
        return_value=httpx.Response(200, json=[{"timestamp": "2024-01-01", "event": "request"}])
    )
    result = logs.get_logs(client, "abc123")
    assert len(result) == 1


@respx.mock
def test_get_logs_with_params(client):
    respx.get(f"{BASE}/projects/abc123/analytics/endpoints/logs.all").mock(
        return_value=httpx.Response(200, json=[])
    )
    result = logs.get_logs(client, "abc123", service="auth", limit=10)
    assert result == []


# =============================================================================
# Client
# =============================================================================


def test_client_requires_token():
    """Client should raise if no token provided."""
    import os
    old = os.environ.pop("SUPABASE_ACCESS_TOKEN", None)
    try:
        with pytest.raises(ValueError, match="SUPABASE_ACCESS_TOKEN"):
            SupabaseManagementClient(access_token="")
    finally:
        if old:
            os.environ["SUPABASE_ACCESS_TOKEN"] = old
