# Dev Output - Jira MCP Integration and Environment Configuration

## Phase

Development

## Changed Files

- `.env.example` - Updated `KEYCLOAK_PUBLIC_URL` to use `auth.salesmate.local:8081`
  hostname and added `JIRA_PERSONAL_TOKEN` placeholder
- `.github/ISSUE_TEMPLATE/config.yml` - Updated Jira project URL to
  `https://jira.critical.pt/browse/AIAPMMWP1`
- `.vscode/mcp.json` - Added MCP server config for `mcp-atlassian` Jira
  integration via `uvx`

## Commands Executed

None - configuration-only changes, no build or test commands required.

## Results

Pass - all changes are configuration and environment template updates with
no impact on compiled code or tests. Jira MCP integration is now available
via the `criticalJiraDc` server in VS Code.
