# -*- coding: utf-8 -*-
"""
refresh_gdp_growth_vn.py — re-fetch VN real GDP growth from the World Bank API and rewrite the
GDP_ANNUAL literal in gdp_growth_vn.py (idempotent: only rewrites if the fetched series differs).

Annual, low-urgency refresh (see gdp_growth_vn.py provenance). No cron installed — run by hand or
fold into the Winston monthly macro-refresh routine if/when adopted. Prints a diff summary; writes
atomically (tmp + os.replace). Fail-safe: any fetch/parse error leaves the file untouched, exit 1.

Run: $DNA_PYEXE refresh_gdp_growth_vn.py
"""
import os, re, sys, json, urllib.request

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
TARGET = f"{WORKDIR}/gdp_growth_vn.py"
URL = ("https://api.worldbank.org/v2/country/VNM/indicator/NY.GDP.MKTP.KD.ZG"
       "?format=json&per_page=200&date=2000:2100")


def fetch():
    with urllib.request.urlopen(URL, timeout=30) as r:
        d = json.loads(r.read().decode())
    rows = [(int(x["date"]), round(float(x["value"]), 2)) for x in d[1] if x["value"] is not None]
    rows.sort()
    if len(rows) < 15:
        raise RuntimeError(f"suspiciously short series ({len(rows)} rows) — refusing to write")
    return rows


def render(rows):
    lines, buf = [], []
    for i, (y, v) in enumerate(rows):
        buf.append(f"({y}, {v:.2f}),")
        if len(buf) == 5 or i == len(rows) - 1:
            lines.append("    " + " ".join(buf))
            buf = []
    return "GDP_ANNUAL = [\n" + "\n".join(lines) + "\n]"


def main():
    try:
        rows = fetch()
    except Exception as exc:
        print(f"FETCH FAILED ({exc}) — file untouched"); return 1
    src = open(TARGET, encoding="utf-8").read()
    m = re.search(r"GDP_ANNUAL = \[.*?\n\]", src, re.S)
    if not m:
        print("could not locate GDP_ANNUAL literal — file untouched"); return 1
    new_block = render(rows)
    if src[m.start():m.end()] == new_block:
        print(f"no change — GDP_ANNUAL already current ({rows[0][0]}-{rows[-1][0]}, {len(rows)} obs)")
        return 0
    new_src = src[:m.start()] + new_block + src[m.end():]
    tmp = TARGET + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(new_src)
    os.replace(tmp, TARGET)
    print(f"UPDATED GDP_ANNUAL → {rows[0][0]}-{rows[-1][0]} ({len(rows)} obs); "
          f"latest {rows[-1][0]}={rows[-1][1]:.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
