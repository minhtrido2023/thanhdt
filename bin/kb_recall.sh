#!/usr/bin/env bash
# bin/kb_recall.sh — keyword-based KB section retrieval
# Usage: kb_recall.sh "keyword1 keyword2 ..." [--top N] [--budget-words W] [--sources LIST]
#
# Trả về các section KB liên quan nhất đến keywords, dưới ngưỡng word-budget.
# Dùng trước khi dispatch để Mike prepend context đúng task vào prompt thay vì
# inject cả context_pack.md (11.9K token, median 0% relevance — Taylor finding 2026-08-17).
#
# Sources (mặc định: context_pack,coding_guidelines):
#   context_pack      — kb/context_pack.md (split theo ## header)
#   coding_guidelines — kb/coding_guidelines.md (split theo ## header)
#   data_registry     — kb/data_registry/index.md (entry-level)
#   projects          — kb/projects/INDEX.md (1 dòng/project)
#
# Ví dụ:
#   bin/kb_recall.sh "GDKHQ rounding UPCOM"
#   bin/kb_recall.sh "DT5G regime VIX" --top 3 --budget-words 800
#   bin/kb_recall.sh "executor funding gate" --sources "context_pack,coding_guidelines"
#   RECALL=$(bin/kb_recall.sh "capit basket") && bin/dispatch.sh Taylor "$RECALL
#
# Task: ..."

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

KEYWORDS=""
TOP=5
BUDGET_WORDS=2000
SOURCES="context_pack,coding_guidelines"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --top)          TOP="$2";          shift 2 ;;
    --budget-words) BUDGET_WORDS="$2"; shift 2 ;;
    --sources)      SOURCES="$2";      shift 2 ;;
    -*)             echo "Unknown flag: $1" >&2; exit 1 ;;
    *)              KEYWORDS="$KEYWORDS $1"; shift ;;
  esac
done
KEYWORDS="${KEYWORDS# }"

if [[ -z "$KEYWORDS" ]]; then
  echo "Usage: kb_recall.sh \"keywords\" [--top N] [--budget-words W] [--sources LIST]" >&2
  exit 1
fi

python3 - "$ROOT" "$KEYWORDS" "$TOP" "$BUDGET_WORDS" "$SOURCES" << 'PYEOF'
import sys, re, os

root, keywords_str, top_s, budget_s, sources_str = sys.argv[1:]
top = int(top_s)
budget = int(budget_s)
keywords = [k.lower() for k in keywords_str.split()]
sources = [s.strip() for s in sources_str.split(',')]

FILES = {
    'context_pack':      os.path.join(root, 'kb/context_pack.md'),
    'coding_guidelines': os.path.join(root, 'kb/coding_guidelines.md'),
    'data_registry':     os.path.join(root, 'kb/data_registry/index.md'),
    'projects':          os.path.join(root, 'kb/projects/INDEX.md'),
}
# Fallback for projects
if not os.path.exists(FILES['projects']):
    FILES['projects'] = os.path.join(root, 'kb/projects/index.md')

def hit_count(text):
    t = text.lower()
    return sum(len(re.findall(re.escape(kw), t)) for kw in keywords)

def split_sections(path):
    """Split markdown file into (header, body) pairs by ## headers."""
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        content = f.read()
    sections = []
    parts = re.split(r'\n(?=##\s)', content)
    for part in parts:
        part = part.strip()
        if part:
            sections.append(part)
    return sections

def index_lines(path):
    """Treat the whole file as one block (for index-style files)."""
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        lines = [l.rstrip() for l in f if l.strip()]
    # Return as one section
    return ['\n'.join(lines)] if lines else []

scored = []
for src in sources:
    path = FILES.get(src)
    if not path:
        print(f'[kb_recall: unknown source {src}]', file=sys.stderr)
        continue
    if src in ('data_registry', 'projects'):
        sections = index_lines(path)
    else:
        sections = split_sections(path)
    for sec in sections:
        hits = hit_count(sec)
        if hits > 0:
            scored.append((hits, sec))

scored.sort(key=lambda x: -x[0])

if not scored:
    print(f'[kb_recall: no matching sections for: {keywords_str}]')
    sys.exit(0)

print('---')
print(f'# KB Recall — keywords: {keywords_str}')
print(f'# (top-{top} sections, budget {budget} words)')
print('---')
print()

emitted = 0
words_used = 0
for hits, sec in scored:
    if emitted >= top:
        break
    wc = len(sec.split())
    if words_used + wc <= budget:
        print(sec)
        print()
        words_used += wc
        emitted += 1

print(f'# [{emitted}/{len(scored)} sections shown, ~{words_used} words of {budget} budget]')
PYEOF
