# -*- coding: utf-8 -*-
"""Build the two dev hand-off zips. Files keep their REPO-RELATIVE paths so that
unzipping BOTH into one folder (= the dev's WORKDIR) preserves the cross-references
(WORKDIR/deploy_golive_dt5g_v4/..., deploy_v3_4b_package/...). Excludes secrets."""
import os, sys, io, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"/home/trido/thanhdt/WorkingClaude"
DIST = os.path.join(ROOT, "deploy_golive_dt5g_v4", "dist"); os.makedirs(DIST, exist_ok=True)

# (source_relpath, arcname)  — arcname defaults to source_relpath
ZIP1 = [  # DT5G state engine
    "macro_state_live.py", "macro_healthcheck.py", "pull_us_market.py",
    "rebuild_state_from_ticker.bat", "sbv_macro_overlay.py", "build_dt_4gate.py",
    "simulate_holistic_nav.py", "telegram_recommend.py", "telegram_config.template.json",
    "vnindex_5state_ew_v1.py", "build_concentration_history.py", "vnindex_5state_dual_v3.py",
    "deploy_v3_4b_package/build_v3_1_clean.py", "deploy_v3_4b_package/build_v3_4_bull_aware.py",
    "deploy_golive_dt5g_v4/publish_gated_state.py",
    # reconciliation kit: transitions + daily reference + diff tool (localize the ~1% gap)
    "deploy_golive_dt5g_v4/dt5g_transitions.csv",
    "deploy_golive_dt5g_v4/dt5g_daily_reference.csv",
    "deploy_golive_dt5g_v4/reconcile_dt5g.py",
    "deploy_golive_dt5g_v4/requirements.txt",
    ("deploy_golive_dt5g_v4/README_zip1_dt5g.md", "deploy_golive_dt5g_v4/README.md"),
]
ZIP2 = [  # V4 + DT5G recommender (RETIRED 2026-06-12 — superseded by ZIP3; kept for reproducibility)
    "signal_v11_sql.py", "simulate_holistic_nav.py",
    "compare_v11_v12_concentration_switch.csv", "earnings_events_classified.csv",
    "deploy_golive_dt5g_v4/golive_recommend.py", "deploy_golive_dt5g_v4/golive_daily.bat",
    "deploy_golive_dt5g_v4/requirements.txt",
    "deploy_golive_dt5g_v4/README.md",
    "deploy_golive_dt5g_v4/README_zip2_v4.md",
]
ZIP3 = [  # V2.3 + DT5G recommender (replaces ZIP2 in production, 2026-06-12).
    # Unzip AFTER ZIP1: intentionally overwrites simulate_holistic_nav.py (bq 0-row fix)
    # and telegram_recommend.py (V2.3 report layout).
    "deploy_golive_dt5g_v4/golive_recommend_v23.py",
    "deploy_golive_dt5g_v4/golive_daily.bat",
    "deploy_golive_dt5g_v4/README.md",
    "deploy_golive_dt5g_v4/README_zip3_v23.md",
    "deploy_golive_dt5g_v4/requirements.txt",
    "signal_v11_sql.py", "simulate_holistic_nav.py",
    "earnings_events_classified.csv", "earnings_surprise_data.pkl",
    # optional Telegram desk report (V2.3 layout) + its display dependencies
    "telegram_recommend.py", "telegram_config.template.json",
    "recommend_holistic.py", "fundamental_rating_all.csv", "data/rating_8l.csv",
]
BLOCK = {"telegram_config.json"}  # never ship secrets

def build(name, items):
    path = os.path.join(DIST, name)
    n = 0
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for it in items:
            src, arc = (it if isinstance(it, tuple) else (it, it))
            if os.path.basename(src) in BLOCK:
                print(f"  SKIP secret {src}"); continue
            full = os.path.join(ROOT, src.replace("/", os.sep))
            if not os.path.exists(full):
                print(f"  MISSING {src} — skipped"); continue
            z.write(full, arc); n += 1
    print(f"  {name}: {n} files, {os.path.getsize(path)/1024:.0f} KB")
    return path

print("Building dev hand-off zips...")
p1 = build("dt5g_state_engine.zip", ZIP1)
p2 = build("v4_dt5g_recommender.zip", ZIP2)
p3 = build("v23_dt5g_recommender.zip", ZIP3)
print("DONE.")
for p in (p1, p2, p3):
    with zipfile.ZipFile(p) as z:
        print(f"\n== {os.path.basename(p)} ==")
        for nm in z.namelist(): print(f"   {nm}")
