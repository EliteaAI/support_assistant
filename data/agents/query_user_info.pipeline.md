---
name: query_user_info
description: access the current user details such as "name", "email", and "personal project id"
model: gpt-5.4-mini
temperature: 0.6
max_tokens: -1
agent_type: pipeline
step_limit: 25
state:
  input:
    type: str
  messages:
    type: list
  user_info:
    type: str
    value: ''
entry_point: fetch_user_details
nodes:
- id: fetch_user_details
  type: code
  code:
    type: fixed
    value: 'user_info = elitea_client.get_user_data()

      user_info'
  input: []
  output:
  - user_info
  structured_output: true
  transition: Printer 1
- id: Printer 1
  type: printer
  final_message: User details
  input_mapping:
    printer:
      type: variable
      value: user_info
  transition: END
pipeline_settings:
  edges:
  - id: xy-edge__fetch_user_details---Printer 1
    data: {}
    type: custom
    source: fetch_user_details
    target: Printer 1
  - id: xy-edge__Printer 1---EliteAPipelineEnd
    type: custom
    source: Printer 1
    target: END
  nodes:
  - id: END
    data:
      label: End
    type: END
    measured:
      width: 460
      height: 44
    position:
      x: 60
      y: 1268
  - id: fetch_user_details
    data:
      label: fetch_user_details
    type: code
    measured:
      width: 460
      height: 471
    position:
      x: 60
      y: 60
  - id: Printer 1
    data:
      label: Printer 1
    type: printer
    measured:
      width: 460
      height: 237
    position:
      x: 60
      y: 781
  orientation: vertical
  layout_version: '1.0'
---

