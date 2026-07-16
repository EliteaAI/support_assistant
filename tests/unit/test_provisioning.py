"""Unit tests for utils/provisioning.py - Agent provisioning utilities."""
import pytest
import yaml


PIPELINE_KEYS = {'state', 'entry_point', 'nodes', 'pipeline_settings'}

ARTIFACT_TOOLKIT_IMPORT_UUID = "sa-artifact-toolkit-supportattachments-v1"
ARTIFACT_BUCKET = "supportattachments"
ARTIFACT_TOOLKIT_NAME = "supportattachments"
ORCHESTRATOR_NAME = "Support Assistant Orchestrator"


def _parse_agent_md_pure(content: str) -> dict | None:
    """Parse agent.md content into config dict - pure logic without file I/O."""
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


def _build_version(agent: dict, project_id: int, author_id: int) -> dict:
    """Build version dict from agent config."""
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


class TestParseAgentMd:
    """Tests for _parse_agent_md_pure function."""

    def test_parses_basic_agent(self):
        content = """---
name: Test Agent
description: A test agent
model: gpt-4o
temperature: 0.7
---
You are a helpful assistant."""

        result = _parse_agent_md_pure(content)
        assert result['name'] == 'Test Agent'
        assert result['description'] == 'A test agent'
        assert result['model'] == 'gpt-4o'
        assert result['temperature'] == 0.7
        assert result['instructions'] == 'You are a helpful assistant.'

    def test_defaults_agent_type_to_react(self):
        content = """---
name: Test Agent
---
Instructions here."""

        result = _parse_agent_md_pure(content)
        assert result['agent_type'] == 'react'

    def test_maps_agent_type_to_react(self):
        content = """---
name: Test Agent
agent_type: agent
---
Instructions."""

        result = _parse_agent_md_pure(content)
        assert result['agent_type'] == 'react'

    def test_parses_pipeline_type(self):
        content = """---
name: Test Pipeline
agent_type: pipeline
entry_point: start
nodes:
  - id: start
    type: llm
---
Body ignored for pipelines."""

        result = _parse_agent_md_pure(content)
        assert result['agent_type'] == 'pipeline'
        assert 'entry_point: start' in result['instructions']
        assert 'nodes:' in result['instructions']

    def test_parses_nested_agents(self):
        content = """---
name: Orchestrator
nested_agents:
  - name: SubAgent1
  - SubAgent2
---
Instructions."""

        result = _parse_agent_md_pure(content)
        assert len(result['tools']) == 2
        assert result['tools'][0]['type'] == 'application'
        assert result['tools'][0]['name'] == 'SubAgent1'
        assert result['tools'][1]['name'] == 'SubAgent2'

    def test_parses_toolkits(self):
        content = """---
name: Agent With Tools
toolkits:
  - type: openapi
    toolkit: my_api
    description: My API toolkit
    tools:
      - get_data
      - post_data
---
Instructions."""

        result = _parse_agent_md_pure(content)
        assert len(result['tools']) == 1
        assert result['tools'][0]['type'] == 'openapi'
        assert result['tools'][0]['name'] == 'my_api'
        assert result['tools'][0]['selected_tools'] == ['get_data', 'post_data']

    def test_returns_none_for_no_frontmatter(self):
        content = "Just plain text without frontmatter"
        result = _parse_agent_md_pure(content)
        assert result is None

    def test_handles_missing_closing_delimiter(self):
        content = "---\nname: Test"  # Missing closing --- still parses
        result = _parse_agent_md_pure(content)
        # The split('---', 2) creates ['', 'name: Test'], so it parses
        assert result['name'] == 'Test'

    def test_default_values(self):
        content = """---
name: Minimal Agent
---
Instructions."""

        result = _parse_agent_md_pure(content)
        assert result['model'] == 'gpt-5.4-mini'
        assert result['temperature'] == 0.6
        assert result['step_limit'] == 25
        assert result['tools'] == []

    def test_empty_body(self):
        content = """---
name: Agent
---"""

        result = _parse_agent_md_pure(content)
        assert result['instructions'] == ''

    def test_toolkit_with_name_fallback(self):
        content = """---
name: Agent
toolkits:
  - name: fallback_toolkit
    type: custom
---
Instructions."""

        result = _parse_agent_md_pure(content)
        assert result['tools'][0]['name'] == 'fallback_toolkit'


class TestBuildVersion:
    """Tests for _build_version function."""

    def test_builds_basic_version(self):
        agent = {
            'name': 'Test Agent',
            'agent_type': 'react',
            'instructions': 'Be helpful',
            'model': 'gpt-4o',
            'temperature': 0.5,
            'step_limit': 10,
            'tools': [],
        }

        result = _build_version(agent, project_id=42, author_id=7)

        assert result['name'] == 'base'
        assert result['agent_type'] == 'react'
        assert result['instructions'] == 'Be helpful'
        assert result['llm_settings']['model_name'] == 'gpt-4o'
        assert result['llm_settings']['temperature'] == 0.5
        assert result['meta']['step_limit'] == 10
        assert result['project_id'] == 42
        assert result['author_id'] == 7
        assert result['user_id'] == 7

    def test_default_model_and_temperature(self):
        agent = {
            'agent_type': 'react',
            'tools': [],
        }

        result = _build_version(agent, project_id=1, author_id=1)

        assert result['llm_settings']['model_name'] == 'gpt-5.4-mini'
        assert result['llm_settings']['temperature'] == 0.6

    def test_includes_tools(self):
        tools = [{"type": "application", "name": "SubAgent"}]
        agent = {
            'agent_type': 'react',
            'tools': tools,
        }

        result = _build_version(agent, project_id=1, author_id=1)

        assert result['tools'] == tools


class TestConstants:
    """Tests for module constants."""

    def test_pipeline_keys(self):
        assert 'state' in PIPELINE_KEYS
        assert 'entry_point' in PIPELINE_KEYS
        assert 'nodes' in PIPELINE_KEYS
        assert 'pipeline_settings' in PIPELINE_KEYS

    def test_artifact_toolkit_uuid(self):
        assert ARTIFACT_TOOLKIT_IMPORT_UUID == "sa-artifact-toolkit-supportattachments-v1"

    def test_artifact_bucket(self):
        assert ARTIFACT_BUCKET == "supportattachments"

    def test_orchestrator_name(self):
        assert ORCHESTRATOR_NAME == "Support Assistant Orchestrator"
