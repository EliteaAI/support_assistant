# User Profile

**Display:** {first_name or username}
**User ID:** {user_id}
**Email:** {email or system_user@...}
**First Seen:** {YYYY-MM-DD}
**Last Seen:** {YYYY-MM-DD}

## Interaction History

- Total interactions: {n}
- Topics: {topic: count, topic: count}
- Outcomes: resolved {n}, corrected {n}, escalated {n}
- Avg corrections per session: {x}

## Context Signals

- Usual project: {project_name} ({project_id}, comma separated if multiple)
- Frequent screens: {e.g. "agent-detail: 3, pipeline-detail: 1, chat: 2"}
- Last page: {current_page}
- Last model: {model_name} / {provider}
- Browser: {navigator.userAgent}
- Skill signal: {beginner|intermediate|advanced}

## Entity History (last 5 asked-about)

| Date | Type | Name | ID | Version | Asks |
| --- | --- | --- | --- | --- | --- |
| {YYYY-MM-DD} | {agent\|pipeline\|toolkit\|mcp\|app\|credential\|conversation} | {entity_name} | {entity_id} | {version_id or blank} | {n} |

## Integration Portfolio

Integrations this user actively works with (inferred from questions):
- {e.g. "jira: 4 questions", "confluence: 2", "sharepoint: 1"}

## Role Signal

- Inferred role: {devops|developer|project-manager|admin|analyst|unknown}
- Basis: {e.g. "pipeline YAML questions", "project space requests", "Jira issue creation"}

## Environment

- Instance URL: {e.g. "next.elitea.ai" or specific client-hosted URL if mentioned}
- Deployment type: {saas|client-hosted|unknown}

## Known Error Fingerprints

Specific recurring errors or codes this user has encountered:
- {YYYY-MM-DD}: {error or symptom — e.g. "InternalSDKError 400 on Jira large results"}

## Communication Style

- Verbosity: {terse|detailed|mixed}
- Format preference: {code-first|explanation-first|step-by-step|unknown}
- Language: {e.g. "English", "Ukrainian", "Spanish"}

## Escalation History

- Bugs filed / escalated: {n}
- {YYYY-MM-DD}: {brief one-line description of issue escalated}

## Preferences Observed

- {e.g. "prefers YAML directly over explanation"}
- {e.g. "asks for step-by-step"}

## Open Issues

- {unresolved topic from prior session — {YYYY-MM-DD}}
