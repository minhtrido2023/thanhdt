"""REDUCE/DEFER vs KEEP (baseline HYBRID) ở tầng REAL, NGOÀI MẪU so với hiệu chuẩn spread_depth_v2 (09-23).

Chỉ-đọc. Shadow là LOG-ONLY ⇒ MỌI lệnh đều chạy đúng baseline HYBRID; so sánh này trả lời
"lệnh bị policy gắn cờ có kết cục baseline TỆ HƠN lệnh KEEP không" (policy có phân biệt được cơ
hội đắt không) — KHÔNG phải phản thực "nếu REDUCE/DEFER thì tốt hơn bao nhiêu".
Đơn vị độc lập: cụm (phiên, mã) — gộp cả 2 account vì cùng mã cùng phiên chung một sổ lệnh;
cận bảo thủ: phiên. Child cùng parent KHÔNG độc lập.
"""
import sys, json, csv, os, collections, itertools, statistics as st, math
sys.path.insert(0, "mike/bin")
import order_book_shadow_probe as P
OOS_FROM = "2026-09-24"
obs = P.load_observations()
real = [r for r in obs if P.stratum(r["account"]) == "REAL" and r.get("snapshot_valid") is True]
oos = [r for r in real if r["plan_date"] >= OOS_FROM and r.get("policy_version") == "spread_depth_v2"]
print(f"REAL valid={len(real)} · OOS(v2, ≥{OOS_FROM})={len(oos)} · in-sample/v1 loại={len(real)-len(oos)}")
mk = {}
for line in open("data/execution_logs/orderbook_markout.jsonl"):
    m = json.loads(line); mk[m["trace_id"]] = m
# fill theo qty: đọc journal độc lập với probe
jr = collections.defaultdict(list)
for acct, d in {(r["account"], r["plan_date"]) for r in oos}:
    for row in csv.DictReader(open(f"data/execution_logs/exec_{acct}_{d}_journal.csv", encoding="utf-8", errors="replace")):
        if row.get("child_oid"): jr[(acct, d, str(row["child_oid"]))].append(row)
rows = []
for r in oos:
    ev = jr.get((r["account"], r["plan_date"], str(r["child_oid"])), [])
    fills = [e for e in ev if e["event"] == "FILL"]
    fq = sum(float(e["qty"] or 0) for e in fills)
    m = mk.get(r["trace_id"]) or {}
    rows.append(dict(tid=r["trace_id"], date=r["plan_date"], tk=r["ticker"], acct=r["account"], parent=r["parent_id"],
                     book=r["book"], side=r["side"], cross=r["baseline"]["cross"], qty=r["baseline"]["qty"],
                     flag=r["shadow"]["recommendation"] != "KEEP", rec=r["shadow"]["recommendation"],
                     filled=1.0 if fills else 0.0, fillq=min(1.0, fq / r["baseline"]["qty"]) if r["baseline"]["qty"] else None,
                     ttf=m.get("time_to_fill_sec"), slip=m.get("slippage_vs_limit_bps"),
                     m1=m.get("markout_1m_bps"), m5=m.get("markout_5m_bps"), m15=m.get("markout_15m_bps"),
                     basis=m.get("markout_basis"), events=[e["event"] for e in ev]))
F = [x for x in rows if x["flag"]]; K = [x for x in rows if not x["flag"]]
METRICS = [("filled", "fill-rate (child có ≥1 FILL)"), ("fillq", "fill theo KL"), ("ttf", "time-to-first-fill (s)"),
           ("slip", "slippage vs limit (bps)"), ("m1", "adverse 1m (bps)"), ("m5", "adverse 5m (bps)"), ("m15", "adverse 15m (bps)")]
def desc(g, k):
    v = [x[k] for x in g if x[k] is not None]
    return (len(v), st.mean(v), st.median(v)) if v else (0, float("nan"), float("nan"))
print(f"\nN dòng: FLAG={len(F)} KEEP={len(K)}")
cl = lambda g, key: len({key(x) for x in g})
print("N độc lập — FLAG: parent=%d · (phiên,mã)=%d · phiên=%d | KEEP: parent=%d · (phiên,mã)=%d · phiên=%d" % (
    cl(F, lambda x: (x["acct"], x["date"], x["parent"])), cl(F, lambda x: (x["date"], x["tk"])), cl(F, lambda x: x["date"]),
    cl(K, lambda x: (x["acct"], x["date"], x["parent"])), cl(K, lambda x: (x["date"], x["tk"])), cl(K, lambda x: x["date"])))
print("FLAG theo phiên:", dict(collections.Counter(x["date"] for x in F)), "| KEEP theo phiên:", dict(collections.Counter(x["date"] for x in K)))
print("FLAG book/side/cross:", dict(collections.Counter((x["book"], x["side"], x["cross"]) for x in F)))
print("KEEP book/side/cross:", dict(collections.Counter((x["book"], x["side"], x["cross"]) for x in K)))
print("basis markout FLAG:", dict(collections.Counter(x["basis"] for x in F)), "KEEP:", dict(collections.Counter(x["basis"] for x in K)))
print("\n[A] MÔ TẢ theo DÒNG (không dùng để suy luận):")
for k, lab in METRICS:
    a, b = desc(F, k), desc(K, k)
    print(f"  {lab:32s} FLAG n={a[0]:3d} mean={a[1]:8.2f} med={a[2]:8.2f} | KEEP n={b[0]:3d} mean={b[1]:8.2f} med={b[2]:8.2f}")
print("\nFLAG chi tiết:")
for x in sorted(F, key=lambda x: x["tid"]): print("  ", x["tid"], x["rec"], "filled", x["filled"], "ttf", x["ttf"], "slip", x["slip"], "m1/5/15", x["m1"], x["m5"], x["m15"], x["events"])

def exact_signflip(d):
    """p hai phía, hoán vị dấu CHÍNH XÁC trên trung bình hiệu (liệt kê đủ 2^n)."""
    n = len(d); obs_ = abs(sum(d)); cnt = 0
    for s in itertools.product((1, -1), repeat=n):
        if abs(sum(a * b for a, b in zip(s, d))) >= obs_ - 1e-12: cnt += 1
    return cnt / 2 ** n
for name, key in (("(phiên,mã)", lambda x: (x["date"], x["tk"])), ("phiên", lambda x: (x["date"],))):
    print(f"\n[B] GHÉP CẶP trong cùng cụm {name}: mean(FLAG) − mean(KEEP), chỉ cụm có CẢ HAI nhóm")
    for k, lab in METRICS:
        d = []
        for c in sorted({key(x) for x in F}):
            f = [x[k] for x in F if key(x) == c and x[k] is not None]; q = [x[k] for x in K if key(x) == c and x[k] is not None]
            if f and q: d.append(st.mean(f) - st.mean(q))
        if not d: print(f"  {lab:32s} cặp=0"); continue
        pos, neg = sum(v > 1e-9 for v in d), sum(v < -1e-9 for v in d)
        p = exact_signflip(d) if len(d) <= 16 else float("nan")
        print(f"  {lab:32s} cặp={len(d):2d} meanΔ={st.mean(d):+8.2f} medΔ={st.median(d):+8.2f} (+{pos}/−{neg}/0:{len(d)-pos-neg}) p_exact_signflip={p:.3f} · p nhỏ nhất đạt được với n này={2/2**len(d):.3f}")
json.dump(rows, open(os.path.join(os.path.dirname(__file__), "oos_rows.json"), "w"), ensure_ascii=False, indent=0)
