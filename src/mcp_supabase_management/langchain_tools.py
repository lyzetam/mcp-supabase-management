"""LangChain @tool wrappers for Supabase Management API operations.

Usage:
    from mcp_supabase_management.langchain_tools import TOOLS

    # Or import individual tools:
    from mcp_supabase_management.langchain_tools import supabase_list_projects, supabase_execute_sql
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from .client import SupabaseManagementClient
from .operations import branches, database, functions, logs, orgs, projects, secrets


@lru_cache
def _get_client() -> SupabaseManagementClient:
    """Singleton SupabaseManagementClient configured from environment."""
    return SupabaseManagementClient()


def _json(obj) -> str:
    return json.dumps(obj, indent=2, default=str)


# =============================================================================
# Organizations
# =============================================================================


@tool
def supabase_list_organizations() -> str:
    """List all Supabase organizations."""
    return _json(orgs.list_organizations(_get_client()))


# =============================================================================
# Projects
# =============================================================================


@tool
def supabase_list_projects() -> str:
    """List all Supabase projects across all organizations."""
    return _json(projects.list_projects(_get_client()))


class ProjectRefInput(BaseModel):
    project_ref: str = Field(description="Project reference ID")


@tool(args_schema=ProjectRefInput)
def supabase_get_project(project_ref: str) -> str:
    """Get details for a specific Supabase project."""
    return _json(projects.get_project(_get_client(), project_ref))


class CreateProjectInput(BaseModel):
    name: str = Field(description="Project name")
    organization_id: str = Field(description="Organization ID")
    region: str = Field(default="us-east-1", description="Region (default: us-east-1)")
    db_password: Optional[str] = Field(default=None, description="Database password (auto-generated if not provided)")


@tool(args_schema=CreateProjectInput)
def supabase_create_project(
    name: str,
    organization_id: str,
    region: str = "us-east-1",
    db_password: Optional[str] = None,
) -> str:
    """Create a new Supabase project."""
    return _json(
        projects.create_project(
            _get_client(), name, organization_id, region, db_password
        )
    )


class DeleteProjectInput(BaseModel):
    project_ref: str = Field(description="Project reference ID")
    confirm: bool = Field(description="Must be true to confirm deletion")


@tool(args_schema=DeleteProjectInput)
def supabase_delete_project(project_ref: str, confirm: bool = False) -> str:
    """Delete a Supabase project (DESTRUCTIVE). Must set confirm=true."""
    if not confirm:
        return "ERROR: Must set confirm=true to delete a project"
    return _json(projects.delete_project(_get_client(), project_ref))


@tool(args_schema=ProjectRefInput)
def supabase_get_api_keys(project_ref: str) -> str:
    """Get API keys (anon, service_role) for a project."""
    return _json(projects.get_api_keys(_get_client(), project_ref))


@tool(args_schema=ProjectRefInput)
def supabase_get_project_url(project_ref: str) -> str:
    """Get the API URL for a project."""
    return _json(projects.get_project_url(_get_client(), project_ref))


# =============================================================================
# Database
# =============================================================================


@tool(args_schema=ProjectRefInput)
def supabase_list_tables(project_ref: str) -> str:
    """List all tables in a project's database."""
    return _json(database.list_tables(_get_client(), project_ref))


class ExecuteSqlInput(BaseModel):
    project_ref: str = Field(description="Project reference ID")
    query: str = Field(description="SQL query to execute")


@tool(args_schema=ExecuteSqlInput)
def supabase_execute_sql(project_ref: str, query: str) -> str:
    """Execute a SQL query on a project's database."""
    return _json(database.execute_sql(_get_client(), project_ref, query))


@tool(args_schema=ProjectRefInput)
def supabase_list_extensions(project_ref: str) -> str:
    """List installed PostgreSQL extensions."""
    return _json(database.list_extensions(_get_client(), project_ref))


@tool(args_schema=ProjectRefInput)
def supabase_list_migrations(project_ref: str) -> str:
    """List applied database migrations."""
    return _json(database.list_migrations(_get_client(), project_ref))


@tool(args_schema=ProjectRefInput)
def supabase_generate_types(project_ref: str) -> str:
    """Generate TypeScript types from database schema."""
    return _json(database.generate_types(_get_client(), project_ref))


# =============================================================================
# Branches
# =============================================================================


@tool(args_schema=ProjectRefInput)
def supabase_list_branches(project_ref: str) -> str:
    """List database branches for a project."""
    return _json(branches.list_branches(_get_client(), project_ref))


class CreateBranchInput(BaseModel):
    project_ref: str = Field(description="Project reference ID")
    branch_name: str = Field(description="Name for the new branch")
    git_branch: Optional[str] = Field(default=None, description="Associated git branch name")


@tool(args_schema=CreateBranchInput)
def supabase_create_branch(
    project_ref: str,
    branch_name: str,
    git_branch: Optional[str] = None,
) -> str:
    """Create a new database branch."""
    return _json(
        branches.create_branch(_get_client(), project_ref, branch_name, git_branch)
    )


class BranchIdInput(BaseModel):
    branch_id: str = Field(description="Branch ID")


@tool(args_schema=BranchIdInput)
def supabase_delete_branch(branch_id: str) -> str:
    """Delete a database branch."""
    return _json(branches.delete_branch(_get_client(), branch_id))


@tool(args_schema=BranchIdInput)
def supabase_reset_branch(branch_id: str) -> str:
    """Reset a database branch to match production."""
    return _json(branches.reset_branch(_get_client(), branch_id))


# =============================================================================
# Edge Functions
# =============================================================================


@tool(args_schema=ProjectRefInput)
def supabase_list_functions(project_ref: str) -> str:
    """List edge functions for a project."""
    return _json(functions.list_functions(_get_client(), project_ref))


class GetFunctionInput(BaseModel):
    project_ref: str = Field(description="Project reference ID")
    function_slug: str = Field(description="Function slug/name")


@tool(args_schema=GetFunctionInput)
def supabase_get_function(project_ref: str, function_slug: str) -> str:
    """Get details for a specific edge function."""
    return _json(functions.get_function(_get_client(), project_ref, function_slug))


class DeployFunctionInput(BaseModel):
    project_ref: str = Field(description="Project reference ID")
    function_slug: str = Field(description="Function slug/name")
    code: str = Field(description="Function code (TypeScript/JavaScript)")
    verify_jwt: bool = Field(default=True, description="Require JWT verification (default: true)")


@tool(args_schema=DeployFunctionInput)
def supabase_deploy_function(
    project_ref: str,
    function_slug: str,
    code: str,
    verify_jwt: bool = True,
) -> str:
    """Deploy an edge function."""
    return _json(
        functions.deploy_function(
            _get_client(), project_ref, function_slug, code, verify_jwt
        )
    )


# =============================================================================
# Secrets
# =============================================================================


@tool(args_schema=ProjectRefInput)
def supabase_list_secrets(project_ref: str) -> str:
    """List secrets for a project (names only)."""
    return _json(secrets.list_secrets(_get_client(), project_ref))


class SetSecretsInput(BaseModel):
    project_ref: str = Field(description="Project reference ID")
    secrets_list: list[dict] = Field(description="Array of {name, value} objects", alias="secrets")


@tool(args_schema=SetSecretsInput)
def supabase_set_secrets(project_ref: str, secrets_list: list[dict] = []) -> str:
    """Create or update project secrets. Pass secrets as array of {name, value} objects."""
    return _json(secrets.set_secrets(_get_client(), project_ref, secrets_list))


class DeleteSecretsInput(BaseModel):
    project_ref: str = Field(description="Project reference ID")
    secret_names: list[str] = Field(description="Names of secrets to delete")


@tool(args_schema=DeleteSecretsInput)
def supabase_delete_secrets(project_ref: str, secret_names: list[str] = []) -> str:
    """Delete project secrets."""
    return _json(secrets.delete_secrets(_get_client(), project_ref, secret_names))


# =============================================================================
# Logs
# =============================================================================


class GetLogsInput(BaseModel):
    project_ref: str = Field(description="Project reference ID")
    service: str = Field(default="api", description="Service: api, auth, db, realtime, storage, functions")
    limit: int = Field(default=100, description="Number of log entries (default: 100)")


@tool(args_schema=GetLogsInput)
def supabase_get_logs(
    project_ref: str,
    service: str = "api",
    limit: int = 100,
) -> str:
    """Get project logs (api, auth, db, realtime, storage, functions)."""
    return _json(logs.get_logs(_get_client(), project_ref, service, limit))


# =============================================================================
# TOOLS list — importable by LangChain agents
# =============================================================================

TOOLS = [
    # Organizations
    supabase_list_organizations,
    # Projects
    supabase_list_projects,
    supabase_get_project,
    supabase_create_project,
    supabase_delete_project,
    supabase_get_api_keys,
    supabase_get_project_url,
    # Database
    supabase_list_tables,
    supabase_execute_sql,
    supabase_list_extensions,
    supabase_list_migrations,
    supabase_generate_types,
    # Branches
    supabase_list_branches,
    supabase_create_branch,
    supabase_delete_branch,
    supabase_reset_branch,
    # Functions
    supabase_list_functions,
    supabase_get_function,
    supabase_deploy_function,
    # Secrets
    supabase_list_secrets,
    supabase_set_secrets,
    supabase_delete_secrets,
    # Logs
    supabase_get_logs,
]
