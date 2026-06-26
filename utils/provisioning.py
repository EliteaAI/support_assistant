"""Support Assistant default agent provisioning."""

import os

import yaml
from pylon.core.tools import log

AGENTS_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'agents')
ARTIFACTS_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'supportattachments')

ARTIFACT_TOOLKIT_IMPORT_UUID = "sa-artifact-toolkit-supportattachments-v1"
ARTIFACT_BUCKET = "supportattachments"
ARTIFACT_TOOLKIT_NAME = "supportattachments"
ORCHESTRATOR_NAME = "Support Assistant Orchestrator"

PIPELINE_KEYS = {'state', 'entry_point', 'nodes', 'pipeline_settings'}

AGENT_IMPORT_ORDER = [
    "query_user_info",
    "fetch_ui_context",
    "ELITEA GitHub Issues Agent",
    "Pipeline Expert",
    "Bug Reporter",
    "Context Enrichment Agent",
    "Assistant for ELITEA Documents",
    "Code Explorer agent",
    ORCHESTRATOR_NAME,
]

INITIAL_ARTIFACTS = {}  # kept for backwards compat — use load_initial_artifacts() instead


def load_initial_artifacts() -> dict:
    """Load artifact files from data/supportattachments/ as {relative_path: bytes}."""
    artifacts = {}
    if not os.path.exists(ARTIFACTS_DATA_DIR):
        log.warning(f"[PROVISION] Artifacts data directory not found: {ARTIFACTS_DATA_DIR}")
        return artifacts
    for dirpath, _, filenames in os.walk(ARTIFACTS_DATA_DIR):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(full_path, ARTIFACTS_DATA_DIR)
            try:
                with open(full_path, 'rb') as f:
                    artifacts[rel_path] = f.read()
            except Exception as e:
                log.error(f"[PROVISION] Failed to read artifact {rel_path}: {e}")
    return artifacts


def _parse_agent_md(filepath: str) -> dict | None:
    """Parse a .agent.md or .pipeline.md file into an agent config dict."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            return None

        parts = content.split('---', 2)
        if len(parts) < 2:
            return None

        frontmatter = yaml.safe_load(parts[1]) or {}
        body = parts[2].strip() if len(parts) > 2 else ''

        agent_type = frontmatter.get('agent_type', 'react')

        if agent_type == 'pipeline':
            pipeline_data = {k: v for k, v in frontmatter.items() if k in PIPELINE_KEYS}
            instructions = yaml.dump(pipeline_data, default_flow_style=False, allow_unicode=True)
        else:
            instructions = body

        # Map generic 'agent' type to the platform-specific 'react' type
        if agent_type == 'agent':
            agent_type = 'react'

        tools = []

        for nested in frontmatter.get('nested_agents', []):
            name = nested.get('name') if isinstance(nested, dict) else nested
            tools.append({
                "type": "application",
                "application_name": name,
                "name": name,
            })

        for tk in frontmatter.get('toolkits', []):
            tools.append({
                "type": tk.get('type', 'openapi'),
                "name": tk.get('toolkit', tk.get('name', '')),
                "description": tk.get('description', ''),
                "settings": tk.get('settings', {}),
                "selected_tools": tk.get('tools', []),
                "meta": tk.get('meta', {}),
            })

        return {
            'name': frontmatter.get('name', ''),
            'description': frontmatter.get('description', ''),
            'agent_type': agent_type,
            'model': frontmatter.get('model', 'gpt-5.4-mini'),
            'temperature': frontmatter.get('temperature', 0.6),
            'instructions': instructions,
            'step_limit': frontmatter.get('step_limit', 25),
            'tools': tools,
        }
    except Exception as e:
        log.error(f"[PROVISION] Failed to parse {filepath}: {e}")
        return None


def _load_all_agents() -> dict:
    """Load all agent definitions from the data/agents directory keyed by name."""
    agents = {}
    if not os.path.exists(AGENTS_DATA_DIR):
        log.warning(f"[PROVISION] Agents data directory not found: {AGENTS_DATA_DIR}")
        return agents

    for filename in os.listdir(AGENTS_DATA_DIR):
        if filename.endswith('.md'):
            filepath = os.path.join(AGENTS_DATA_DIR, filename)
            agent_data = _parse_agent_md(filepath)
            if agent_data and agent_data.get('name'):
                agents[agent_data['name']] = agent_data

    return agents


def _build_version(agent: dict, project_id: int, author_id: int) -> dict:
    return {
        "name": "base",
        "agent_type": agent['agent_type'],
        "instructions": agent.get('instructions', ''),
        "llm_settings": {
            "model_name": agent.get('model', 'gpt-5.4-mini'),
            "temperature": agent.get('temperature', 0.6),
        },
        "meta": {
            "step_limit": agent.get('step_limit', 25),
        },
        "author_id": author_id,
        "project_id": project_id,
        "user_id": author_id,
        "tools": agent.get('tools', []),
    }


def build_import_data(project_id: int, author_id: int) -> list:
    """Build import_wizard data list for all default support assistant agents."""
    agents = _load_all_agents()
    if not agents:
        log.warning("[PROVISION] No agents found in data directory")
        return []

    import_data = []

    for agent_name in AGENT_IMPORT_ORDER:
        agent = agents.get(agent_name)
        if not agent:
            log.warning(f"[PROVISION] Agent definition not found: {agent_name}")
            continue

        tools = list(agent.get('tools', []))

        if agent_name == ORCHESTRATOR_NAME:
            # Attach the artifact toolkit via import_uuid reference
            tools.append({"import_uuid": ARTIFACT_TOOLKIT_IMPORT_UUID})

        version = _build_version(agent, project_id, author_id)
        version['tools'] = tools

        import_data.append({
            "entity": "agents",
            "name": agent['name'],
            "description": agent.get('description', ''),
            "is_selected": True,
            "owner_id": project_id,
            "versions": [version],
        })

    # Artifact toolkit (top-level, shared)
    import_data.insert(
        len(import_data) - 1,  # before orchestrator
        {
            "entity": "toolkits",
            "import_uuid": ARTIFACT_TOOLKIT_IMPORT_UUID,
            "name": ARTIFACT_TOOLKIT_NAME,
            "description": "Support Assistant knowledge base and attachment storage",
            "is_selected": True,
            "type": "artifact",
            "settings": {"bucket": ARTIFACT_BUCKET},
            "selected_tools": [
                "list_files", "read_file", "append_data", "read_multiple_files",
                "grep_file", "create_file", "edit_file", "get_file_metadata",
            ],
            "meta": {},
        }
    )

    return import_data

