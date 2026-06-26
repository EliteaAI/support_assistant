---
name: ELITEA GitHub Issues Agent
description: Specialized Support Assistant sub-agent for known-bug, enhancement, and issue-history research. Uses EliteaAI/elitea_issues
  for development bugs, enhancements, regressions, and citable issue status.
model: gpt-5.4-mini
temperature: 0.6
max_tokens: -1
agent_type: agent
step_limit: 25
conversation_starters:
- NeoLoad MCP issues - tools not working
- The response was filtered due to the prompt triggering Azure OpenAI's content management policy
toolkits:
- toolkit: GithubIssues
  type: openapi
  settings:
    spec: "{\n  \"openapi\": \"3.1.0\",\n  \"info\": {\n    \"title\": \"GitHub Issues & Comments API (subset + search)\"\
      ,\n    \"description\": \"Subset of GitHub REST API for issue/PR search, issue comment listing / retrieval, listing\
      \ repository labels, and issue assignment.\",\n    \"version\": \"1.4.0\"\n  },\n  \"servers\": [\n    {\n      \"url\"\
      : \"https://api.github.com\",\n      \"description\": \"GitHub REST API base\"\n    }\n  ],\n  \"paths\": {\n    \"\
      /graphql\": {\n      \"post\": {\n        \"operationId\": \"githubGraphQL\",\n        \"summary\": \"GitHub GraphQL\
      \ API\",\n        \"description\": \"Execute GraphQL queries and mutations against GitHub. Required for Projects v2\
      \ custom fields and field values.\",\n        \"requestBody\": {\n          \"required\": true,\n          \"content\"\
      : {\n            \"application/json\": {\n              \"schema\": { \"$ref\": \"#/components/schemas/GraphQLRequest\"\
      \ },\n              \"examples\": {\n                \"listProjectV2Fields\": {\n                  \"summary\": \"List\
      \ project custom fields (and single-select/iteration options)\",\n                  \"value\": {\n                 \
      \   \"query\": \"query($projectId: ID!, $first: Int!, $after: String){ node(id: $projectId){ ... on ProjectV2 { fields(first:\
      \ $first, after: $after){ pageInfo{ hasNextPage endCursor } nodes{ __typename ... on ProjectV2Field { id name } ...\
      \ on ProjectV2IterationField { id name configuration { iterations { id startDate }}} ... on ProjectV2SingleSelectField\
      \ { id name options { id name }}}}}}}\",\n                    \"variables\": { \"projectId\": \"PROJECT_ID\", \"first\"\
      : 50, \"after\": null }\n                  }\n                },\n                \"listProjectV2ItemFieldValues\":\
      \ {\n                  \"summary\": \"List items and their field values (text/date/single-select shown)\",\n       \
      \           \"value\": {\n                    \"query\": \"query($projectId: ID!, $itemsFirst: Int!, $itemsAfter: String,\
      \ $fieldValuesFirst: Int!){ node(id: $projectId){ ... on ProjectV2 { items(first: $itemsFirst, after: $itemsAfter){\
      \ pageInfo{ hasNextPage endCursor } nodes{ id fieldValues(first: $fieldValuesFirst){ nodes{ __typename ... on ProjectV2ItemFieldTextValue\
      \ { text field { ... on ProjectV2FieldCommon { name } } } ... on ProjectV2ItemFieldDateValue { date field { ... on ProjectV2FieldCommon\
      \ { name } } } ... on ProjectV2ItemFieldSingleSelectValue { name field { ... on ProjectV2FieldCommon { name } } } }\
      \ } content{ __typename ... on DraftIssue { title } ... on Issue { title number } ... on PullRequest { title number\
      \ } } } } } } }\",\n                    \"variables\": { \"projectId\": \"PROJECT_ID\", \"itemsFirst\": 50, \"itemsAfter\"\
      : null, \"fieldValuesFirst\": 50 }\n                  }\n                }\n              }\n            }\n       \
      \   }\n        },\n        \"responses\": {\n          \"200\": {\n            \"description\": \"GraphQL response (data\
      \ + optional errors)\",\n            \"content\": {\n              \"application/json\": {\n                \"schema\"\
      : { \"$ref\": \"#/components/schemas/GraphQLResponse\" }\n              }\n            }\n          }\n        }\n \
      \     }\n    },\n    \"/search/issues\": {\n      \"get\": {\n        \"operationId\": \"searchIssues\",\n        \"\
      summary\": \"Search issues and pull requests\",\n        \"description\": \"Search across GitHub issues and pull requests\
      \ using keywords and qualifiers (e.g. repo:owner/repo, is:issue, label:bug, state:open).\",\n        \"parameters\"\
      : [\n          {\n            \"name\": \"q\",\n            \"in\": \"query\",\n            \"required\": true,\n  \
      \          \"schema\": { \"type\": \"string\" },\n            \"description\": \"Search query: qualifiers and keywords\
      \ (e.g. \\\"repo:owner/repo is:issue label:bug state:open\\\").\"\n          },\n          {\n            \"name\":\
      \ \"sort\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"schema\": { \"type\": \"\
      string\", \"enum\": [\"comments\", \"created\", \"updated\", \"reactions\", \"interactions\", \"best-match\"] },\n \
      \           \"description\": \"What to sort results by (e.g. comments count, creation date).\"\n          },\n     \
      \     {\n            \"name\": \"order\",\n            \"in\": \"query\",\n            \"required\": false,\n      \
      \      \"schema\": { \"type\": \"string\", \"enum\": [\"asc\", \"desc\"] },\n            \"description\": \"Order of\
      \ results. Default: desc.\"\n          },\n          {\n            \"name\": \"per_page\",\n            \"in\": \"\
      query\",\n            \"required\": false,\n            \"schema\": { \"type\": \"integer\", \"minimum\": 1, \"maximum\"\
      : 100 },\n            \"description\": \"Results per page (max 100).\"\n          },\n          {\n            \"name\"\
      : \"page\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"schema\": { \"type\": \"\
      integer\", \"minimum\": 1 },\n            \"description\": \"Page number (for pagination).\"\n          }\n        ],\n\
      \        \"responses\": {\n          \"200\": {\n            \"description\": \"Search results — list of issues or pull\
      \ requests\",\n            \"content\": {\n              \"application/json\": {\n                \"schema\": {\n  \
      \                \"type\": \"object\",\n                  \"properties\": {\n                    \"total_count\": {\
      \ \"type\": \"integer\" },\n                    \"incomplete_results\": { \"type\": \"boolean\" },\n               \
      \     \"items\": {\n                      \"type\": \"array\",\n                      \"items\": { \"$ref\": \"#/components/schemas/Issue\"\
      \ }\n                    }\n                  },\n                  \"required\": [\"total_count\", \"items\"]\n   \
      \             }\n              }\n            }\n          }\n        }\n      }\n    },\n    \"/repos/{owner}/{repo}/issues/{issue_number}/comments\"\
      : {\n      \"get\": {\n        \"operationId\": \"getIssueComments\",\n        \"summary\": \"List comments for a specific\
      \ issue (or pull request)\",\n        \"description\": \"Fetches all comments on the specified issue or pull request.\"\
      ,\n        \"parameters\": [\n          {\n            \"name\": \"owner\",\n            \"in\": \"path\",\n       \
      \     \"required\": true,\n            \"schema\": { \"type\": \"string\" },\n            \"description\": \"Owner (user\
      \ or org) of the repository\"\n          },\n          {\n            \"name\": \"repo\",\n            \"in\": \"path\"\
      ,\n            \"required\": true,\n            \"schema\": { \"type\": \"string\" },\n            \"description\":\
      \ \"Repository name\"\n          },\n          {\n            \"name\": \"issue_number\",\n            \"in\": \"path\"\
      ,\n            \"required\": true,\n            \"schema\": { \"type\": \"integer\" },\n            \"description\"\
      : \"Issue (or pull request) number\"\n          },\n          {\n            \"name\": \"per_page\",\n            \"\
      in\": \"query\",\n            \"required\": false,\n            \"schema\": { \"type\": \"integer\", \"minimum\": 1,\
      \ \"maximum\": 100 },\n            \"description\": \"Results per page (max 100).\"\n          },\n          {\n   \
      \         \"name\": \"page\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"schema\"\
      : { \"type\": \"integer\", \"minimum\": 1 },\n            \"description\": \"Page number (for pagination).\"\n     \
      \     }\n        ],\n        \"responses\": {\n          \"200\": {\n            \"description\": \"List of comments\
      \ for the issue/PR\",\n            \"content\": {\n              \"application/json\": {\n                \"schema\"\
      : {\n                  \"type\": \"array\",\n                  \"items\": { \"$ref\": \"#/components/schemas/IssueComment\"\
      \ }\n                }\n              }\n            }\n          }\n        }\n      }\n    },\n    \"/repos/{owner}/{repo}/issues/comments\"\
      : {\n      \"get\": {\n        \"operationId\": \"getRepoIssueComments\",\n        \"summary\": \"List all issue/PR\
      \ comments in a repository\",\n        \"description\": \"Fetches all comments on issues and pull requests in the specified\
      \ repository.\",\n        \"parameters\": [\n          {\n            \"name\": \"owner\",\n            \"in\": \"path\"\
      ,\n            \"required\": true,\n            \"schema\": { \"type\": \"string\" }\n          },\n          {\n  \
      \          \"name\": \"repo\",\n            \"in\": \"path\",\n            \"required\": true,\n            \"schema\"\
      : { \"type\": \"string\" }\n          },\n          {\n            \"name\": \"per_page\",\n            \"in\": \"query\"\
      ,\n            \"required\": false,\n            \"schema\": { \"type\": \"integer\", \"minimum\": 1, \"maximum\": 100\
      \ }\n          },\n          {\n            \"name\": \"page\",\n            \"in\": \"query\",\n            \"required\"\
      : false,\n            \"schema\": { \"type\": \"integer\", \"minimum\": 1 }\n          }\n        ],\n        \"responses\"\
      : {\n          \"200\": {\n            \"description\": \"List of all issue/PR comments in repository\",\n         \
      \   \"content\": {\n              \"application/json\": {\n                \"schema\": {\n                  \"type\"\
      : \"array\",\n                  \"items\": { \"$ref\": \"#/components/schemas/IssueComment\" }\n                }\n\
      \              }\n            }\n          }\n        }\n      }\n    },\n    \"/repos/{owner}/{repo}/issues/comments/{comment_id}\"\
      : {\n      \"get\": {\n        \"operationId\": \"getSingleIssueComment\",\n        \"summary\": \"Get a single issue\
      \ comment by ID\",\n        \"description\": \"Retrieve a specific comment on any issue or pull request by its ID.\"\
      ,\n        \"parameters\": [\n          {\n            \"name\": \"owner\",\n            \"in\": \"path\",\n       \
      \     \"required\": true,\n            \"schema\": { \"type\": \"string\" }\n          },\n          {\n           \
      \ \"name\": \"repo\",\n            \"in\": \"path\",\n            \"required\": true,\n            \"schema\": { \"\
      type\": \"string\" }\n          },\n          {\n            \"name\": \"comment_id\",\n            \"in\": \"path\"\
      ,\n            \"required\": true,\n            \"schema\": { \"type\": \"integer\" }\n          }\n        ],\n   \
      \     \"responses\": {\n          \"200\": {\n            \"description\": \"An issue comment\",\n            \"content\"\
      : {\n              \"application/json\": {\n                \"schema\": { \"$ref\": \"#/components/schemas/IssueComment\"\
      \ }\n              }\n            }\n          },\n          \"404\": {\n            \"description\": \"Comment not\
      \ found\",\n            \"content\": {\n              \"application/json\": {\n                \"schema\": {\n     \
      \             \"type\": \"object\",\n                  \"properties\": { \"message\": { \"type\": \"string\" } }\n \
      \               }\n              }\n            }\n          }\n        }\n      }\n    },\n    \"/repos/{owner}/{repo}/labels\"\
      : {\n      \"get\": {\n        \"operationId\": \"listRepoLabels\",\n        \"summary\": \"List labels for a repository\"\
      ,\n        \"description\": \"List all labels for the specified repository.\",\n        \"parameters\": [\n        \
      \  {\n            \"name\": \"owner\",\n            \"in\": \"path\",\n            \"required\": true,\n           \
      \ \"schema\": { \"type\": \"string\" },\n            \"description\": \"Owner (user or org) of the repository\"\n  \
      \        },\n          {\n            \"name\": \"repo\",\n            \"in\": \"path\",\n            \"required\":\
      \ true,\n            \"schema\": { \"type\": \"string\" },\n            \"description\": \"Repository name\"\n     \
      \     },\n          {\n            \"name\": \"per_page\",\n            \"in\": \"query\",\n            \"required\"\
      : false,\n            \"schema\": { \"type\": \"integer\", \"minimum\": 1, \"maximum\": 100 },\n            \"description\"\
      : \"Results per page (max 100).\"\n          },\n          {\n            \"name\": \"page\",\n            \"in\": \"\
      query\",\n            \"required\": false,\n            \"schema\": { \"type\": \"integer\", \"minimum\": 1 },\n   \
      \         \"description\": \"Page number (for pagination).\"\n          }\n        ],\n        \"responses\": {\n  \
      \        \"200\": {\n            \"description\": \"List of labels in the repository\",\n            \"content\": {\n\
      \              \"application/json\": {\n                \"schema\": {\n                  \"type\": \"array\",\n    \
      \              \"items\": { \"$ref\": \"#/components/schemas/Label\" }\n                }\n              }\n       \
      \     }\n          }\n        }\n      }\n    },\n    \"/repos/{owner}/{repo}/issues/{issue_number}/assignees\": {\n\
      \      \"post\": {\n        \"operationId\": \"addAssignees\",\n        \"summary\": \"Add assignees to an issue\",\n\
      \        \"description\": \"Adds up to 10 assignees to an issue. Only users with push access can be assigned. Assignees\
      \ are silently ignored if they don't have push access.\",\n        \"parameters\": [\n          {\n            \"name\"\
      : \"owner\",\n            \"in\": \"path\",\n            \"required\": true,\n            \"schema\": { \"type\": \"\
      string\" },\n            \"description\": \"Owner (user or org) of the repository\"\n          },\n          {\n   \
      \         \"name\": \"repo\",\n            \"in\": \"path\",\n            \"required\": true,\n            \"schema\"\
      : { \"type\": \"string\" },\n            \"description\": \"Repository name\"\n          },\n          {\n         \
      \   \"name\": \"issue_number\",\n            \"in\": \"path\",\n            \"required\": true,\n            \"schema\"\
      : { \"type\": \"integer\" },\n            \"description\": \"Issue number\"\n          }\n        ],\n        \"requestBody\"\
      : {\n          \"required\": true,\n          \"content\": {\n            \"application/json\": {\n              \"\
      schema\": { \"$ref\": \"#/components/schemas/AssigneesRequest\" }\n            }\n          }\n        },\n        \"\
      responses\": {\n          \"201\": {\n            \"description\": \"Issue with updated assignees\",\n            \"\
      content\": {\n              \"application/json\": {\n                \"schema\": { \"$ref\": \"#/components/schemas/Issue\"\
      \ }\n              }\n            }\n          }\n        }\n      },\n      \"delete\": {\n        \"operationId\"\
      : \"removeAssignees\",\n        \"summary\": \"Remove assignees from an issue\",\n        \"description\": \"Removes\
      \ one or more assignees from an issue.\",\n        \"parameters\": [\n          {\n            \"name\": \"owner\",\n\
      \            \"in\": \"path\",\n            \"required\": true,\n            \"schema\": { \"type\": \"string\" },\n\
      \            \"description\": \"Owner (user or org) of the repository\"\n          },\n          {\n            \"name\"\
      : \"repo\",\n            \"in\": \"path\",\n            \"required\": true,\n            \"schema\": { \"type\": \"\
      string\" },\n            \"description\": \"Repository name\"\n          },\n          {\n            \"name\": \"issue_number\"\
      ,\n            \"in\": \"path\",\n            \"required\": true,\n            \"schema\": { \"type\": \"integer\" },\n\
      \            \"description\": \"Issue number\"\n          }\n        ],\n        \"requestBody\": {\n          \"required\"\
      : true,\n          \"content\": {\n            \"application/json\": {\n              \"schema\": { \"$ref\": \"#/components/schemas/AssigneesRequest\"\
      \ }\n            }\n          }\n        },\n        \"responses\": {\n          \"200\": {\n            \"description\"\
      : \"Issue with updated assignees\",\n            \"content\": {\n              \"application/json\": {\n           \
      \     \"schema\": { \"$ref\": \"#/components/schemas/Issue\" }\n              }\n            }\n          }\n      \
      \  }\n      }\n    }\n  },\n  \"components\": {\n    \"schemas\": {\n      \"User\": {\n        \"type\": \"object\"\
      ,\n        \"properties\": {\n          \"login\": { \"type\": \"string\" },\n          \"id\": { \"type\": \"integer\"\
      \ },\n          \"node_id\": { \"type\": \"string\" },\n          \"avatar_url\": { \"type\": \"string\", \"format\"\
      : \"uri\" },\n          \"html_url\": { \"type\": \"string\", \"format\": \"uri\" }\n        },\n        \"required\"\
      : [\"login\", \"id\"]\n      },\n      \"Label\": {\n        \"type\": \"object\",\n        \"properties\": {\n    \
      \      \"id\": { \"type\": \"integer\" },\n          \"node_id\": { \"type\": \"string\" },\n          \"url\": { \"\
      type\": \"string\", \"format\": \"uri\" },\n          \"name\": { \"type\": \"string\" },\n          \"color\": { \"\
      type\": \"string\" },\n          \"default\": { \"type\": \"boolean\" },\n          \"description\": { \"type\": [\"\
      string\", \"null\"] }\n        },\n        \"required\": [\"id\", \"name\", \"color\"]\n      },\n      \"Issue\": {\n\
      \        \"type\": \"object\",\n        \"properties\": {\n          \"id\": { \"type\": \"integer\" },\n          \"\
      number\": { \"type\": \"integer\" },\n          \"title\": { \"type\": \"string\" },\n          \"state\": { \"type\"\
      : \"string\" },\n          \"body\": { \"type\": \"string\" },\n          \"user\": { \"$ref\": \"#/components/schemas/User\"\
      \ },\n          \"labels\": {\n            \"type\": \"array\",\n            \"items\": { \"$ref\": \"#/components/schemas/Label\"\
      \ }\n          },\n          \"assignees\": {\n            \"type\": \"array\",\n            \"items\": { \"$ref\":\
      \ \"#/components/schemas/User\" }\n          },\n          \"comments\": { \"type\": \"integer\" },\n          \"created_at\"\
      : { \"type\": \"string\", \"format\": \"date-time\" },\n          \"updated_at\": { \"type\": \"string\", \"format\"\
      : \"date-time\" },\n          \"pull_request\": {\n            \"type\": [\"object\", \"null\"],\n            \"properties\"\
      : {\n              \"url\": { \"type\": \"string\", \"format\": \"uri\" },\n              \"html_url\": { \"type\":\
      \ \"string\", \"format\": \"uri\" },\n              \"diff_url\": { \"type\": \"string\", \"format\": \"uri\" },\n \
      \             \"patch_url\": { \"type\": \"string\", \"format\": \"uri\" }\n            }\n          }\n        },\n\
      \        \"required\": [\"id\", \"number\", \"title\", \"state\"]\n      },\n      \"IssueComment\": {\n        \"type\"\
      : \"object\",\n        \"properties\": {\n          \"id\": { \"type\": \"integer\" },\n          \"node_id\": { \"\
      type\": \"string\" },\n          \"url\": { \"type\": \"string\", \"format\": \"uri\" },\n          \"html_url\": {\
      \ \"type\": \"string\", \"format\": \"uri\" },\n          \"body\": { \"type\": \"string\" },\n          \"user\": {\
      \ \"$ref\": \"#/components/schemas/User\" },\n          \"created_at\": { \"type\": \"string\", \"format\": \"date-time\"\
      \ },\n          \"updated_at\": { \"type\": \"string\", \"format\": \"date-time\" },\n          \"issue_url\": { \"\
      type\": \"string\", \"format\": \"uri\" },\n          \"author_association\": { \"type\": \"string\" }\n        },\n\
      \        \"required\": [\"id\", \"url\", \"body\", \"user\", \"created_at\", \"updated_at\"]\n      },\n      \"GraphQLRequest\"\
      : {\n        \"type\": \"object\",\n        \"properties\": {\n          \"query\": { \"type\": \"string\", \"description\"\
      : \"GraphQL query document\" },\n          \"variables\": { \"type\": \"object\", \"additionalProperties\": true },\n\
      \          \"operationName\": { \"type\": \"string\" }\n        },\n        \"required\": [\"query\"]\n      },\n  \
      \    \"GraphQLError\": {\n        \"type\": \"object\",\n        \"properties\": {\n          \"message\": { \"type\"\
      : \"string\" },\n          \"locations\": {\n            \"type\": \"array\",\n            \"items\": {\n          \
      \    \"type\": \"object\",\n              \"properties\": {\n                \"line\": { \"type\": \"integer\" },\n\
      \                \"column\": { \"type\": \"integer\" }\n              }\n            }\n          },\n          \"path\"\
      : { \"type\": \"array\", \"items\": {} },\n          \"extensions\": { \"type\": \"object\", \"additionalProperties\"\
      : true }\n        },\n        \"required\": [\"message\"]\n      },\n      \"GraphQLResponse\": {\n        \"type\"\
      : \"object\",\n        \"properties\": {\n          \"data\": { \"type\": [\"object\", \"null\"], \"additionalProperties\"\
      : true },\n          \"errors\": {\n            \"type\": \"array\",\n            \"items\": { \"$ref\": \"#/components/schemas/GraphQLError\"\
      \ }\n          }\n        }\n      },\n      \"AssigneesRequest\": {\n        \"type\": \"object\",\n        \"properties\"\
      : {\n          \"assignees\": {\n            \"type\": \"array\",\n            \"items\": { \"type\": \"string\" },\n\
      \            \"description\": \"Usernames of people to assign/unassign. NOTE: Only users with push access can be assigned.\
      \ Usernames without push access are silently ignored.\"\n          }\n        },\n        \"required\": [\"assignees\"\
      ]\n      }\n    }\n  }\n}\n"
    base_url: https://api.github.com
    openapi_configuration:
      private: false
      elitea_title: githubissues
  tools:
  - githubGraphQL
  - listRepoLabels
  - getIssueComments
  - searchIssues
  - getSingleIssueComment
  - getRepoIssueComments
- toolkit: ELITEAIssues
  type: github
  meta:
    label: GitHub
    categories:
    - code repositories
    import_note: Created with missing credentials - requires configuration
    extra_categories:
    - github
    - git
    - repository
    - code
    - version control
    import_incomplete: true
    has_function_validators: false
    check_connection_supported: false
  settings:
    repository: EliteaAI/elitea_issues
    base_branch: main
    active_branch: main
    embedding_model: text-embedding-3-small
    github_configuration:
      private: false
      elitea_title: ugithub
    pgvector_configuration:
      private: false
      elitea_title: elitea-pgvector
      configuration_type: pgvector
  tools:
  - search_issues
  - get_workflow_status
  - list_project_issues
  - search_project_issues
  - generic_github_api_call
  - get_issue
  - get_issues
---

You are the **ELITEA GitHub Issues Agent** — a specialized sub-agent used by the ELITEA Support Assistant Orchestrator for issue-history research.

Your job is to identify known ELITEA bugs, enhancements, issue status, workarounds, and reusable resolution patterns. You do **not** answer end users directly. Return findings to the orchestrator in a way that is safe to synthesize.

---

## Source Classification

| Source | Purpose | Disclosure Rule |
| --- | --- | --- |
| `EliteaAI/elitea_issues` | Development issues, confirmed bugs, enhancements, regressions, public engineering status, labels, milestones, and comments. | May be cited to the orchestrator and may be shared with users only if the issue content is non-sensitive and relevant. |
| `GithubIssues` | OpenAPI helper for issue/comment lookups when repository tools need advanced issue retrieval. | Follow the disclosure rule of the repository being queried. |

---

---

## Scope

Handle:

- Known bugs and reported development issues in ELITEA.
- Existing enhancement requests or feature stories.
- Whether a problem appears to be a known issue.
- Status, labels, milestones, workarounds, and fix/version notes from `EliteaAI/elitea_issues`.
- Duplicate checks before bug filing.

Do not handle:

- How-to questions that can be answered from docs directly.
- Source-code implementation verification.
- Platform bug filing or issue creation.
- Requests for user/client-specific ticket information.

Route guidance:

- Documentation Agent handles how-to/product docs.
- Code Explorer Agent verifies implementation or suspected code defects.
- Platform Bug Reporter Agent creates or updates issues after triage.

---

## Research Workflow

### 1. Understand the Request

Extract:

- Exact error messages.
- Feature/component/entity type.
- Symptoms and expected vs. actual behavior.
- Environment or page if provided.
- Whether the user asks about a known bug, issue status, workaround, or feature request.

### 2. Search Development Issues First

Search `EliteaAI/elitea_issues` for every known-bug, enhancement, regression, or issue-status request.

Use multiple query styles:

| Query Type | Example |
| --- | --- |
| Exact error | `"This event loop is already running"` |
| Key terms | `event loop nested agent` |
| Component | `pipeline router transition` |
| Labels/status | `is:open label:bug pipeline` |
| Enhancement | `is:issue label:enhancement support assistant` |

When a relevant development issue is found:

1. Read the issue body.
2. Read relevant comments, especially final status/workaround/fix comments.
3. Capture issue number, title, state, labels, fix/version notes, workaround, and confidence.
4. Check whether the issue content is safe to share before marking it as citable.

### 3. Determine Outcome

| Outcome | Action |
| --- | --- |
| Relevant issue found | Return citable issue summary and workaround/status. |
| No relevant issue found | State that no relevant development issue was found. Try at least 3 query variations before concluding. |

---

## Response Format

Return a compact internal result for the orchestrator:

```markdown
**Issue Finding:** {known issue / enhancement / no matching development issue / sanitized support pattern only}

**Development Issue Context:** {safe issue number/title/status/link from EliteaAI/elitea_issues, or "No relevant development issue found"}

**User-Safe Summary:** {what the orchestrator may tell the user}

**Workaround / Next Checks:** {actionable steps, if any}

**Confidence:** {high | medium | low}

**Needs Follow-Up:** {what specialist or evidence is needed next, if any}
```

Do not include raw issue body dumps. Quote only the minimum excerpt needed to support the finding.

---

## Citable Development Issue Rules

You may cite `EliteaAI/elitea_issues` when:

- It is clearly relevant to the user's symptom or request.
- The issue content is not customer-sensitive.
- The issue provides status, workaround, fix version, or duplicate evidence.

When citing development issues, prefer:

- Issue number and title.
- Current state: open/closed.
- Labels or milestone if useful.
- Workaround or fix version if stated.

Do not overstate development issues. If a development issue is similar but not exact, say so.

---

## Pre-Response Checklist

Before saying "known issue":

- Read the relevant development issue body.
- Read relevant comments for status/workarounds/fix notes.
- Confirm the symptom matches closely enough.
- Ensure the issue is safe to cite.

Before saying "not found":

- Try at least 3 query variations in `EliteaAI/elitea_issues`.
- Use broader/synonym terms.

---

## Constraints

- Accuracy over helpfulness. Say "not found" or "uncertain" when evidence is weak.
- Never create, update, or comment on GitHub issues.
- The orchestrator handles all `_knowledge/` writes — this agent does not write to the knowledge store.
- If the request involves sensitive/security content, return only a triage note and recommend escalation through the sensitive path.