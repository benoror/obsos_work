#!/usr/bin/env python3
"""Batch cache Google Docs meeting notes as Obsidian callouts.

Usage:
    ASDF_PYTHON_VERSION=3.11.14 python3 batch_cache.py [--dry-run]

Scans Meetings/ for files with Google Docs links but no NotesCached,
fetches each doc, parses Gemini sections, and embeds as callouts.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
_user_email = os.environ.get('GOOGLE_EMAIL')
if not _user_email:
    _user_md = os.path.join(WORKSPACE_ROOT, 'USER.md')
    if os.path.exists(_user_md):
        with open(_user_md) as _f:
            _m = re.search(r'\*\*Email\*\*:\s*`?([^`\s]+)`?', _f.read())
            if _m:
                _user_email = _m.group(1)
if not _user_email:
    raise RuntimeError('Set GOOGLE_EMAIL env var or fill Email in USER.md')
CREDS_PATH = os.path.expanduser(f'~/.google_workspace_mcp/credentials/{_user_email}.json')
CST = timezone(timedelta(hours=-6))


def get_docs_service():
    with open(CREDS_PATH) as f:
        creds_data = json.load(f)
    creds = Credentials(
        token=creds_data.get('token'),
        refresh_token=creds_data.get('refresh_token'),
        token_uri=creds_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=creds_data.get('client_id'),
        client_secret=creds_data.get('client_secret'),
    )
    return build('docs', 'v1', credentials=creds)


def find_uncached_files():
    meetings_dir = os.path.join(WORKSPACE_ROOT, 'Meetings')
    has_docs = set()
    has_cached = set()

    for root, _, files in os.walk(meetings_dir):
        for fname in files:
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, WORKSPACE_ROOT)
            with open(fpath) as f:
                content = f.read()
            if 'docs.google.com/document' in content:
                has_docs.add(rel)
            if 'NotesCached:' in content:
                has_cached.add(rel)

    return sorted(has_docs - has_cached)


def extract_doc_id(content):
    m = re.search(r'docs\.google\.com/document/d/([^/\s]+)', content)
    return m.group(1) if m else None


def fetch_doc_text(service, doc_id):
    doc = service.documents().get(documentId=doc_id, includeTabsContent=True).execute()
    parts = []
    tabs = doc.get('tabs', [])
    for tab in tabs:
        tab_props = tab.get('tabProperties', {})
        title = tab_props.get('title', 'Untitled')
        body = tab.get('documentTab', {}).get('body', {})
        text = extract_text_from_body(body)
        parts.append((title, text))
    if not parts:
        body = doc.get('body', {})
        text = extract_text_from_body(body)
        parts.append(('Notes', text))
    return parts


def extract_text_from_body(body):
    lines = []
    for elem in body.get('content', []):
        para = elem.get('paragraph', {})
        if para:
            line_parts = []
            for pe in para.get('elements', []):
                tr = pe.get('textRun', {})
                if tr.get('content'):
                    line_parts.append(tr['content'])
            line = ''.join(line_parts).rstrip('\n')
            lines.append(line)
    return '\n'.join(lines)


def parse_gemini_sections(text):
    summary = ''
    details = ''
    todos = ''

    s_match = re.search(r'(?:^|\n)Summary\n(.*?)(?=\nDetails\n|\nSuggested next steps\n|$)', text, re.DOTALL)
    d_match = re.search(r'(?:^|\n)Details\n(.*?)(?=\nSuggested next steps\n|$)', text, re.DOTALL)
    t_match = re.search(r'(?:^|\n)Suggested next steps\n(.*?)(?=\nYou should review|$)', text, re.DOTALL)

    if s_match:
        summary = s_match.group(1).strip()
    if d_match:
        details = d_match.group(1).strip()
    if t_match:
        todos = t_match.group(1).strip()

    return summary, details, todos


def to_callout_line(line):
    return '>' if line == '' else f'> {line}'


def format_callouts(summary, details, todos):
    lines = []

    if summary or details:
        lines.append('> [!gemini_notes]- Summary & Details')
        if summary:
            lines.append('> ### Summary')
            for l in summary.split('\n'):
                lines.append(to_callout_line(l))
        if details:
            lines.append('>')
            lines.append('> ### Details')
            for l in details.split('\n'):
                if l.strip() and not l.startswith('- '):
                    lines.append(to_callout_line(f'- {l}'))
                else:
                    lines.append(to_callout_line(l))
        lines.append('')

    if todos:
        lines.append('> [!gemini_todos]- Suggested Next Steps')
        for l in todos.split('\n'):
            if l.strip() and not l.startswith('- '):
                lines.append(to_callout_line(f'- {l}'))
            else:
                lines.append(to_callout_line(l))
        lines.append('')

    return '\n'.join(lines)


def apply_to_file(filepath, callouts, timestamp):
    with open(filepath) as f:
        content = f.read()

    fm_start = content.find('---')
    fm_end = content.find('---', fm_start + 3)
    if fm_start == -1 or fm_end == -1:
        return False

    before_closing = content[:fm_end]
    after_closing = content[fm_end:]

    if 'NotesCached:' not in before_closing:
        before_closing += f'NotesCached: {timestamp}\n'

    existing_body = after_closing[3:].strip()  # skip the ---
    ai_section = f'\n## AI Transcripts\n\n### Gemini\n\n{callouts}'

    if existing_body:
        new_content = before_closing + '---\n' + existing_body + '\n' + ai_section + '\n'
    else:
        new_content = before_closing + '---' + ai_section + '\n'

    with open(filepath, 'w') as f:
        f.write(new_content)
    return True


def main():
    dry_run = '--dry-run' in sys.argv

    print('Finding uncached meeting files...')
    uncached = find_uncached_files()
    print(f'Found {len(uncached)} files to process.\n')

    if not uncached:
        print('Nothing to do!')
        return

    if dry_run:
        for f in uncached:
            print(f'  Would process: {f}')
        return

    print('Connecting to Google Docs API...')
    service = get_docs_service()

    timestamp = datetime.now(CST).strftime('%Y-%m-%dT%H:%M:%S-06:00')
    results = {'success': 0, 'skipped': 0, 'failed': 0}

    for i, rel_path in enumerate(uncached, 1):
        abs_path = os.path.join(WORKSPACE_ROOT, rel_path)
        with open(abs_path) as f:
            content = f.read()

        doc_id = extract_doc_id(content)
        if not doc_id:
            print(f'  [{i}/{len(uncached)}] SKIP (no doc ID): {rel_path}')
            results['skipped'] += 1
            continue

        try:
            tabs = fetch_doc_text(service, doc_id)
            notes_text = ''
            for title, text in tabs:
                if title.lower() in ('notes', 'untitled'):
                    notes_text = text
                    break
            if not notes_text and tabs:
                notes_text = tabs[0][1]

            summary, details, todos = parse_gemini_sections(notes_text)
            if not summary and not details and not todos:
                print(f'  [{i}/{len(uncached)}] SKIP (no Gemini sections): {rel_path}')
                results['skipped'] += 1
                continue

            callouts = format_callouts(summary, details, todos)
            if apply_to_file(abs_path, callouts, timestamp):
                print(f'  [{i}/{len(uncached)}] OK: {rel_path}')
                results['success'] += 1
            else:
                print(f'  [{i}/{len(uncached)}] SKIP (no frontmatter): {rel_path}')
                results['skipped'] += 1

        except Exception as e:
            print(f'  [{i}/{len(uncached)}] FAIL: {rel_path}: {e}')
            results['failed'] += 1

    print(f"\nDone: {results['success']} cached, {results['skipped']} skipped, {results['failed']} failed")


if __name__ == '__main__':
    main()
