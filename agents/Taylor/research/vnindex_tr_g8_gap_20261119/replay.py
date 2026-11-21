"""Dựng lại TRONG BỘ NHỚ như --update (không ghi chuỗi nào; chỉ đọc data/benchmark/) bằng code WORKTREE +
cache BQ bq_inputs_20251103.pkl; chạy check_period cũ (chuỗi canonical) vs mới (chuỗi dựng lại) cho 2 kỳ."""
import sys, pickle, hashlib, json, io, contextlib
sys.path.insert(0, sys.argv[1] + "/bin")
import vnindex_total_return as V
D = __file__.rsplit("/", 1)[0]
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
h0 = md5(V.SERIES_PATH)
inp = pickle.load(open(f"{D}/bq_inputs_20251103.pkl", "rb"))
inp["first_seen"] = {r["ticker"]: r["first_time"] for r in inp["first_seen"]}
lines = V._raw_lines(V.SERIES_PATH)
old = V._parse_lines(lines, V.SERIES_PATH)
acks = V.load_acks(V.ACKS_PATH)
sealed_idx = [i for i, r in enumerate(old) if r["status"] == "sealed"]
k = sealed_idx[max(len(sealed_idx) - 1 - V.VERIFY_SEALED, 0)]
src2 = {r["date"]: r["vnindex_src2"] for r in old if r["vnindex_src2"] is not None}
since, rebuilt, _ = V._rebuild(old, k, V.MEMBERSHIP_LATEST, inp, src2, old[-1]["built_at_ict"], V.FIRST_DATE)
drift = []
new_bytes, blocked = V._merge_lines(lines, rebuilt, acks, "replay", warn=drift)
new = V._parse_lines(new_bytes.decode().splitlines(keepends=True), "replay")
open(f"{D}/series_replay.csv", "wb").write(new_bytes)
out = {"anchor": since.isoformat(), "rebuilt": len(rebuilt), "seal_blocked": blocked, "sealed_drift_warnings": drift}
for r in new:
    if r["date"] >= since and r["g8_new"]:
        out.setdefault("g8_new_by_date", {})[r["date"].isoformat()] = [":".join(t) for t in r["g8_new"]]
for a, b in (("2026-11-06", "2026-11-18"), ("2026-11-12", "2026-11-18")):
    eo, en = V.check_period(old, a, b, acks), V.check_period(new, a, b, acks)
    bo, bn = V.benchmark_period(a, b, series=old), V.benchmark_period(a, b, series=new)
    out[f"{a}->{b}"] = {
        "old_errs": eo, "new_errs": en,
        "G5_old": [e for e in eo if e.startswith("G5")], "G5_new": [e for e in en if e.startswith("G5")],
        "G8_new_only": [e for e in en if e.startswith("G8") and e not in eo],
        "bench_old": {k2: bo[k2] for k2 in ("status", "vnindex_price_pct", "vnindex_tr_net_pct")},
        "bench_new": {k2: bn[k2] for k2 in ("status", "vnindex_price_pct", "vnindex_tr_net_pct")}}
assert md5(V.SERIES_PATH) == h0, "chuỗi canonical đổi!"
out["canonical_md5_unchanged"] = h0
json.dump(out, open(f"{D}/replay_result.json", "w"), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k2: v for k2, v in out.items() if not k2.startswith("2026")}, ensure_ascii=False, indent=1, default=str)[:3000])
for p in ("2026-11-06->2026-11-18", "2026-11-12->2026-11-18"):
    o = out[p]
    print(p, "| G5 cũ:", len(o["G5_old"]), "G5 mới:", len(o["G5_new"]), "G5 giống hệt:", o["G5_old"] == o["G5_new"],
          "| G8 mới:", len(o["G8_new_only"]), "| bench cũ", o["bench_old"], "mới", o["bench_new"])
    print("  lỗi cũ theo cổng:", sorted({e[:2] for e in o["old_errs"]}), "mới:", sorted({e[:2] for e in o["new_errs"]}))
