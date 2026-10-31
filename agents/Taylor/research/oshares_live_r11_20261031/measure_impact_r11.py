"""R11 impact: plan echo / EOD / paper — trước (main: không khai price_date) vs sau (khớp giá↔phiên cache).

Replay ĐÚNG khung cache lúc job chạy thật (sync BQ cache 23:45 ICT):
  - plan echo 21:00 ngày T-1 (plan_date=T): cache có tới phiên TRƯỚC signal_date ⇒ cutoff = phiên < signal_date
  - EOD 19:10 ngày T: cache có tới T-1 ⇒ cutoff = phiên < plan_date
Khớp: price_session_for(ticker, cutoff, ref_price) (chỉ nhìn phiên <= cutoff), rồi
_dcf_check_for_order(ticker, ref_price, plan_date, price_date=<phiên khớp | UNKNOWN>) — đúng lời gọi caller.
Trước = _dcf_check_for_order(ticker, ref_price, plan_date) (main, price_date=None).
Chạy: python3 run_wt.py <WT> measure_impact_r11.py [YYYY-MM-DD đầu]   (knob = live như PROD)."""
import csv, glob, json, os, sys
import duckdb, pandas as pd
import dcf_valuation as dv, oshares_dcf
from trading_bot.strategies import _dcf_check_for_order, format_dcf_check

OUT = os.path.dirname(os.path.abspath(__file__))
D0 = sys.argv[1] if len(sys.argv) > 1 else "2026-09-01"
PLANS = "/home/trido/thanhdt/WorkingClaude/data/trade_plans"
assert dv.OSHARES_SOURCE == "live", dv.OSHARES_SOURCE

sess = [d.date().isoformat() for d in duckdb.sql(
    f"SELECT DISTINCT time FROM read_parquet('{dv.WORKDIR}/data/bq_cache/ticker/2026.parquet') "
    f"WHERE ticker='VNINDEX' ORDER BY time").df().time]


def prev_sess(d):
    p = [s for s in sess if s < d]
    return p[-1] if p else None


rows = []
for p in sorted(glob.glob(f"{PLANS}/plan_*_2026-*.json")):
    d = json.load(open(p))
    acct, pdate, sig = d.get("account"), d.get("plan_date"), d.get("signal_date")
    if not pdate or pdate < D0:
        continue
    for o in d.get("orders", []):
        px = o.get("ref_price")
        if str(o.get("side", "")).lower() != "buy" or o.get("dcf_check") or not isinstance(px, (int, float)) or not px:
            continue
        rows.append(dict(acct=acct, plan_date=pdate, signal_date=sig, ticker=o["ticker"], px=float(px)))
print(f"{len(rows)} BUY (plan_date >= {D0}), {len({r['ticker'] for r in rows})} ma", file=sys.stderr)
oshares_dcf.prime(sorted({r["ticker"] for r in rows}), max(r["plan_date"] for r in rows))


def summ(c):
    s = format_dcf_check(c, "buy", ticker=None) if c else ""
    return (c or {}).get("status"), (c or {}).get("margin_of_safety"), (c or {}).get("robust"), \
        ("cần dcf_override_reason" in s), s


out = []
for r in rows:
    before = _dcf_check_for_order(r["ticker"], r["px"], r["plan_date"])
    for leg, cut in (("plan_echo", prev_sess(r["signal_date"] or r["plan_date"])), ("eod", prev_sess(r["plan_date"]))):
        pd_ = dv.price_session_for(r["ticker"], cut, r["px"]) if cut else dv.PRICE_SESSION_UNKNOWN
        after = _dcf_check_for_order(r["ticker"], r["px"], r["plan_date"], price_date=pd_)
        b, a = summ(before), summ(after)
        out.append({**r, "leg": leg, "cutoff": cut, "price_date": pd_,
                    "st_b": b[0], "st_a": a[0], "mos_b": b[1], "mos_a": a[1], "rb_b": b[2], "rb_a": a[2],
                    "rich_b": b[3], "rich_a": a[3], "line_b": b[4], "line_a": a[4],
                    "identical": json.dumps(before, sort_keys=True, default=str) == json.dumps(after, sort_keys=True, default=str)})

with open(f"{OUT}/out_impact_r11_plans.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)

df = pd.DataFrame(out)
summary = {}
for leg, g in df.groupby("leg"):
    m = g[g.price_date != dv.PRICE_SESSION_UNKNOWN]
    summary[leg] = {
        "n_buy": int(len(g)), "n_matched": int(len(m)),
        "n_unmatched_identical": int(g[g.price_date == dv.PRICE_SESSION_UNKNOWN].identical.sum()),
        "n_unmatched": int((g.price_date == dv.PRICE_SESSION_UNKNOWN).sum()),
        "n_changed_any": int((~g.identical).sum()),
        "n_changed_mos": int((g.mos_b.fillna(-9e9) != g.mos_a.fillna(-9e9)).sum()),
        "n_changed_status": int((g.st_b != g.st_a).sum()),
        "n_changed_robust": int((g.rb_b != g.rb_a).sum()),
        "n_rich_flag_b": int(g.rich_b.sum()), "n_rich_flag_a": int(g.rich_a.sum()),
        "rich_flag_lost": int((g.rich_b & ~g.rich_a).sum()), "rich_flag_gained": int((~g.rich_b & g.rich_a).sum()),
        "status_flips": sorted({f"{x.ticker} {x.plan_date} {x.st_b}->{x.st_a}" for x in g[g.st_b != g.st_a].itertuples()}),
        "mos_changes": sorted({f"{x.ticker} {x.plan_date} {x.mos_b}->{x.mos_a}" for x in g[g.mos_b.fillna(-9e9) != g.mos_a.fillna(-9e9)].itertuples()}),
    }
both = df.pivot_table(index=["acct", "plan_date", "ticker", "px"], columns="leg", values="line_a", aggfunc="first")
summary["plan_echo_vs_eod_line_differs"] = int((both["plan_echo"] != both["eod"]).sum())
summary["plan_echo_vs_eod_examples"] = [f"{i[0]} {i[1]} {i[2]}: plan='{r.plan_echo}' eod='{r.eod}'"
                                        for i, r in both[both["plan_echo"] != both["eod"]].head(12).iterrows()]
json.dump(summary, open(f"{OUT}/impact_r11_summary.json", "w"), ensure_ascii=False, indent=1, default=str)
print(json.dumps(summary, ensure_ascii=False, indent=1, default=str))
