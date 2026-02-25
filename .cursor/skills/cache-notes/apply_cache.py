#!/usr/bin/env python3
"""Apply cached Google Doc content as Obsidian callouts to meeting files.

Usage:
    python apply_cache.py <mappings.json>

mappings.json format:
    {
        "Meetings/PAM/Some Meeting.md": "## Title\n\n### Summary\n...",
        ...
    }
"""

import json
import sys
import re
from datetime import datetime, timezone, timedelta


CST = timezone(timedelta(hours=-6))


def parse_gemini_doc(content: str) -> dict:
    summary_match = re.search(r'### Summary\s*\n(.*?)(?=\n### Details|\n### Suggested next steps|$)', content, re.DOTALL)
    details_match = re.search(r'### Details\s*\n(.*?)(?=\n### Suggested next steps|$)', content, re.DOTALL)
    todos_match = re.search(r'### Suggested next steps\s*\n(.*?)(?=\n\*You should review|\n\*Please provide|$)', content, re.DOTALL)

    return {
        'summary': summary_match.group(1).strip() if summary_match else '',
        'details': details_match.group(1).strip() if details_match else '',
        'todos': todos_match.group(1).strip() if todos_match else '',
    }


def to_callout_line(line: str) -> str:
    if line == '':
        return '>'
    return f'> {line}'


def format_callouts(parsed: dict) -> str:
    lines = []

    if parsed['summary'] or parsed['details']:
        lines.append('> [!gemini_notes]- Summary & Details')
        if parsed['summary']:
            lines.append('> ### Summary')
            for line in parsed['summary'].split('\n'):
                lines.append(to_callout_line(line))
        if parsed['details']:
            lines.append('>')
            lines.append('> ### Details')
            for line in parsed['details'].split('\n'):
                lines.append(to_callout_line(line))
        lines.append('')

    if parsed['todos']:
        lines.append('> [!gemini_todos]- Suggested Next Steps')
        for line in parsed['todos'].split('\n'):
            if line.strip().startswith('- '):
                lines.append(to_callout_line(line))
            elif line.strip():
                lines.append(to_callout_line(f'- {line}'))
            else:
                lines.append('>')
        lines.append('')

    return '\n'.join(lines)


def apply_to_file(filepath: str, doc_content: str, timestamp: str) -> bool:
    with open(filepath, 'r') as f:
        content = f.read()

    if 'NotesCached:' in content and '## AI Transcripts' in content:
        return False

    parsed = parse_gemini_doc(doc_content)
    callouts = format_callouts(parsed)

    if not callouts.strip():
        return False

    ai_section = f'\n## AI Transcripts\n\n### Gemini\n\n{callouts}'

    frontmatter_end = content.find('---', content.find('---') + 3)
    if frontmatter_end == -1:
        return False

    insert_pos = frontmatter_end + 3
    before = content[:insert_pos]
    after = content[insert_pos:]

    if 'NotesCached:' not in before:
        before = before[:frontmatter_end] + f'NotesCached: {timestamp}\n' + before[frontmatter_end:]

    existing_content = after.strip()
    if existing_content:
        new_content = before + '\n' + existing_content + '\n' + ai_section + '\n'
    else:
        new_content = before + ai_section + '\n'

    with open(filepath, 'w') as f:
        f.write(new_content)

    return True


def main():
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <mappings.json>')
        sys.exit(1)

    with open(sys.argv[1]) as f:
        mappings = json.load(f)

    timestamp = datetime.now(CST).strftime('%Y-%m-%dT%H:%M:%S-06:00')

    results = {'success': 0, 'skipped': 0, 'failed': 0}
    for filepath, doc_content in mappings.items():
        try:
            if apply_to_file(filepath, doc_content, timestamp):
                results['success'] += 1
                print(f'  OK: {filepath}')
            else:
                results['skipped'] += 1
                print(f'  SKIP: {filepath}')
        except Exception as e:
            results['failed'] += 1
            print(f'  FAIL: {filepath}: {e}')

    print(f"\nDone: {results['success']} cached, {results['skipped']} skipped, {results['failed']} failed")


if __name__ == '__main__':
    main()
