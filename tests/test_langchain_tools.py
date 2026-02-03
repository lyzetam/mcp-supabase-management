"""Tests for LangChain tool interfaces."""

from langchain_core.tools import BaseTool

from mcp_supabase_management.langchain_tools import TOOLS


def test_tools_count():
    """Verify TOOLS list has the expected number of tools (23)."""
    assert len(TOOLS) == 23


def test_all_tools_are_base_tool():
    """Every entry in TOOLS must be a LangChain BaseTool instance."""
    for t in TOOLS:
        assert isinstance(t, BaseTool), f"{t} is not a BaseTool"


def test_tool_names_follow_convention():
    """All tool names should start with supabase_."""
    for t in TOOLS:
        assert t.name.startswith("supabase_"), f"Tool {t.name} does not follow supabase_ naming convention"


def test_tool_names_are_unique():
    """No duplicate tool names."""
    names = [t.name for t in TOOLS]
    assert len(names) == len(set(names)), f"Duplicate tool names: {names}"


def test_expected_tools_present():
    """Check all 24 tools are in the TOOLS list."""
    names = {t.name for t in TOOLS}
    expected = {
        # Organizations
        "supabase_list_organizations",
        # Projects
        "supabase_list_projects",
        "supabase_get_project",
        "supabase_create_project",
        "supabase_delete_project",
        "supabase_get_api_keys",
        "supabase_get_project_url",
        # Database
        "supabase_list_tables",
        "supabase_execute_sql",
        "supabase_list_extensions",
        "supabase_list_migrations",
        "supabase_generate_types",
        # Branches
        "supabase_list_branches",
        "supabase_create_branch",
        "supabase_delete_branch",
        "supabase_reset_branch",
        # Functions
        "supabase_list_functions",
        "supabase_get_function",
        "supabase_deploy_function",
        # Secrets
        "supabase_list_secrets",
        "supabase_set_secrets",
        "supabase_delete_secrets",
        # Logs
        "supabase_get_logs",
    }
    assert expected == names


def test_all_tools_have_descriptions():
    """Every tool should have a non-empty description."""
    for t in TOOLS:
        assert t.description, f"Tool {t.name} has no description"
