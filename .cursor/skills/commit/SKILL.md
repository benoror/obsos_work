---
name: commit
description: Offers to commit changes after a skill modifies files. Stages only the affected files, uses a conventional commit message, and waits for user confirmation. Referenced by other skills as a final step.
---

# Commit

## Usage

This skill is invoked as the **final step** of any skill that modifies files. It is not meant to be called standalone — other skills reference it via:

```
See [/commit](../commit/SKILL.md).
```

## Sequence Mode

When a skill is called as part of a **sequenced workflow** (e.g. `/meeting wrap`), the caller is responsible for the single commit at the end. Individual skills **skip** their commit step in this case.

How to detect: the calling workflow will explicitly state it is running sub-skills in sequence. When you are executing a sub-skill within a sequence, do not offer to commit — just proceed to the next sub-skill. The sequence owner commits once at the end with a combined message.

## Workflow

### Step 1: Offer to commit

After all edits are applied, ask the user if they'd like to commit the changes.

### Step 2: Stage only modified files

- Only stage files that were actually modified by the current skill invocation (or the full sequence).
- Do NOT stage unrelated files that may have changed via iCloud sync or Obsidian plugins.
- Use `git add` with **explicit file paths** — never `git add .` or `git add -A`.

### Step 3: Commit message

**Standalone**: `update: /{skill-name} {argument}`

**Sequence**: `update: /{workflow-name} {argument}` (e.g. `update: /meeting wrap Meetings/PAM/Some Meeting.md`)

### Step 4: Confirm and commit

Present the list of files that will be staged and the proposed commit message. Wait for user confirmation before committing. If the user declines, skip silently.

Example flow:

```
I've updated 5 meeting files. Want me to commit these changes?

Files to stage:
  - Meetings/PAM/Ben x Zak Sync - 2026-02-23.md
  - Meetings/PAM/Scrum/2026-02-25.md (+ 3 more)

Commit message: "update: /followup-todos week"

[Yes / No]
```

## Important Notes

- This workspace may not be a git repo. If `git status` fails, skip the commit step entirely without error.
- Always use explicit file paths for staging — never broad patterns.
- If no files were actually modified, skip the commit offer.
