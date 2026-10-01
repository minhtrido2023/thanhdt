#!/usr/bin/env python3
"""Selfcheck for dna_report.build_macro_killswitch_a_line() (quant-skeptic round-1 required_change
#4, 2026-10-01). Monkeypatches dna_report.get_macro_killswitch_a() so every one of the 4 status
shapes (armed / clear / stale / None-on-failure) is exercised deterministically in both html=True
and html=False mode -- no BQ/network dependency, no TZ dependency (no datetime involved here at
all, pure string formatting over a fixed dict)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dna_report as dr

N = 0


def check(label, cond):
    global N
    N += 1
    assert cond, f"FAIL [{label}]"
    print(f"  ok: {label}")


FIXTURES = {
    "armed": {"armed": True, "rate": 0.09, "threshold": 0.075, "stale": False,
              "last_update": "2012-10-01", "age_days": 10, "reason": "deposit 9.00% > 7.5% -> SUSPEND",
              "rate_source": "big4_12m"},
    "clear": {"armed": False, "rate": 0.068, "threshold": 0.075, "stale": False,
              "last_update": "2026-06-01", "age_days": 20, "reason": "deposit 6.80% <= 7.5% -> CLEAR",
              "rate_source": "big4_12m"},
    "stale": {"armed": True, "rate": 0.068, "threshold": 0.075, "stale": True,
              "last_update": "2026-06-01", "age_days": 122, "reason": "feed stale (122d > 45d) -> fail-closed (armed)",
              "rate_source": "big4_12m"},
    # CCTG-driven shape (quant-skeptic round-2 fix 2, 2026-10-01) -- the line must name the TENOR
    # that actually drove the number, not a hardcoded "Big-4 12M" regardless of rate_source.
    "cctg_driven": {"armed": False, "rate": 0.075, "threshold": 0.075, "stale": False,
                    "last_update": "2026-10-01", "age_days": 1,
                    "reason": "cctg_6m(2026-09-30) 7.50% <= 7.5% -> CLEAR",
                    "rate_source": "cctg_6m(2026-09-30)"},
    # no-data fail-closed path: rate_source=None (early-return shape, e.g. no deposit data at all
    # or a corrupt-CSV error) -- must fall back to "N/A" for the source label, not crash on
    # rate_source.startswith().
    "no_data": {"armed": True, "rate": None, "threshold": 0.075, "stale": True,
                "last_update": None, "age_days": None,
                "reason": "no deposit data at/before asof -> fail-closed (armed)",
                "rate_source": None},
}

print("=== build_macro_killswitch_a_line selfcheck ===")
_orig = dr.get_macro_killswitch_a

for label, fixture in FIXTURES.items():
    dr.get_macro_killswitch_a = lambda f=fixture: f
    for html in (True, False):
        line = dr.build_macro_killswitch_a_line(html=html)
        check(f"{label} html={html}: line is non-empty string", isinstance(line, str) and len(line) > 0)
        verdict = "ARMED" if fixture["armed"] else "CLEAR"
        check(f"{label} html={html}: verdict '{verdict}' present", verdict in line)
        rate_s = f"{fixture['rate']*100:.1f}%" if fixture["rate"] is not None else "N/A"
        check(f"{label} html={html}: rate '{rate_s}' present", rate_s in line)
        if fixture["stale"]:
            check(f"{label} html={html}: STALE tag present", "STALE" in line)
        else:
            check(f"{label} html={html}: no STALE tag", "STALE" not in line)
        if html:
            check(f"{label} html=True: has <i> tail tag", "<i>" in line and "</i>" in line)
        else:
            check(f"{label} html=False: no HTML tags", "<i>" not in line and "<b>" not in line)
        badge = "🔴" if fixture["armed"] else "🟢"
        check(f"{label} html={html}: correct badge", badge in line)
        check(f"{label} html={html}: no stale legal-vn phrase", "chờ legal-vn" not in line)
        rsrc = fixture["rate_source"] or ""
        if rsrc.startswith("cctg_6m"):
            check(f"{label} html={html}: tail names CCTG 6 tháng", "CCTG" in line and "6 tháng" in line)
            check(f"{label} html={html}: tail does NOT mislabel as Big-4 12 tháng",
                  "Big-4 12 tháng" not in line)
        elif rsrc == "big4_12m":
            check(f"{label} html={html}: tail names Big-4 12 tháng", "Big-4 12 tháng" in line)
            check(f"{label} html={html}: tail does NOT mislabel as CCTG", "CCTG" not in line)
        else:
            check(f"{label} html={html}: no rate_source -> tail falls back to N/A", "N/A" in line)

# None case (BQ/import failure inside get_macro_killswitch_a, or any exception) -> caller drops
# the line entirely; build_macro_killswitch_a_line must return None, not raise, not a blank string.
dr.get_macro_killswitch_a = lambda: None
for html in (True, False):
    line = dr.build_macro_killswitch_a_line(html=html)
    check(f"none html={html}: line is None", line is None)

dr.get_macro_killswitch_a = _orig

print(f"\n=== {N} assertions PASS ===")
