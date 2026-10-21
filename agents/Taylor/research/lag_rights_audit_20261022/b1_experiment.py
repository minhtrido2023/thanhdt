#!/usr/bin/env python3
"""B1 — hồi cứu: cảnh báo ex-date có bắt QUYỀN MUA (ISS/Rights) của mã đang giữ không?

CHỈ gọi hàm THUẦN với fixture; mọi kênh gửi (notify/bus/marker) bị thay bằng hàm ném lỗi.
BQ chỉ ĐỌC (corporate_action, corporate_action_snapshots, ticker). Không ghi data/ state/.
Chạy: cd <worktree> && MIKE_BOT_TEST_MODE=1 TZ=Asia/Ho_Chi_Minh python3 agents/Taylor/research/lag_rights_audit_20261022/b1_experiment.py
"""
import json
import os
import sys

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
WT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
BIN = os.path.join(WT, "bin")
sys.path.insert(0, BIN)

import corp_action_daily as cad  # noqa: E402
sys.path.insert(0, BIN)   # cad chèn mike/bin lên đầu — đặt lại worktree bin lên trước
import nav_exdate_forecast as nef  # noqa: E402
import exdate_frame as xf  # noqa: E402
import corp_action_broker_detect as cbd  # noqa: E402
import corp_action_lib as lib  # noqa: E402


def _boom(*a, **k):
    raise RuntimeError("SIDE EFFECT BLOCKED (audit)")


for m in (cad, nef):
    for name in ("notify", "bus", "_mark_alerted_today", "_atomic_write_json"):
        if hasattr(m, name):
            setattr(m, name, _boom)

print("module files:", {m.__name__: m.__file__ for m in (cad, nef, xf, cbd, lib)})

COLS = """ticker, event_code, CAST(exright_date AS STRING) exright_date,
  CAST(effective_date AS STRING) effective_date, event_status, value_per_share, exercise_ratio,
  issue_method_name_vi, shares_delta, shares_total_after, event_title_vi,
  CAST(public_date AS STRING) public_date, CAST(record_date AS STRING) record_date,
  issue_volumn, total_value, issue_status_code, id"""

HOLD = {"SCL": 14000, "DIG": 10000, "NLG": 5000, "BVB": 10000, "NVL": 10000}
CUM = {"SCL": 22200.0, "DIG": 21550.0, "NLG": 42050.0}   # Price phiên cum cuối (tav2_bq.ticker, đo 2026-10-22)
RIGHTS_IDS = {"SCL": "682291730e8a716db6edd5a4", "DIG": "68083370b3bb8d7911ef70a1",
              "NLG": "67dcb1e9ac13fa2f172c79b3"}


def section(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


def run_daily_and_nav(asof, rows, held):
    up = cad.upcoming_events(asof, set(held), rows=rows)
    holders = {e["ticker"]: [("SpaceX", held[e["ticker"]])] for e in up}
    print(f"[corp_action_daily.upcoming_events asof={asof}] n={len(up)}")
    for e in up:
        print("   ", cad._fmt_event(e, holders).replace("\n", "\n    "))
    snap = {"upcoming_events_held": up}
    rel = nef.relevant_events(snap, asof)
    pos = {"SpaceX": {tk: {"qty": q, "price": CUM.get(tk)} for tk, q in held.items()}}
    print(f"[nav_exdate_forecast.relevant_events ≤1 phiên] n={len(rel)}")
    for e in rel:
        print("   ", nef.build_event_line(e, pos, asof=asof))
    return up, rel


# ───────────────────── E1: 3 đợt quyền mua 2025 (SCL/DIG/NLG), hồi cứu theo asof
section("E1 — quyền mua 2025 đã thực hiện; fixture = dòng BQ thật, ép event_status='announced' "
        "(giả lập vintage trước GDKHQ; bảng nguồn bị upsert nên KHÔNG có vintage thật trước 2026-08-17)")
rows_now = lib.bq(f"SELECT {COLS} FROM `{lib.TABLE}` AS c WHERE c.id IN "
                  f"({','.join(repr(v).replace(chr(39), chr(34)) for v in RIGHTS_IDS.values())})")
for r in rows_now:
    print("BQ row:", json.dumps({k: r[k] for k in ("ticker", "exercise_ratio", "public_date", "exright_date",
                                                   "record_date", "issue_volumn", "total_value",
                                                   "issue_status_code", "event_status")}, ensure_ascii=False))
fix = [dict(r, event_status="announced") for r in rows_now]
plan = {"SCL": ["2025-10-10", "2025-10-14", "2025-10-16", "2025-10-17"],
        "DIG": ["2025-10-02", "2025-10-06", "2025-10-08"],
        "NLG": ["2025-10-14", "2025-10-15", "2025-10-16"]}
for tk, dates in plan.items():
    for asof in dates:
        run_daily_and_nav(asof, [r for r in fix if r["ticker"] == tk], {tk: HOLD[tk]})

# ───────────────────── E2: vintage THẬT từ snapshot (BVB/NVL 2026 P→có ngày→D; SCL P 15,38%)
section("E2 — vintage THẬT tav2_mike.corporate_action_snapshots: chạy upcoming_events(asof=snapshot_date, rows=vintage đó)")
ids = {"BVB": "6949e1c7bdc91e0e0d556c68", "NVL": "6a4c4732279ac17a86f02b65", "SCL": "6a0516165b1fb4c98c3ab2a2"}
snap_rows = lib.bq(f"SELECT CAST(s.snapshot_date AS STRING) sd, {COLS.replace('ticker,', 's.ticker,', 1)} "
                   f"FROM `lithe-record-440915-m9.tav2_mike.corporate_action_snapshots` AS s "
                   f"WHERE s.id IN ({','.join(chr(34) + v + chr(34) for v in ids.values())}) "
                   f"AND s.snapshot_date BETWEEN '2026-09-05' AND '2026-10-21' ORDER BY s.ticker, sd")
by = {}
for r in snap_rows:
    by.setdefault((r["ticker"], r["sd"]), []).append(r)
first_alert = {}
for (tk, sd), rr in sorted(by.items()):
    up = cad.upcoming_events(sd, {tk}, rows=rr)
    r0 = rr[0]
    tag = (f"{tk} snap={sd} st={r0['issue_status_code']}/{r0['event_status']} pd={r0['public_date']} "
           f"ex={r0['exright_date']} rd={r0['record_date']} vol={r0['issue_volumn']} tv={r0['total_value']} "
           f"→ upcoming n={len(up)}")
    if up:
        first_alert.setdefault(tk, sd)
        tag += "  ALERT: " + cad._fmt_event(up[0], {tk: [("SpaceX", HOLD[tk])]}).replace("\n", " | ")
    print(tag)
print("first asof có cảnh báo corp_action_daily:", first_alert)

# ───────────────────── E3: fixture SCL P 2026 → bản sau có ngày → D
section("E3 — fixture SCL 15,38%: P/NULL ngày → P có exright/record (giả định) → D có KL/tổng giá trị")
base = [r for r in snap_rows if r["ticker"] == "SCL"][-1]
v1 = dict(base)                                                     # thật: P, ngày NULL
v2 = dict(base, exright_date="2026-11-05", record_date="2026-11-06")  # GIẢ ĐỊNH ngày
v3 = dict(v2, event_status="executed", issue_status_code="D", issue_volumn="6000000", total_value="7.5E10")
for asof, v in (("2026-10-22", v1), ("2026-10-30", v2), ("2026-11-03", v2), ("2026-11-04", v2),
                ("2026-11-05", v3), ("2026-11-06", v3)):
    print(f"-- vintage st={v['issue_status_code']} ex={v['exright_date']}")
    run_daily_and_nav(asof, [v], {"SCL": HOLD["SCL"]})
print("Cột corp_action_lib._events() SELECT (không có record_date/issue_volumn/total_value/id):")
import inspect  # noqa: E402
src = inspect.getsource(lib._events)
print("   record_date" in src, "issue_volumn" in src, "total_value" in src, " id," in src)

# ───────────────────── E4: due_diligence._get_upcoming_exdate (cờ EXDATE_SAP_TOI của lag_dd_pack)
section("E4 — trading_bot.due_diligence._get_upcoming_exdate (BQ thật, chỉ đọc)")
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import trading_bot.due_diligence as dd  # noqa: E402
seen_codes = []
_orig = lib.pricing_events


def _spy(tickers, since=None, until=None, codes=("DIV", "ISS")):
    seen_codes.append(tuple(codes))
    return _orig(tickers, since=since, until=until, codes=codes)


dd._corp_action_lib().pricing_events = _spy
for tk, asof in (("SCL", "2025-10-10"), ("SCL", "2025-10-14"), ("DIG", "2025-10-02"), ("NLG", "2025-10-14")):
    dd._CACHE.clear()
    out = dd._get_upcoming_exdate(tk, today_ict=asof, ref_price=CUM[tk])
    print(f"{tk} asof={asof} → upcoming_exdate={out}")
print("codes truyền vào pricing_events:", seen_codes)
dd._corp_action_lib().pricing_events = _orig
dd._CACHE.clear()
print("_recent_iss SCL asof 2025-10-24 (sau GDKHQ):", dd._recent_iss("SCL", "2025-10-24"))

# ───────────────────── E5: exdate_frame + broker_detect (đêm trước GDKHQ, giá tham chiếu quyền mua)
section("E5 — exdate_frame.verify_post_event_price + broker_detect.decide_price_only với TERP quyền mua")
for tk, r, px_issue in (("SCL", 0.35714286, 12500.0), ("DIG", 0.232, 12000.0), ("NLG", 0.26, 25000.0)):
    pc = CUM[tk]
    terp = (pc + r * px_issue) / (1 + r)
    print(f"{tk}: cum {pc:,.0f} giá PH {px_issue:,.0f} r={r} ⇒ TERP {terp:,.1f} (giảm {1 - terp / pc:.2%}); "
          f"nav_exdate nói 'giảm ~{r / (1 + r):.2%}, KL tăng ~{r:.2%}'")
    print("   verify_post_event_price(mult=1+r):", xf.verify_post_event_price(pc, round(terp, -1), 1 + r))
    for exch in ("HOSE", "HNX", "UPCOM"):
        res = cbd.decide_price_only(tk, "2025-10-16", None,
                                    {"SpaceX": {"verdict": cbd.CONFIRMABLE, "cash_leg": 0.0,
                                                "mkt1": [round(terp, -1)]}},
                                    pc, exch, {}, vendor_events=())
        print(f"   decide_price_only[{exch}] → {res['verdict']}: {res.get('why')}")

print("\nDONE — không có side effect nào được gọi (mọi notify/bus bị chặn bằng _boom).")
