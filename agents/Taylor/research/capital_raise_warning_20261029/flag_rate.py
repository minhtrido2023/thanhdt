"""Tỉ lệ mã sẽ mang cờ lớp A tại asof, áp ĐÚNG capital_raise_lib lên q_lag2.csv (ISS public≥2025) — ước cận dưới
(dòng public<2025 không có trong file). Mẫu số = mã có trong q_shares.csv (đang GD, ticker_1m)."""
import csv, sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/wt-capraise-20261029/bin")
import capital_raise_lib as L
asof = sys.argv[1] if len(sys.argv) > 1 else "2026-10-29"
rows = {}
for r in csv.DictReader(open("q_lag2.csv")):
    r = {k: (v or None) for k, v in r.items()}
    rows.setdefault(r["ticker"], []).append({"id": r["id"], "ticker": r["ticker"], "issue_method_code": r["m"],
        "issue_status_code": r["st"], "event_status": r["event_status"], "exright_date": r["ex"],
        "record_date": r["rec"], "public_date": r["pub_now"], "exercise_ratio": r["ratio"],
        "total_value": r["tv"], "issue_volumn": r["vol"]})
live = {t for t in (x["ticker"] for x in csv.DictReader(open("q_shares.csv")))}
cnt = {"CAPITAL_RAISE_PENDING": 0, "CAPITAL_RAISE_12M": 0, "any": 0}
for t in live:
    fl, _ = L.pre_entry_flags(rows.get(t, []), asof)
    for c, _e in fl:
        cnt[c] += 1
    cnt["any"] += bool(fl)
print(f"asof {asof}: mã đang GD {len(live)}; " + ", ".join(f"{k} {v} ({v/len(live):.1%})" for k, v in cnt.items()))
