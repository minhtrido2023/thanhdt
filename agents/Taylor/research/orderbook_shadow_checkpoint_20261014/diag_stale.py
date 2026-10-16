"""Vì sao source_age>5s: đọc raw quote_l2 (dnse_raw) + so invalid vs valid. Chỉ-đọc."""
import json, os, sys, collections, statistics as st
sys.path.insert(0, "mike/bin")
import order_book_shadow_probe as P
obs = P.load_observations()
real = [r for r in obs if P.stratum(r.get("account")) == "REAL"]
dates = sorted({r["plan_date"] for r in real})
# 1) raw L2: phân bố source_age theo mã và theo khung giờ, cho MỌI bản ghi quote_l2 (không chỉ lúc đặt lệnh)
raw = collections.defaultdict(list); nlev = collections.Counter(); tstat = collections.Counter()
seq = collections.defaultdict(list)
for d in dates:
    p = f"data/execution_logs/dnse_raw_{d}.jsonl"
    if not os.path.exists(p): print("MISSING", p); continue
    for line in open(p, encoding="utf-8", errors="replace"):
        if '"quote_l2"' not in line: continue
        try: row = json.loads(line)
        except Exception: continue
        if row.get("kind") != "quote_l2": continue
        s = row.get("payload") or {}
        tstat[s.get("source_time_status")] += 1
        nlev[(s.get("n_bid"), s.get("n_offer"))] += 1
        a = s.get("source_age_ms")
        if a is None: continue
        hhmm = (s.get("captured_at") or "")[11:16]
        raw[s.get("symbol")].append((hhmm, a))
        seq[(d, s.get("symbol"))].append((s.get("captured_at"), s.get("source_ts"), json.dumps([s.get("bids"), s.get("offers"), s.get("last"), s.get("day_volume")])))
print("raw quote_l2 source_time_status:", dict(tstat))
print("raw levels (n_bid,n_offer) top:", nlev.most_common(5))
allr = [x for v in raw.values() for x in v]
def bucket(h):
    if h < "09:15": return "pre-open"
    if h == "09:15": return "09:15"
    if h in ("10:00",): return "10:00"
    if "11:30" <= h < "13:00": return "lunch"
    if h in ("13:00",): return "13:00"
    if h >= "14:30": return "ATC+"
    return "continuous-other"
bk = collections.defaultdict(list)
for h, a in allr: bk[bucket(h)].append(a)
print("RAW stale-rate (>5s) theo khung giờ — mọi snapshot, không riêng lúc đặt lệnh:")
for k, v in sorted(bk.items()): print(f"   {k:18s} n={len(v):6d} stale={sum(a>5000 for a in v)/len(v):6.1%} median_age={st.median(v):.0f}ms")
print("RAW stale-rate theo mã (mã có lệnh REAL):")
tk = sorted({r["ticker"] for r in real})
for t in tk:
    v = [a for h, a in raw.get(t, []) if "09:15" <= h < "11:30" or "13:00" <= h < "14:30"]
    if v: print(f"   {t} n={len(v)} stale={sum(a>5000 for a in v)/len(v):.1%} med={st.median(v):.0f}")
# 2) source_ts có đứng yên khi sổ không đổi không? (bằng chứng 'age = thời gian từ lần cập nhật sổ gần nhất')
same_ts_same_book = same_ts_diff_book = diff_ts = 0
for k, v in seq.items():
    v.sort()
    for (c1, s1, b1), (c2, s2, b2) in zip(v, v[1:]):
        if s1 == s2:
            if b1 == b2: same_ts_same_book += 1
            else: same_ts_diff_book += 1
        else: diff_ts += 1
print(f"cặp snapshot liên tiếp cùng mã: source_ts KHÔNG đổi & sổ y hệt={same_ts_same_book} · source_ts KHÔNG đổi nhưng sổ khác={same_ts_diff_book} · source_ts đổi={diff_ts}")
# 3) invalid vs valid ở tầng REAL
cfg = dict(rs=1.0, rd=2.0, ds=2.0, dd=1.0)
def would(r):
    f = r.get("features") or {}
    s, d = f.get("spread_ticks"), f.get("touch_depth_ratio")
    if s is None or d is None: return "NA"
    if s >= cfg["ds"] and d < cfg["dd"]: return "DEFER"
    if s >= cfg["rs"] and d < cfg["rd"]: return "REDUCE"
    return "KEEP"
inv = [r for r in real if r.get("snapshot_valid") is not True]; val = [r for r in real if r.get("snapshot_valid") is True]
for name, g in (("INVALID", inv), ("VALID", val)):
    d = [r["features"]["touch_depth_ratio"] for r in g if (r.get("features") or {}).get("touch_depth_ratio") is not None]
    s = [r["features"]["spread_ticks"] for r in g if (r.get("features") or {}).get("spread_ticks") is not None]
    print(name, "n", len(g), "would-be v2:", dict(collections.Counter(would(r) for r in g)),
          "| actual:", dict(collections.Counter(r["shadow"]["recommendation"] for r in g)),
          f"| depth med={st.median(d):.1f} p25={st.quantiles(d, n=4)[0]:.1f} | spread_ticks med={st.median(s)} mean={st.mean(s):.2f}",
          "| 09:15 share", f"{sum(r['recorded_at'][11:16]=='09:15' for r in g)/len(g):.0%}",
          "| pv", dict(collections.Counter(r.get('policy_version') for r in g)))
print("invalid rate by book:", {b: f"{sum(1 for r in inv if r.get('book')==b)}/{sum(1 for r in real if r.get('book')==b)}" for b in sorted({r.get('book') for r in real})})
print("invalid rate by date:", {d: f"{sum(1 for r in inv if r['plan_date']==d)}/{sum(1 for r in real if r['plan_date']==d)}" for d in dates})
print("latency of invalid (ms):", sorted(r.get("latency_snapshot_to_order_ms") for r in inv)[-5:], "→ latency_ok cho tất cả?", all((r.get("latency_snapshot_to_order_ms") or 0) <= 5000 for r in inv))
big = sorted(inv, key=lambda r: -r["snapshot"]["source_age_ms"])[:6]
for r in big: print("  oldest:", r["trace_id"], r["recorded_at"][11:19], "src", r["snapshot"]["source_ts"][11:19], r["snapshot"]["source_age_ms"])
