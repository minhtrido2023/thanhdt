"""Đo THẬT: |q.ref (secdef basicPrice, DNSE live) − close phiên hoàn tất gần nhất| / close.
Đây là đại lượng mà dung sai của guard PHẢI dung nạp (nhiễu lành tính), tách khỏi cái nó
PHẢI bắt (plan trễ 1 phiên, corp-action, sai đơn vị)."""
import datetime as dt, json, sys
from zoneinfo import ZoneInfo
from trading_bot.brokers import DNSEBroker

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
tickers = sys.argv[1].split(",")
b = DNSEBroker(quote_only=True).connect()
to_ts = int(dt.datetime(2026, 8, 15, 20, 0, tzinfo=ICT).timestamp())
fr = to_ts - 30 * 86400
out = []
for t in tickers:
    try:
        q = b.get_quote(t)
        raw = b.client.ohlc(t, resolution="1D", **{"from": fr, "to": to_ts})
        c = raw.get("c") or []
        ts = raw.get("t") or []
        if not c or q.ref is None:
            out.append({"ticker": t, "ref": q.ref, "close": None, "dev": None}); continue
        # bar cuối = phiên 08-14 (đã đóng, hôm nay T7 không có bar mới)
        last_close = float(c[-1]) * 1000.0
        last_date = dt.datetime.fromtimestamp(int(ts[-1]), ICT).date().isoformat()
        dev = q.ref / last_close - 1.0
        out.append({"ticker": t, "ref": q.ref, "close": last_close, "close_date": last_date,
                    "dev_pct": round(dev * 100, 4), "last": q.last,
                    "ce": q.ceiling, "fl": q.floor})
    except Exception as e:
        out.append({"ticker": t, "err": f"{type(e).__name__}: {e}"})
json.dump(out, open("mike/agents/Taylor/research/rule_a_ref_guard_20260815/ref_vs_close_probe.json", "w"),
          ensure_ascii=False, indent=1)
ok = [r for r in out if r.get("dev_pct") is not None]
ok.sort(key=lambda r: abs(r["dev_pct"]))
print(f"N={len(ok)}/{len(tickers)}")
for r in ok:
    print(f"  {r['ticker']:<5} ref={r['ref']:>10,.0f}  close={r['close']:>10,.0f}  dev={r['dev_pct']:+7.3f}%")
import statistics as st
a = [abs(r["dev_pct"]) for r in ok]
a.sort()
def pct(p):
    return a[min(len(a) - 1, int(round(p * (len(a) - 1))))]
print(f"\n|dev|: 0%={sum(1 for x in a if x==0)}/{len(a)} exact | median={st.median(a):.3f}% "
      f"p90={pct(.90):.3f}% p95={pct(.95):.3f}% max={a[-1]:.3f}%")
for thr in (0.25, 0.5, 1.0, 1.5, 2.0, 3.0):
    print(f"  |dev| > {thr:>4.2f}%: {sum(1 for x in a if x > thr):>3}/{len(a)}")
