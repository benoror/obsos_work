# Google Calendar MCP Setup

Mode B (`/meeting` with no args) requires Google Calendar access via the `workspace-mcp` server.

## Configuration

Already handled — `calendar` is included in the `--tools` list in `.cursor/mcp.json` alongside `docs` and `drive`. Uses the same OAuth credentials.

If Calendar was removed, re-add it:

```json
"args": [
  "workspace-mcp",
  "--tools",
  "docs",
  "drive",
  "calendar"
]
```

## Re-authentication

The Calendar API requires the `https://www.googleapis.com/auth/calendar.readonly` scope. On first use after adding `calendar`, the MCP server will prompt for OAuth consent. Approve it once and credentials are cached.

## Troubleshooting

- **MCP not connecting**: Restart Cursor or reload MCP servers after changing `mcp.json`.
- **Permission denied**: Delete cached credentials and re-authenticate. Credentials are stored by `workspace-mcp` (check `~/.workspace-mcp/` or similar).
