---
created: 2026-02-28T18:00:00-06:00
---
# User Profile

This file is the single source of truth for the vault owner's identity. Skills, rules, and agents reference this instead of hardcoding user info.

## Identity

- **Full name**: Your Name
- **Short name**: Ben
- **Aliases**: "Your Name", "YourNick"
- **Email**: you@example.com
- **Vault person file**: `[[@Me]]`

## Location & Timezone

- **Location**: Your City, Country
- **Timezone**: `-06:00` (CST)
- **ISO format**: `YYYY-MM-DDTHH:MM:SS-06:00`

## AI Transcript Anonymization

Gemini and other AI transcript providers anonymize speakers by location. These patterns refer to the user:

- "someone in Your City"
- "someone in Mexico"
- "someone in [Your City/Country]"

## Agent Behavior

- When the user is the assignee of a task, **omit** the `[[@Name]]` prefix — leave it as just `- [ ] Description`.
- Do NOT create `[[@Ben]]` or `[[@Your Name]]` wikilinks — the user's own name doesn't need linking.
- References to the user in meeting transcripts should be treated as first-person context, not third-party.
