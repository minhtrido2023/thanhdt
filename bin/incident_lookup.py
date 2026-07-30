#!/usr/bin/env python3
"""incident_lookup.py <label> [details]

Deterministic keyword search over kb/incidents/ (OKF: 1 sự cố = 1 file), used by
ops_autofix.sh/wags_autofix.sh to hand a fixer prior-occurrence context INLINE instead of making
it rediscover history via its own tool calls every dispatch (cost-opt #2, 2026-07-30 — "biết
trước rồi thì đừng bắt LLM tìm lại"). Not a replacement for the fixer's own verification: each
incident so far has turned out to have a genuinely different specific root cause even within the
same recurring pattern (see the "data-registry-accuracy" family in kb/incidents/) — this only
shortcuts the SEARCH step, never the diagnosis.

Scans every `.md` under kb/incidents/ (each file IS one entry — before the 2026-07-30 OKF migrate
this script had to split one 408KB kb/INCIDENTS.md on "## " and merge wrapped header lines
itself; the directory layout removes that whole failure mode), skips the index, strips YAML
frontmatter, scores each by keyword DENSITY (distinct-keyword hits normalized by length, not raw
count — a raw count without normalization is a length proxy: on real payloads it made large
end-of-day RETRO digests always outrank short, specific, genuinely-matching entries), and prints
the top 2 with score > 0, each labelled with its file path so the caller can read the full entry.
Word-boundary matching only (no substring containment) and bare numeric tokens (dates/years,
near-universal across a dated log) are dropped from the keyword set. Prints nothing (silent,
exit 0) on no match or any error — caller must treat empty output as "no known prior occurrence
found", not as a failure.
"""
import sys, os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INCIDENTS_DIR = os.path.join(ROOT, "kb", "incidents")
MAX_SECTIONS = 2
MAX_CHARS = 1500
DENSITY_DIVISOR = 1500  # section length (chars) that counts as "one unit" for normalization


def keywords(*texts):
    words = re.findall(r"[a-z0-9]+", " ".join(texts).lower())
    return {w for w in words if len(w) >= 4 and not w.isdigit()}


def strip_frontmatter(text):
    """Drop the leading '---' YAML block if present (title is repeated as the '# ' heading)."""
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    return text[end + 5:] if end != -1 else text


def entries():
    """Yield (relative_path, body_text) for every incident file. Skips index files."""
    for dirpath, _dirnames, filenames in os.walk(INCIDENTS_DIR):
        for fn in sorted(filenames):
            if not fn.endswith(".md") or fn == "index.md":
                continue
            full = os.path.join(dirpath, fn)
            try:
                with open(full, encoding="utf-8") as f:
                    text = f.read()
            except Exception:
                continue
            rel = os.path.relpath(full, ROOT)
            yield rel, strip_frontmatter(text).strip()


def main():
    if len(sys.argv) < 2:
        return
    label = sys.argv[1]
    details = sys.argv[2] if len(sys.argv) > 2 else ""
    kws = keywords(label, details)
    if not kws:
        return

    kw_re = re.compile(r"\b(" + "|".join(re.escape(w) for w in kws) + r")\b")
    scored = []
    try:
        for rel, sec in entries():
            hits = len(set(kw_re.findall(sec.lower())))
            if hits == 0:
                continue
            density = hits / (1 + len(sec) / DENSITY_DIVISOR)
            scored.append((density, rel, sec))
    except Exception:
        return

    if not scored:
        return
    scored.sort(key=lambda x: -x[0])
    top = scored[:MAX_SECTIONS]

    print("[Tự động tra kb/incidents/ theo từ khoá — CHỈ LÀ GỢI Ý (có thể không liên quan) để "
          "đỡ phải tìm lại từ đầu, PHẢI tự verify có thực sự cùng root cause không trước khi áp "
          "dụng lại cách sửa cũ:]")
    for _score, rel, sec in top:
        if len(sec) > MAX_CHARS:
            sec = sec[:MAX_CHARS] + "\n… (cắt bớt, đọc file gốc nếu cần đầy đủ)"
        print("\n--- (nghi liên quan theo từ khoá, chưa chắc đúng) — mike/%s ---" % rel)
        print(sec)


if __name__ == "__main__":
    main()
