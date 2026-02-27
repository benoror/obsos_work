---
name: followup-todos
description: Extracts actionable follow-up items from a meeting's cached AI transcript and proposes them as Obsidian todo checkboxes. Filters by relevance, assigns owners, and suggests priorities. Use when the user says /followup-todos or asks to extract action items or todos from a meeting.
---

# Follow-up Todos

## Usage

- `/followup-todos <path>` — Extract and propose todos from a specific meeting note.
- `/followup-todos` (no args) — Let the user pick a recent meeting.

## Prerequisites

The meeting file should ideally have cached AI transcripts (from `/cache-notes`). If not cached, suggest running `/cache-notes <path>` first. However, the skill also works on notes with only manual content.

## Obsidian Tasks Format

Todos use the [Obsidian Tasks](https://publish.obsidian.md/tasks/) plugin syntax. A full task line looks like:

```markdown
- [ ] [[@Assignee]] Description 🔼 🛫 2026-03-01 📅 2026-03-07 🔁 every week
```

### Checkbox states

| State | Syntax | Meaning |
|-------|--------|---------|
| Open | `- [ ]` | Not started |
| Done | `- [x]` | Completed (append `✅ YYYY-MM-DD`) |
| In progress | `- [/]` | Started |
| Cancelled | `- [-]` | Cancelled (append `❌ YYYY-MM-DD`) |

### Task components (recommended order)

| Element | Emoji | Format | Required |
|---------|-------|--------|----------|
| Checkbox | — | `- [*]` | Yes |
| Assignee | — | `[[@Name]]` wikilink prefix | If not the user |
| Description | — | Free text | Yes |
| Priority | `🔺⏫🔼🔽` | After description | Optional |
| Created date | `➕` | `➕ YYYY-MM-DD` | Optional (auto-set if desired) |
| Start date | `🛫` | `🛫 YYYY-MM-DD` — earliest date to begin work | Optional |
| Scheduled date | `⏳` | `⏳ YYYY-MM-DD` — date planned to work on it | Optional |
| Due date | `📅` | `📅 YYYY-MM-DD` — hard deadline | Optional |
| Done date | `✅` | `✅ YYYY-MM-DD` | When completing |
| Cancelled date | `❌` | `❌ YYYY-MM-DD` | When cancelling |
| Recurrence | `🔁` | `🔁 every <interval>` (e.g. `every week`, `every month on the 1st`) | Optional |

### Priorities

```
🔺 Highest — blocking, deadline this week, critical path
⏫ High    — important but not urgent, next sprint
🔼 Medium  — moderate urgency
🔽 Low     — low urgency
```

### Date inference

When extracting todos, infer dates from meeting context:

| Phrase | Maps to |
|--------|---------|
| "today", "end of day" | `📅` = meeting date |
| "tomorrow" | `📅` = meeting date + 1 |
| "by Friday", "end of week" | `📅` = that Friday |
| "Monday", "next week" | `📅` = next Monday |
| "next sprint" | `🛫` = next sprint start (if known) |
| "start working on X" | `🛫` = inferred start date |
| "schedule for <date>" | `📅` = that date |

When in doubt, include the date in the proposal table (Step 3) and let the user confirm.

### Nested sub-tasks

Use tab indentation:

```markdown
- [ ] Main task 🔼
	- [ ] Sub-task 1
	- [ ] Sub-task 2
```

## Workflow

### Step 1: Read the meeting note

Read the entire file. Extract action items from **all** content sources, skipping only existing `- [ ]` / `- [x]` todo lines:

1. **Manual notes** (between frontmatter `---` and `## AI Transcripts`): The user may have jotted down action items, commitments, or follow-ups during the meeting as free text (e.g. "- Talk to Chris about X", "Need to review Y"). These are first-class sources. Skip lines that are already checkboxes (`- [*]` — any single character between brackets).
2. **`[!gemini_todos]` callout**: Gemini's "Suggested Next Steps" — explicit action items.
3. **`[!gemini_notes]` callout**: Summary & Details — scan for implicit commitments ("will do X", "agreed to Y", "plans to Z").
4. **Other provider callouts** (`[!otter_todos]`, etc.): Same treatment as Gemini.

Also extract:
- Existing todos matching `- [*]` pattern (any checkbox state) to avoid duplicates
- `Participants:` from frontmatter (to resolve assignees)
- Meeting date (from filename or `created:` frontmatter)

### Step 2: Classify each action item

For each candidate action item (from manual notes, transcript todos, or implicit commitments in details), determine:

1. **Owner**: Who is responsible? Map names to `[[@Name]]` wikilinks using `Teams/People/` files.
   - If the owner is the user (Your Name / "Ben"), omit the assignee prefix.
   - If the owner is "someone in [location]" (Gemini anonymization), try to resolve from context or Participants.
   - If the owner is someone else, prefix with `[[@Name]]`.

2. **Relevance**: Score as `high`, `medium`, or `skip`:
   - **High**: Action is for the user, has a clear deliverable, or is time-sensitive.
   - **Medium**: Action is for someone else but the user should track it, or it's vague but potentially important.
   - **Skip**: Purely informational, already completed (based on date vs today), or not actionable.

3. **Priority**: Based on urgency and impact:
   - `🔺` — Blocking others, deadline this week, or critical path.
   - `⏫` — Important but not urgent, next sprint.
   - `🔼` — Moderate urgency, nice-to-have.
   - `🔽` — Low urgency.

4. **Dates**: Infer from meeting context using the date inference table above. Assign `📅` (due), `🛫` (start), or `⏳` (scheduled) as appropriate. Omit if no date is mentioned or inferable.

### Step 3: Present proposals to the user — MANDATORY CONFIRMATION

**⚠️ STOP HERE AND WAIT FOR USER CONFIRMATION. Never skip this step, even during `/meeting wrap` sequences. Do NOT write todos to the file until the user explicitly approves.**

Display a numbered table:

```
| # | Add? | Todo | Owner | Priority | Due 📅 | Start 🛫 | Scheduled ⏳ |
|---|------|------|-------|----------|--------|----------|--------------|
| 1 | ✅   | Talk with Chris about temp environments | Me | 🔼 | — | — | — |
| 2 | ✅   | Offload data lake work to Rob | Me | ⏫ | — | — | — |
| 3 | ⬜   | Confirm travel plans for Friday | @Zak | — | 2026-02-28 | — | — |
| 4 | ⬜   | Verify Vtor's prod hash deployed | Me | 🔼 | 2026-02-24 | — | — |
```

- Default `✅` for high-relevance items owned by the user.
- Default `⬜` for others' items or skippable ones.
- Let the user toggle by saying numbers (e.g. "1,3,4" or "all" or "none except 2").

### Step 4: Insert confirmed todos

**Only proceed after the user has explicitly confirmed which todos to include (Step 3).**

Insert the confirmed todos into the note body. Placement depends on the note's template:

#### Daily Standup notes (`Meetings/*/Scrum/YYYY-MM-DD.md`)

These follow the [Daily Standup template](../../Templates/Daily%20Standup.md):

```
Yesterday
- ...
Today
- ...          ← INSERT TODOS HERE (append after existing Today items)
Blockers
- ...
---
Pending/Carry-over Backlog
- ...
```

Insert todos at the **end of the "Today" section**, just before the `Blockers` line. Use `StrReplace` targeting `Blockers` as the anchor.

#### Other meeting notes

Insert after any existing user content but before `## 🤖 AI Notes` (or `## AI Transcripts`). If neither heading exists, append after the frontmatter closing `---`. Use `StrReplace` targeting the heading as the anchor.

#### General rules

- Group by owner if multiple people are involved.
- Preserve existing content in the section — always append, never overwrite.

### Step 5: Mark as processed

After inserting, add a `TodosExtracted: YYYY-MM-DDTHH:MM:SS-06:00` frontmatter property to prevent re-processing. This is required — `/meeting wrap pending` relies on it to detect unprocessed meetings.

### Step 6: Offer to commit

See [/commit](../commit/SKILL.md). Skip when called as part of a sequence (e.g. `/meeting wrap`).

## Important Notes

- Always read the file before editing — frontmatter may have changed via iCloud sync.
- The user is Your Name. References to "Your Name", "Ben", or "someone in [Your City/Country]" are the user.
- Do NOT duplicate todos that already exist in the note body (compare by description similarity).
- When in doubt about relevance, include it as `⬜` and let the user decide.
- If the meeting is old (>2 weeks), flag items that may already be completed and suggest skipping them.
