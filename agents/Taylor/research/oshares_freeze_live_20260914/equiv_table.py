"""Bảng đối chiếu từng lời gọi: BQ SỐNG (code gốc bc86963e) vs FEED ĐÓNG BĂNG (code mới, BQ bị chặn)."""
import json
rows = ["| # | module | hàm | mã | asof | live | trạng thái cổng | value | method | anchor | events | verdict nhánh | output đầy đủ trùng |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
tot = same = 0
for mod, b, n in (("live", "base_live_live.json", "new_live_blocked.json"), ("pit", "base_pit_live.json", "new_pit_blocked.json")):
    B, N = json.load(open(b))["calls"], json.load(open(n))["calls"]
    assert len(B) == len(N)
    for i, (x, y) in enumerate(zip(B, N)):
        ax = {k: v for k, v in x["args"].items() if k not in ("cached", "n_corp")}
        ay = {k: v for k, v in y["args"].items() if k not in ("cached", "n_corp")}
        eq = ax == ay and x["state"] == y["state"] and x["out"] == y["out"] and x["err"] == y["err"]
        tot += 1; same += eq
        s = x["state"]; st = ",".join(t for t, c in (("serve+UNVERIFIED", len(s["serve"]) > 2), ("fallback-off", s["age"] > 90),
                                                  ("verdicts-boom", s["verdicts_fn"] != "_ais_verdicts"), ("fwd-off", s["fwd_fn"] != "_forward_absorption_test")) if c) or "-"
        o = x["out"] or {}
        tks = ax.get("tickers") or [ax.get("ticker")]
        if x["fn"] == "_ais_verdicts":
            rows.append(f"| {tot} | {mod} | _ais_verdicts | {tks[0]} | {ax['asof']} | - | {st} | - | - | - | - | {len(o)} verdict: {sum(v=='OK' for v in o.values())} OK / {sum(v=='UNVERIFIED' for v in o.values())} UNVERIFIED | {'✓' if eq else '✗'} |")
            continue
        for t in tks:
            r = o.get(t) or {}
            fwd = (r.get("forward_absorption") or {}).get("verdict"); ab = (r.get("absorption_test") or {}).get("verdict")
            vv = ",".join(v for v in (fwd, ab) if v) or "-"
            val = r.get("value"); val = f"{val:,.0f}" if isinstance(val, (int, float)) else str(val)
            rows.append(f"| {tot} | {mod} | {x['fn']} | {t} | {ax['asof']} | {ax.get('live', '-')} | {st} | {val} | {r.get('method', r.get('source', '-'))} | {r.get('anchor_date', '-')} | {len(r.get('events_applied') or [])} | {vv} | {'✓' if eq else '✗'} |")
open("equivalence_table.md", "w").write(f"# Bảng tương đương — {same}/{tot} lời gọi tầng ngoài trùng khít (full JSON output)\n\n"
    "Trái: selfcheck code gốc bc86963e trên BQ SỐNG 2026-09-14/15. Phải: code branch `test/oshares-freeze-live-selfchecks` "
    "trên `oshares_selfcheck_fixture`, BQ BỊ CHẶN (capture.py mode=blocked). So toàn bộ dict output, không chỉ các cột dưới.\n\n" + "\n".join(rows) + "\n")
print(same, tot)
