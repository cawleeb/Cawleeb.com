#!/usr/bin/env python3
"""Simple Markdown validator.
Checks each .md file in the repository for:
- YAML front matter (starts with '---')
- presence of a `title:` field in the front matter
- stray HTML closing tags like </div>
Exits with non-zero code if any file has issues.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

issues = []

for dirpath, dirnames, filenames in os.walk(ROOT):
    # skip .git
    if '.git' in dirpath.split(os.sep):
        continue
    for fn in filenames:
        if not fn.lower().endswith('.md'):
            continue
        path = os.path.join(dirpath, fn)
        rel = os.path.relpath(path, ROOT)
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        if not text.lstrip().startswith('---'):
            issues.append(f'{rel}: missing YAML front matter')
            continue
        # extract front matter
        parts = text.split('\n')
        if len(parts) < 2:
            issues.append(f'{rel}: short file')
            continue
        # find end of front matter
        try:
            end_idx = parts[1:].index('---') + 1
            fm_lines = parts[:end_idx+1]
        except ValueError:
            issues.append(f'{rel}: unterminated YAML front matter')
            continue
        fm_text = '\n'.join(fm_lines)
        if 'title:' not in fm_text:
            issues.append(f'{rel}: front matter missing `title:`')
        # look for common stray HTML
        if '</div>' in text or '<div' in text:
            issues.append(f'{rel}: contains raw HTML tags (</div> or <div>) - consider removing')

if issues:
    print('Validation failed:')
    for it in issues:
        print(' -', it)
    sys.exit(2)
else:
    print('All markdown files passed validation.')
    sys.exit(0)
