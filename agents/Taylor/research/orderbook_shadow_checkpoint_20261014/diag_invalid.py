"""Chẩn đoán bản ghi REAL snapshot_valid=False — đọc thẳng telemetry, chỉ-đọc."""
import glob, json, os, collections, sys
sys.path.insert(0, "mike/bin")
import order_book_shadow_probe as P
obs = P.load_observations()
real = [r for r in obs if P.stratum(r.get("account")) == "REAL"]
inv = [r for r in real if r.get("snapshot_valid") is not True]
val = [r for r in real if r.get("snapshot_valid") is True]
print("REAL", len(real), "valid", len(val), "invalid", len(inv))
C = collections.Counter
print("by date/account:", sorted(C((r["plan_date"], r["account"]) for r in inv).items()))
print("all REAL by date/account:", sorted(C((r["plan_date"], r["account"]) for r in real).items()))
print("reason:", C((r.get("shadow") or {}).get("reason") for r in inv))
print("policy_version:", C(r.get("policy_version") for r in inv))
def snapinfo(r):
    s = r.get("snapshot") or {}
    return (s.get("source_time_status"), bool(s.get("bids")), bool(s.get("offers")), s.get("board_id"),
            None if s.get("source_age_ms") is None else ("<=5s" if s["source_age_ms"] <= 5000 else ">5s"))
print("snapshot (time_status,hasbid,hasoffer,board,age):")
for k, v in C(snapinfo(r) for r in inv).most_common(): print("  ", k, v)
print("same for VALID:")
for k, v in C(snapinfo(r) for r in val).most_common(): print("  ", k, v)
print("invalid keys of snapshot:", C(tuple(sorted((r.get("snapshot") or {}).keys())) for r in inv).most_common(4))
print("book/side:", C((r.get("book"), r.get("side")) for r in inv), "| valid:", C((r.get("book"), r.get("side")) for r in val))
print("ticker:", C(r["ticker"] for r in inv).most_common())
print("hour:", sorted(C(r["recorded_at"][11:16] for r in inv).items()))
ages = sorted((r.get("snapshot") or {}).get("source_age_ms") for r in inv if (r.get("snapshot") or {}).get("source_age_ms") is not None)
if ages: print("age_ms min/med/max", ages[0], ages[len(ages)//2], ages[-1], "n", len(ages))
for r in inv[:3] + inv[-2:]:
    print(json.dumps({k: r.get(k) for k in ("trace_id","recorded_at","baseline","shadow","features","snapshot","latency_snapshot_to_order_ms")}, ensure_ascii=False)[:1200])
