---
name: fetch_ui_context
description: 'Fetch agent, pipeline, toolkit, MCP, chat history, etc, details from ELITEA the user is currently viewing.


  CALL THIS TOOL when the runtime UI context shows that the user is on an entity page:

  agent, pipeline, toolkit, MCP, app, credential, or conversation.


  Arguments:

  - project_id: the user''s current project_id from runtime UI context.

  - entity_type: the entity kind, such as "agent", "pipeline", "toolkit", "mcp", "app", "credential", or "conversation".

  - entity_id: the ID of that entity. This is the same thing as agent_id, pipeline_id, toolkit_id, mcp_id, app_id, credential_id,
  or conversation_id depending on entity_type.

  - version_id: optional version ID from runtime UI context. Use 0 if absent.


  Important:

  The entity_id is usually found in the page URL.


  Examples:

  - /agents/all/123 means entity_type="agent", entity_id=123

  - /pipelines/all/545 means entity_type="pipeline", entity_id=545

  - /toolkits/all/77 means entity_type="toolkit", entity_id=77

  - /mcp/all/88 means entity_type="mcp", entity_id=88

  - /apps/all/99 means entity_type="app", entity_id=99

  - /credentials/all/42 means entity_type="credential", entity_id=42


  Use this tool before answering questions about the user''s current setup, configuration, instructions, attached tools, selected
  toolkit operations, pipeline YAML, model settings, variables, credentials, or troubleshooting.


  Returns a redacted ui_context object with the actual entity configuration. Secrets, tokens, passwords, and API keys are
  not returned.'
model: gpt-5.4-mini
temperature: 0.6
max_tokens: -1
agent_type: pipeline
step_limit: 25
conversation_starters:
- 'Task: {"project_id":406,"entity_type":"pipeline","entity_id":603,"version_id":1138}'
state:
  entity_id:
    type: int
    value: ''
  entity_type:
    type: str
    value: ''
  input:
    type: str
    value: ''
  messages:
    type: list
    value: []
  project_id:
    type: int
    value: ''
  ui_context:
    type: dict
    value: {}
  version_id:
    type: int
    value: ''
entry_point: parse_ui_context_vars
nodes:
- id: parse_ui_context_vars
  type: llm
  input:
  - input
  input_mapping:
    chat_history:
      type: fixed
      value: []
    system:
      type: fixed
      value: "Extract these four values from the task text: project_id, entity_type, entity_id, version_id.\n\nReturn only\
        \ valid JSON with this exact shape:\n{\n  \"project_id\": <integer>,\n  \"entity_type\": \"<agent|pipeline|toolkit|mcp|app|credential|conversation>\"\
        ,\n  \"entity_id\": <integer>,\n  \"version_id\": <integer>\n}\n\nRules:\n- Parse values from patterns like project_id=360,\
        \ entity_type=agent, entity_id=85, version_id=134.\n- Cast numeric values to integers.\n- If version_id is missing,\
        \ use 0.\n- If any required value except version_id is missing, set it to null.\n- Do not include explanations or\
        \ extra fields."
    task:
      type: fstring
      value: 'input: {input}'
  output:
  - entity_id
  - entity_type
  - project_id
  - version_id
  structured_output: true
  transition: route_by_entity_type
- id: route_by_entity_type
  type: router
  condition: '{% set t = entity_type|default('''', true)|lower %}

    {% if t == ''agent'' or t == ''pipeline'' or t == ''app'' %}

    fetch_application_context

    {% elif t == ''toolkit'' or t == ''mcp'' %}

    fetch_toolkit_context

    {% elif t == ''credential'' %}

    fetch_credential_context

    {% elif t == ''conversation'' %}

    fetch_conversation_context

    {% else %}

    unsupported_entity_type

    {% endif %}

    '
  default_output: unsupported_entity_type
  input:
  - entity_type
  routes:
  - fetch_application_context
  - fetch_toolkit_context
  - fetch_credential_context
  - fetch_conversation_context
  - unsupported_entity_type
- id: fetch_application_context
  type: code
  code:
    type: fixed
    value: "target_project_id = elitea_state.get('project_id', 0)\ntarget_entity_id = elitea_state.get('entity_id', 0)\ntarget_entity_type\
      \ = (elitea_state.get('entity_type', '') or '').lower()\ntarget_version_id = elitea_state.get('version_id', 0)\n\nSECRET_MARKERS\
      \ = {\n    'password', 'token', 'api_key', 'secret', 'client_secret',\n    'authorization', 'bearer', 'private_key',\
      \ 'access_token',\n    'refresh_token', 'webhook_secret', 'x-api-key', 'apikey',\n}\n\ndef redact(obj):\n    if isinstance(obj,\
      \ dict):\n        redacted = {}\n        for k, v in obj.items():\n            key = str(k).lower()\n            redacted[k]\
      \ = '***REDACTED***' if any(marker in key for marker in SECRET_MARKERS) else redact(v)\n        return redacted\n  \
      \  if isinstance(obj, list):\n        return [redact(x) for x in obj]\n    return obj\n\nresult = {\n    'project_id':\
      \ int(target_project_id) if target_project_id else 0,\n    'entity_id': int(target_entity_id) if target_entity_id else\
      \ 0,\n    'entity_type': target_entity_type,\n    'version_id': int(target_version_id) if target_version_id else 0,\n\
      \    'fetch_method': 'SandboxClient application version API',\n}\n\nif not target_project_id:\n    result['error'] =\
      \ 'project_id missing from UI context'\nelif not target_entity_id:\n    result['error'] = 'entity_id missing from UI\
      \ context'\nelif not int(target_version_id or 0):\n    result['error'] = 'version_id missing from UI context; refusing\
      \ to fetch full application configuration'\nelse:\n    try:\n        client = SandboxClient(\n            base_url=elitea_client.base_url,\n\
      \            project_id=int(target_project_id),\n            auth_token=elitea_client.auth_token,\n        )\n     \
      \   result['version_details'] = client.get_app_version_details(\n            int(target_entity_id),\n            int(target_version_id),\n\
      \        )\n    except Exception as e:\n        result['error'] = str(e)\n\n{'ui_context': redact(result)}\n"
  input:
  - entity_id
  - entity_type
  - version_id
  - project_id
  output:
  - ui_context
  structured_output: true
  transition: present_ui_context
- id: fetch_toolkit_context
  type: code
  code:
    type: fixed
    value: "import httpx\n\ntarget_project_id = elitea_state.get('project_id', 0)\ntarget_entity_id = elitea_state.get('entity_id',\
      \ 0)\ntarget_entity_type = (elitea_state.get('entity_type', '') or '').lower()\n\nSECRET_MARKERS = {\n    'password',\
      \ 'token', 'api_key', 'secret', 'client_secret',\n    'authorization', 'bearer', 'private_key', 'access_token',\n  \
      \  'refresh_token', 'webhook_secret', 'x-api-key', 'apikey',\n}\n\ndef redact(obj):\n    if isinstance(obj, dict):\n\
      \        redacted = {}\n        for k, v in obj.items():\n            key = str(k).lower()\n            redacted[k]\
      \ = '***REDACTED***' if any(marker in key for marker in SECRET_MARKERS) else redact(v)\n        return redacted\n  \
      \  if isinstance(obj, list):\n        return [redact(x) for x in obj]\n    return obj\n\nasync def response_payload(resp):\n\
      \    try:\n        payload = resp.json()\n    except Exception:\n        payload = {'raw': resp.text}\n    return payload\
      \ if resp.status_code < 400 else {\n        'error': payload,\n        'status_code': resp.status_code,\n    }\n\nresult\
      \ = {\n    'project_id': int(target_project_id) if target_project_id else 0,\n    'entity_id': int(target_entity_id)\
      \ if target_entity_id else 0,\n    'entity_type': target_entity_type,\n    'fetch_method': 'GET /api/v2/elitea_core/tool/prompt_lib/{project_id}/{toolkit_id}',\n\
      }\n\nif not target_project_id:\n    result['error'] = 'project_id missing from UI context'\nelif not target_entity_id:\n\
      \    result['error'] = 'entity_id missing from UI context'\nelse:\n    headers = {\n        'Authorization': f'Bearer\
      \ {elitea_client.auth_token}',\n        'Content-Type': 'application/json',\n    }\n    url = (\n        f\"{elitea_client.base_url.rstrip('/')}\"\
      \n        f\"/api/v2/elitea_core/tool/prompt_lib/{int(target_project_id)}/{int(target_entity_id)}\"\n    )\n    try:\n\
      \        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as http:\n            resp = await http.get(url,\
      \ headers=headers)\n        result['toolkit'] = await response_payload(resp)\n    except Exception as e:\n        result['error']\
      \ = str(e)\n\n{'ui_context': redact(result)}\n"
  input:
  - entity_id
  - entity_type
  - project_id
  output:
  - ui_context
  structured_output: true
  transition: present_ui_context
- id: fetch_credential_context
  type: code
  code:
    type: fixed
    value: "import httpx\n\ntarget_project_id = elitea_state.get('project_id', 0)\ntarget_entity_id = elitea_state.get('entity_id',\
      \ 0)\ntarget_entity_type = (elitea_state.get('entity_type', '') or '').lower()\n\nSECRET_MARKERS = {\n    'password',\
      \ 'token', 'api_key', 'secret', 'client_secret',\n    'authorization', 'bearer', 'private_key', 'access_token',\n  \
      \  'refresh_token', 'webhook_secret', 'x-api-key', 'apikey',\n}\n\ndef redact(obj):\n    if isinstance(obj, dict):\n\
      \        redacted = {}\n        for k, v in obj.items():\n            key = str(k).lower()\n            redacted[k]\
      \ = '***REDACTED***' if any(marker in key for marker in SECRET_MARKERS) else redact(v)\n        return redacted\n  \
      \  if isinstance(obj, list):\n        return [redact(x) for x in obj]\n    return obj\n\nasync def response_payload(resp):\n\
      \    try:\n        payload = resp.json()\n    except Exception:\n        payload = {'raw': resp.text}\n    return payload\
      \ if resp.status_code < 400 else {\n        'error': payload,\n        'status_code': resp.status_code,\n    }\n\nresult\
      \ = {\n    'project_id': int(target_project_id) if target_project_id else 0,\n    'entity_id': int(target_entity_id)\
      \ if target_entity_id else 0,\n    'entity_type': target_entity_type,\n    'fetch_method': 'GET /api/v1/configurations/configuration/{project_id}/{config_id}',\n\
      }\n\nif not target_project_id:\n    result['error'] = 'project_id missing from UI context'\nelif not target_entity_id:\n\
      \    result['error'] = 'entity_id missing from UI context'\nelse:\n    headers = {\n        'Authorization': f'Bearer\
      \ {elitea_client.auth_token}',\n        'Content-Type': 'application/json',\n    }\n    url = (\n        f\"{elitea_client.base_url.rstrip('/')}\"\
      \n        f\"/api/v1/configurations/configuration/{int(target_project_id)}/{int(target_entity_id)}\"\n    )\n    try:\n\
      \        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as http:\n            resp = await http.get(url,\
      \ headers=headers)\n        result['credential'] = await response_payload(resp)\n    except Exception as e:\n      \
      \  result['error'] = str(e)\n\n{'ui_context': redact(result)}\n"
  input:
  - entity_id
  - entity_type
  - project_id
  output:
  - ui_context
  structured_output: true
  transition: present_ui_context
- id: fetch_conversation_context
  type: code
  code:
    type: fixed
    value: "import httpx\n\ntarget_project_id = elitea_state.get('project_id', 0)\ntarget_entity_id = elitea_state.get('entity_id',\
      \ 0)\ntarget_entity_type = (elitea_state.get('entity_type', '') or '').lower()\n\nSECRET_MARKERS = {\n    'password',\
      \ 'token', 'api_key', 'secret', 'client_secret',\n    'authorization', 'bearer', 'private_key', 'access_token',\n  \
      \  'refresh_token', 'webhook_secret', 'x-api-key', 'apikey',\n}\n\ndef redact(obj):\n    if isinstance(obj, dict):\n\
      \        redacted = {}\n        for k, v in obj.items():\n            key = str(k).lower()\n            redacted[k]\
      \ = '***REDACTED***' if any(marker in key for marker in SECRET_MARKERS) else redact(v)\n        return redacted\n  \
      \  if isinstance(obj, list):\n        return [redact(x) for x in obj]\n    return obj\n\nasync def response_payload(resp):\n\
      \    try:\n        payload = resp.json()\n    except Exception:\n        payload = {'raw': resp.text}\n    return payload\
      \ if resp.status_code < 400 else {\n        'error': payload,\n        'status_code': resp.status_code,\n    }\n\nresult\
      \ = {\n    'project_id': int(target_project_id) if target_project_id else 0,\n    'entity_id': int(target_entity_id)\
      \ if target_entity_id else 0,\n    'entity_type': target_entity_type,\n    'fetch_method': 'GET conversation details\
      \ + messages APIs',\n}\n\nif not target_project_id:\n    result['error'] = 'project_id missing from UI context'\nelif\
      \ not target_entity_id:\n    result['error'] = 'entity_id missing from UI context'\nelse:\n    headers = {\n       \
      \ 'Authorization': f'Bearer {elitea_client.auth_token}',\n        'Content-Type': 'application/json',\n    }\n    base_url\
      \ = elitea_client.base_url.rstrip('/')\n    conversation_url = (\n        f\"{base_url}/api/v2/elitea_core/conversation/prompt_lib/\"\
      \n        f\"{int(target_project_id)}/{int(target_entity_id)}\"\n    )\n    messages_url = (\n        f\"{base_url}/api/v2/elitea_core/messages/prompt_lib/\"\
      \n        f\"{int(target_project_id)}/{int(target_entity_id)}\"\n    )\n    try:\n        async with httpx.AsyncClient(timeout=30,\
      \ follow_redirects=True) as http:\n            conversation_resp = await http.get(conversation_url, headers=headers)\n\
      \            messages_resp = await http.get(\n                messages_url,\n                headers=headers,\n    \
      \            params={\n                    'limit': 100,\n                    'offset': 0,\n                    'sort_by':\
      \ 'created_at',\n                    'sort_order': 'asc',\n                },\n            )\n        result['conversation']\
      \ = await response_payload(conversation_resp)\n        result['messages'] = await response_payload(messages_resp)\n\
      \    except Exception as e:\n        result['error'] = str(e)\n\n{'ui_context': redact(result)}\n"
  input:
  - entity_id
  - entity_type
  - project_id
  output:
  - ui_context
  structured_output: true
  transition: present_ui_context
- id: unsupported_entity_type
  type: code
  code:
    type: fixed
    value: "target_project_id = elitea_state.get('project_id', 0)\ntarget_entity_id = elitea_state.get('entity_id', 0)\ntarget_entity_type\
      \ = elitea_state.get('entity_type', '')\ntarget_version_id = elitea_state.get('version_id', 0)\n\n{'ui_context': {\n\
      \    'project_id': int(target_project_id) if target_project_id else 0,\n    'entity_id': int(target_entity_id) if target_entity_id\
      \ else 0,\n    'entity_type': target_entity_type,\n    'version_id': int(target_version_id) if target_version_id else\
      \ 0,\n    'error': f'Unsupported entity_type: {target_entity_type}',\n    'supported_entity_types': [\n        'agent',\
      \ 'pipeline', 'app', 'toolkit', 'mcp', 'credential', 'conversation',\n    ],\n}}\n"
  input:
  - entity_id
  - entity_type
  - project_id
  - version_id
  output:
  - ui_context
  structured_output: true
  transition: present_ui_context
- id: present_ui_context
  type: printer
  final_message: context
  input_mapping:
    printer:
      type: fstring
      value: 'ui_context: {ui_context}'
  transition: END
pipeline_settings:
  edges:
  - id: xy-edge__parse_ui_context_vars---route_by_entity_type
    data: {}
    type: custom
    source: parse_ui_context_vars
    target: route_by_entity_type
  - id: xy-edge__route_by_entity_type---fetch_application_context
    data: {}
    type: custom
    source: route_by_entity_type
    target: fetch_application_context
    sourceHandle: routerNode_routes
  - id: xy-edge__route_by_entity_type---fetch_toolkit_context
    data: {}
    type: custom
    source: route_by_entity_type
    target: fetch_toolkit_context
    sourceHandle: routerNode_routes
  - id: xy-edge__route_by_entity_type---fetch_credential_context
    data: {}
    type: custom
    source: route_by_entity_type
    target: fetch_credential_context
    sourceHandle: routerNode_routes
  - id: xy-edge__route_by_entity_type---fetch_conversation_context
    data: {}
    type: custom
    source: route_by_entity_type
    target: fetch_conversation_context
    sourceHandle: routerNode_routes
  - id: xy-edge__route_by_entity_type---unsupported_entity_type
    data: {}
    type: custom
    source: route_by_entity_type
    target: unsupported_entity_type
    sourceHandle: routerNode_routes
  - id: xy-edge__route_by_entity_typedefault_output---unsupported_entity_type
    data: {}
    type: custom
    source: route_by_entity_type
    target: unsupported_entity_type
    sourceHandle: routerNode_default_output
  - id: xy-edge__fetch_application_context---present_ui_context
    data: {}
    type: custom
    source: fetch_application_context
    target: present_ui_context
  - id: xy-edge__present_ui_context---EliteAPipelineEnd
    type: custom
    source: present_ui_context
    target: END
  - id: xy-edge__fetch_toolkit_context---present_ui_context
    data: {}
    type: custom
    source: fetch_toolkit_context
    target: present_ui_context
  - id: xy-edge__fetch_credential_context---present_ui_context
    data: {}
    type: custom
    source: fetch_credential_context
    target: present_ui_context
  - id: xy-edge__fetch_conversation_context---present_ui_context
    data: {}
    type: custom
    source: fetch_conversation_context
    target: present_ui_context
  - id: xy-edge__unsupported_entity_type---present_ui_context
    data: {}
    type: custom
    source: unsupported_entity_type
    target: present_ui_context
  nodes:
  - id: END
    data:
      label: End
    type: END
    measured:
      width: 460
      height: 44
    position:
      x: 2380
      y: 2950
  - id: parse_ui_context_vars
    data:
      label: parse_ui_context_vars
    type: llm
    measured:
      width: 460
      height: 770
    position:
      x: 60
      y: 60
  - id: route_by_entity_type
    data:
      label: route_by_entity_type
    type: router
    measured:
      width: 460
      height: 472
    position:
      x: 60
      y: 1080
  - id: fetch_application_context
    data:
      label: fetch_application_context
    type: code
    measured:
      width: 460
      height: 411
    position:
      x: 60
      y: 1802
  - id: present_ui_context
    data:
      label: present_ui_context
    type: printer
    measured:
      width: 460
      height: 237
    position:
      x: 2380
      y: 2463
  - id: fetch_toolkit_context
    data:
      label: fetch_toolkit_context
    type: code
    measured:
      width: 460
      height: 385
    position:
      x: 1220
      y: 1815
  - id: fetch_credential_context
    data:
      label: fetch_credential_context
    type: code
    measured:
      width: 460
      height: 385
    position:
      x: 2380
      y: 1815
  - id: fetch_conversation_context
    data:
      label: fetch_conversation_context
    type: code
    measured:
      width: 460
      height: 385
    position:
      x: 3540
      y: 1815
  - id: unsupported_entity_type
    data:
      label: unsupported_entity_type
    type: code
    measured:
      width: 460
      height: 411
    position:
      x: 4700
      y: 1802
  orientation: vertical
  layout_version: '1.0'
---

