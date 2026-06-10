from pylon.core.tools import log
from tools import config as c, auth, rpc_tools


MCP_ENDPOINT_CONFIGS = [
    {"suffix": "elitea_core/applications", "name": "Elitea Applications"},
    {"suffix": "elitea_core/chat", "name": "Elitea Chat"},
    {"suffix": "elitea_core/toolkits", "name": "Elitea Toolkits"},
]


def _get_project_system_token(project_id: int) -> str | None:
    """Get or create a system token for the project's system user."""

    system_user = rpc_tools.RpcMixin().rpc.timeout(5).admin_get_project_system_user(project_id)
    if not system_user:
        log.warning(f"[MCP Utils] System user not found for project {project_id}")
        return None

    system_user_id = system_user["id"]
    all_tokens = auth.list_tokens(system_user_id)

    if all_tokens:
        token_id = all_tokens[0]["id"]
    else:
        token_id = auth.add_token(system_user_id, "mcp-internal")
        log.info(f"[MCP Utils] Created system token for project {project_id}")

    return auth.encode_token(token_id)


def _get_internal_base_url() -> str:
    """Get internal base URL for container-to-container communication."""
    base_url = c.APP_HOST
    if not base_url or base_url in ('http://localhost', 'http://127.0.0.1'):
        base_url = 'http://pylon_main:8080'
    return base_url


def _build_mcp_url(base_url: str, user_project_id: int, suffix: str) -> str:
    return f"{base_url}/app/{user_project_id}/mcp/{suffix}"


def add_mcp_toolkits_to_conversation(
    support_project_id: int,
    user_id: int,
    conversation_id: int,
) -> None:
    """
    Build MCP endpoint list and delegate toolkit creation/participant-linking
    to elitea_core via RPC to avoid direct cross-plugin model imports.
    """
    base_url = _get_internal_base_url()
    if not base_url:
        log.warning("[MCP Utils] APP_HOST not configured — skipping MCP toolkit creation")
        return

    user_project = rpc_tools.RpcMixin().rpc.timeout(5).admin_get_user_private_project(user_id)

    if not user_project:
        log.warning(f"[MCP Utils] Private project not found for user {user_id} — skipping MCP toolkit creation")
        return

    user_project_id = user_project.id

    system_token = _get_project_system_token(user_project_id)
    if not system_token:
        log.warning(f"[MCP Utils] Could not get system token for project {user_project_id} — skipping MCP toolkit creation")
        return

    mcp_endpoints = [
        {
            "url": _build_mcp_url(base_url, user_project_id, ep["suffix"]),
            "name": f'{ep["name"]} - {user_id}',
            "description": f"Elitea platform MCP — {ep['suffix']}",
        }
        for ep in MCP_ENDPOINT_CONFIGS
    ]

    rpc_tools.RpcMixin().rpc.timeout(5).chat_add_mcp_toolkits_to_conversation(
        support_project_id=support_project_id,
        user_id=user_id,
        conversation_id=conversation_id,
        mcp_endpoints=mcp_endpoints,
        auth_headers={"Authorization": f"Bearer {system_token}"},
    )

