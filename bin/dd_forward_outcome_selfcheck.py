#!/usr/bin/env python3
"""Selfcheck dd_forward_outcome: (A) logic tổng hợp, (B) tái lập TAY 2 entry thật với h=5,10 qua đường BQ độc lập."""
import os, sys, subprocess, csv, io, tempfile
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dd_forward_outcome as m

fail = []
def check(name, cond, info=""):
    print(("PASS " if cond else "FAIL ") + name, info)
    if not cond: fail.append(name)

# (A) tổng hợp
ents = [dict(ticker="AAA", dd_date="2026-01-05", rev=1, recorded_at="2026-01-05T20:00:00+07:00", center=100, price_ref=80, price_date="2026-01-05", zone_low=70, zone_high=120),
        dict(ticker="AAA", dd_date="2026-01-05", rev=2, recorded_at="2026-01-06T20:00:00+07:00", center=90, price_ref=81, price_date="2026-01-06", zone_low=70, zone_high=120),
        dict(ticker="BBB", dd_date="2026-01-05", rev=None, recorded_at="2026-01-05T08:00:00+07:00", center=None, price_ref=50, price_date="2026-01-05")]
pk = m.pick_last(ents)
check("pick_last lấy rev cao nhất", [(e["ticker"], e.get("rev")) for e in pk] == [("AAA", 2), ("BBB", None)])
check("r_bin biên 0.85 thuộc luật 4", m.r_bin(0.85).startswith("r<=0.85") and m.r_bin(0.8501).startswith("0.85<") and m.r_bin(1.0).startswith("0.85<") and m.r_bin(1.01) == "r>1.0")
check("zone cơ học", m.zone_label(dict(price_ref=60, zone_low=70, zone_high=120)) == "DUOI" and m.zone_label(dict(price_ref=130, zone_low=70, zone_high=120)) == "TREN" and m.zone_label(dict(price_ref=1)) == "KHONG_RO")
cal = ["2026-01-%02d" % d for d in (5, 6, 7, 8, 9, 12, 13, 14)]
ser = {"VNINDEX": {d: (1000.0 + i * 10, None) for i, d in enumerate(cal)},
       "AAA": {d: (100.0 + i, None) for i, d in enumerate(cal)}}
vtr = {d: 2000.0 + i * 20 for i, d in enumerate(cal)}
rows = m.compute(pk[:1], ser, vtr, (2, 5, 10))
r = rows[0]
# anchor = 2026-01-06 (recorded) ⇒ phiên vào = 01-07 (i=2); h2 → 01-09 (i=4)
check("phiên vào = phiên SAU ngày neo (T+1)", r["entry_session"] == "2026-01-07", r["entry_session"])
check("ret h2 = 104/102-1", abs(r["ret_2"] - (104 / 102 - 1)) < 1e-5, r["ret_2"])
check("excess h2 = ret - VNI TR", abs(r["excess_2"] - (104 / 102 - 1 - (2080 / 2040 - 1))) < 1e-5)
check("h5 → i=7 đủ kỳ; h10 chưa đủ", r["st_5"] == "ok" and r["st_10"] == "chua_du")
check("hôm nay không tự là phiên vào", m.compute(pk[:1], {"VNINDEX": {"2026-01-06": (1, None)}, "AAA": {}}, {}, (2,))[0]["entry_session"] == "")

# (B) tái lập tay 2 entry thật, h=5,10 — đường BQ độc lập (mỗi mã 1 truy vấn riêng, tính tay)
LEDGER = m.DEF_LEDGER
picked = {(e["ticker"], e["dd_date"]): e for e in m.pick_last(m.load_entries(LEDGER))}
pairs = [("NT2", "2026-10-26"), ("DRI", "2026-11-03")]
out = tempfile.mkdtemp()
def bq(sql):
    cmd = "source %s/wc_env.sh >/dev/null 2>&1; bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=100000 \"$SQL\"" % m.WC
    p = subprocess.run(["bash", "-c", cmd], env=dict(os.environ, SQL=sql), capture_output=True, text=True)
    return list(csv.DictReader(io.StringIO(p.stdout)))
vni = [(x["d"], float(x["c"])) for x in bq("SELECT FORMAT_DATE('%F',t.time) d, t.Close c FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time>='2026-10-01' ORDER BY t.time")]
trs = {r["date"]: float(r["tr_gross"]) for r in csv.DictReader(open(m.VNI_TR))}
pk2 = [picked[k] for k in pairs]
series = {"VNINDEX": dict((d, (c, None)) for d, c in vni)}
for t, _ in pairs:
    series[t] = {x["d"]: (float(x["c"]), None) for x in bq("SELECT FORMAT_DATE('%%F',t.time) d, t.Close c FROM tav2_bq.ticker AS t WHERE t.ticker='%s' AND t.time>='2026-10-01'" % t)}
prog = m.compute(pk2, series, trs, (5, 10))
for e, row in zip(pk2, prog):
    # tay: ngày neo
    a = max(x for x in (e["dd_date"], e["price_date"], e["recorded_at"][:10]) if x)
    days = [d for d, _ in vni]
    i = next(k for k, d in enumerate(days) if d > a)
    for h in (5, 10):
        if i + h >= len(days):
            check("%s h%d chưa đủ" % (e["ticker"], h), row["st_%d" % h] == "chua_du"); continue
        c0 = series[e["ticker"]][days[i]][0]; c1 = series[e["ticker"]][days[i + h]][0]
        hand = c1 / c0 - 1
        check("%s h%d tay=%.5f vs script=%s" % (e["ticker"], h, hand, row.get("ret_%d" % h)), abs(hand - row["ret_%d" % h]) < 1e-4)
        vh = trs[days[i + h]] / trs[days[i]] - 1
        check("%s h%d excess" % (e["ticker"], h), abs((hand - vh) - row["excess_%d" % h]) < 1e-4)
print("TỔNG: %s" % ("PASS" if not fail else "FAIL %s" % fail))
sys.exit(1 if fail else 0)
