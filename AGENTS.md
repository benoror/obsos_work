# Agents

This is an Obsidian vault managed by Your Name. AI agents working in this repo should be aware of the following structure and conventions.

## Skills

Custom Cursor skills live in `.cursor/skills/`. Each has a `SKILL.md` with usage, workflow, and conventions.

| Skill | Slash command | What it does |
|-------|--------------|--------------|
| [meeting](.cursor/skills/meeting/SKILL.md) | `/meeting` | Create meeting notes (manual title or Google Calendar picker) |
| [cache-notes](.cursor/skills/cache-notes/SKILL.md) | `/cache-notes` | Fetch external AI transcripts (Gemini, Otter) and cache as Obsidian callouts |
| [fill-participants](.cursor/skills/fill-participants/SKILL.md) | `/fill-participants` | Resolve and fill `Participants:` frontmatter from Google Docs / filename / context |
| [followup-todos](.cursor/skills/followup-todos/SKILL.md) | `/followup-todos` | Extract action items from notes & AI transcripts into Obsidian Tasks checkboxes |
| [commit](.cursor/skills/commit/SKILL.md) | `/commit` | Shared final step — stage modified files and commit with user confirmation |

## Rules

Cursor rules in `.cursor/rules/` are auto-injected based on glob patterns.

| Rule | Applies to | Purpose |
|------|-----------|---------|
| [skill-conventions](.cursor/rules/skill-conventions.mdc) | `.cursor/skills/**` | Enforces skill structure, commit step, Obsidian Tasks priorities, and project context |
| [skill-registry](.cursor/rules/skill-registry.mdc) | `.cursor/skills/*/SKILL.md` | Keeps skill tables in `skill-conventions.mdc` and `AGENTS.md` in sync when skills change |

## Vault Layout

```
Meetings/              Meeting notes by subfolder (PAM/, TBs/, Eng/, etc.)
Templates/             Obsidian templates
Teams/People/          Person files: @Name.md
Teams/                 Team files: +TeamName.md
ToDo's.md              Aggregated Tasks plugin view
Tracker.md             Project tracker
```

## Conventions

- **Frontmatter**: YAML between `---` fences. `modified:` is managed by Obsidian — never set manually.
- **Participants**: `[[@Name]]` wikilinks (people) or `[[+Team]]` (teams).
- **AI Transcripts**: Cached under `## 🤖 AI Notes` with provider subheadings and collapsible callouts (`[!gemini_notes]-`, `[!gemini_todos]-`, `[!gemini_transcript]-`).
- **Tasks priorities**: 🔺 highest, ⏫ high, 🔼 medium, 🔽 low.
- **Timezone**: `-06:00` (CST).
- **User**: Your Name / "Ben".

## MCP Servers

Configured in [.cursor/mcp.json](.cursor/mcp.json). Provides Google Workspace tools (Docs, Drive, Calendar).
