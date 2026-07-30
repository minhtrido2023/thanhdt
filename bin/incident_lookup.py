#!/usr/bin/env python3
"""incident_lookup.py <label> [details]

Deterministic keyword search over kb/INCIDENTS.md, used by ops_autofix.sh/wags_autofix.sh to
hand a fixer prior-occurrence context INLINE instead of making it rediscover history via its
own tool calls every dispatch (cost-opt #2, 2026-07-30 — "biết trước rồi thì đừng bắt LLM tìm
lại"). Not a replacement for the fixer's own verification: each incident so far has turned out
to have a genuinely different specific root cause even within the same recurring pattern (see
kb/INCIDENTS.md's own "data-registry-accuracy" family) — this only shortcuts the SEARCH step,
never the diagnosis.

Splits INCIDENTS.md into its "## "-level entries (merging consecutive "## " lines first — some
long headers wrap across several such lines in the file, which would otherwise fragment one
entry into a bodiless header-only "section" plus an orphaned body), scores each by keyword
DENSITY (distinct-keyword hits normalized by length, not raw count — a raw count without
normalization is a length proxy: on real payloads it made large end-of-day RETRO digests always
outrank short, specific, genuinely-matching entries), and prints the top 2 with score > 0.
Word-boundary matching only (no substring containment) and bare numeric tokens (dates/years,
near-universal across a dated log) are dropped from the keyword set. Prints nothing (silent,
exit 0) on no match or any error — caller must treat empty output as "no known prior occurrence
found", not as a failure.
"""
import sys, os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INCIDENTS = os.path.join(ROOT, "kb", "INCIDENTS.md")
MAX_SECTIONS = 2
MAX_CHARS = 1500
DENSITY_DIVISOR = 1500  # section length (chars) that counts as "one unit" for normalization


def keywords(*texts):
    words = re.findall(r"[a-z0-9]+", " ".join(texts).lower())
    return {w for w in words if len(w) >= 4 and not w.isdigit()}


def merge_wrapped_headers(text):
    """Join consecutive '## '-prefixed lines into one logical header line."""
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("## "):
            parts = [lines[i][3:].rstrip()]
            j = i + 1
            while j < len(lines) and lines[j].startswith("## "):
                parts.append(lines[j][3:].rstrip())
                j += 1
            out.append("## " + " ".join(p for p in parts if p))
            i = j
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def main():
    if len(sys.argv) < 2:
        return
    label = sys.argv[1]
    details = sys.argv[2] if len(sys.argv) > 2 else ""
    kws = keywords(label, details)
    if not kws:
        return
    try:
        with open(INCIDENTS, encoding="utf-8") as f:
            text = merge_wrapped_headers(f.read())
    except Exception:
        return

    kw_re = re.compile(r"\b(" + "|".join(re.escape(w) for w in kws) + r")\b")
    parts = re.split(r"(?m)^(?=## )", text)
    scored = []
    for sec in parts:
        if not sec.startswith("## "):
            continue
        low = sec.lower()
        hits = len(set(kw_re.findall(low)))
        if hits == 0:
            continue
        density = hits / (1 + len(sec) / DENSITY_DIVISOR)
        scored.append((density, sec))

    if not scored:
        return
    scored.sort(key=lambda x: -x[0])
    top = scored[:MAX_SECTIONS]

    print("[Tự động tra kb/INCIDENTS.md theo từ khoá — CHỈ LÀ GỢI Ý (có thể không liên quan) để "
          "đỡ phải tìm lại từ đầu, PHẢI tự verify có thực sự cùng root cause không trước khi áp "
          "dụng lại cách sửa cũ:]")
    for _score, sec in top:
        sec = sec.strip()
        if len(sec) > MAX_CHARS:
            sec = sec[:MAX_CHARS] + "\n… (cắt bớt, đọc file gốc nếu cần đầy đủ)"
        print("\n--- (nghi liên quan theo từ khoá, chưa chắc đúng) ---")
        print(sec)


if __name__ == "__main__":
    main()
