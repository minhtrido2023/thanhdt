"""R12 impact + đếm BQ đường plan echo (job Taylor_20261031_092209).

plan echo: exec CHÍNH khối DCF của mike/bin/send_plan_report.sh (worktree R12) rồi gọi _dcf_timed(ticker,
ref_price, plan_date) cho mọi lệnh MUA plan_date >= D0 — KHÔNG prime trước; mọi điểm vào BQ (oshares_for,
fetch_cache, pricing_events, oshares_live._fetch, prime, google.cloud.bigquery.Client.query) bị đếm + chặn.
EOD: như R11 (khớp phiên ở cutoff phiên < plan_date) + format R12 (nhãn số quý).
So với: main (price_date=None) và R11 (out_impact_r11_plans.csv, cột line_a).
Chạy: python3 run_wt.py <WT> measure_impact_r12.py <send_plan_report.sh> [D0]"""
import csv, glob, io, json, os, sys, textwrap, contextlib
import duckdb, pandas as pd
import dcf_valuation as dv, oshares_dcf as osd, oshares_live as ol
import trading_bot.strategies as st

OUT = os.path.dirname(os.path.abspath(__file__))
SP = sys.argv[1]
D0 = sys.argv[2] if len(sys.argv) > 2 else "2026-09-01"
R11 = "/home/trido/wt-oshares-r11-ops-20261031/agents/Taylor/research/oshares_live_r11_20261031/out_impact_r11_plans.csv"
PLANS = "/home/trido/thanhdt/WorkingClaude/data/trade_plans"
assert dv.OSHARES_SOURCE == "live", dv.OSHARES_SOURCE

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
print(f"{len(rows)} BUY (plan_date >= {D0})", file=sys.stderr)

# ---- plan echo: khối thật của send_plan_report.sh, đếm BQ
src = open(SP, encoding="utf-8").read()
i = src.index("    _dcf_pd_kw = {}"); j = src.index("    # Due-diligence tổng hợp", i)
blk = textwrap.dedent(src[i:j])
calls = {}


def counter(name):
    def f(*a, **k):
        calls[name] = calls.get(name, 0) + 1
        raise RuntimeError(f"BQ chặn (đếm): {name}")
    return f


patch = [(osd, "oshares_for"), (osd, "fetch_cache"), (osd, "pricing_events"), (osd, "prime"), (ol, "_fetch"),
         (dv, "price_session_for"), (dv, "price_sessions_for")]
try:
    from google.cloud import bigquery as _bq
    patch.append((_bq.Client, "query"))
except Exception:                                  # noqa: BLE001
    pass
saved = [(m, a, getattr(m, a)) for m, a in patch]
for m, a in patch:
    setattr(m, a, counter(f"{getattr(m, '__name__', m)}.{a}"))
ns = {"os": os, "format_dcf_check": st.format_dcf_check, "_dcf_check_for_order": st._dcf_check_for_order}
err = io.StringIO()
try:
    with contextlib.redirect_stderr(err):
        exec(blk, ns)
        plan = [ns["_dcf_timed"](r["ticker"], r["px"], r["plan_date"]) for r in rows]
finally:
    for m, a, f in saved:
        setattr(m, a, f)
n_bq = sum(calls.values())
print(f"plan echo: BQ/khớp-phiên calls = {n_bq} {calls}; timeouts={ns['_dcf_timeouts']}; stderr '!!!!!' = "
      f"{err.getvalue().count('!!!!!')}", file=sys.stderr)

# ---- main (None) + EOD (R11 khớp phiên + format R12)
with contextlib.redirect_stderr(io.StringIO()):
    main = [st._dcf_check_for_order(r["ticker"], r["px"], r["plan_date"]) for r in rows]
sess = [d.date().isoformat() for d in duckdb.sql(
    f"SELECT DISTINCT time FROM read_parquet('{dv.WORKDIR}/data/bq_cache/ticker/2026.parquet') "
    f"WHERE ticker='VNINDEX' ORDER BY time").df().time]
prev = lambda d: ([s for s in sess if s < d] or [None])[-1]
osd.prime(sorted({r["ticker"] for r in rows}), max(r["plan_date"] for r in rows))
with contextlib.redirect_stderr(io.StringIO()):
    eod = []
    for r in rows:
        cut = prev(r["plan_date"])
        pd_ = dv.price_session_for(r["ticker"], cut, r["px"]) if cut else dv.PRICE_SESSION_UNKNOWN
        eod.append(st._dcf_check_for_order(r["ticker"], r["px"], r["plan_date"], price_date=pd_))

r11 = {}
for x in csv.DictReader(open(R11, encoding="utf-8")):
    r11.setdefault((x["acct"], x["plan_date"], x["ticker"], float(x["px"]), x["leg"]), x["line_a"])
fmt = lambda c: st.format_dcf_check(c, "buy", ticker=None) if c else ""
js = lambda c: json.dumps(c, sort_keys=True, default=str)
out = []
for r, p, m, e in zip(rows, plan, main, eod):
    k = (r["acct"], r["plan_date"], r["ticker"], r["px"])
    out.append({**r, "plan_line": fmt(p), "plan_line_r11": r11.get(k + ("plan_echo",)), "main_line": fmt(m),
                "plan_eq_main_dict": js(p) == js(m), "eod_line": fmt(e), "eod_line_r11": r11.get(k + ("eod",)),
                "eod_label": "cơ sở plan echo" in fmt(e)})
with open(f"{OUT}/out_impact_r12_plans.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
df = pd.DataFrame(out)
spz = df.acct.isin(["SpaceX", "ZaloPay"])
s = {
    "n_buy": len(df), "plan_echo_bq_calls": n_bq, "plan_echo_calls_by_fn": calls,
    "plan_echo_timeouts": ns["_dcf_timeouts"], "plan_echo_stderr_shouts": err.getvalue().count("!!!!!"),
    "plan_echo_dict_identical_main": int(df.plan_eq_main_dict.sum()),
    "plan_echo_line_identical_main": int((df.plan_line == df.main_line).sum()),
    "plan_echo_line_changed_vs_r11": int((df.plan_line != df.plan_line_r11).sum()),
    "plan_echo_changed_vs_r11_examples": [f"{x.ticker} {x.plan_date}: r11='{x.plan_line_r11}' r12='{x.plan_line}'"
                                          for x in df[df.plan_line != df.plan_line_r11].head(6).itertuples()],
    "eod_line_changed_vs_r11": int((df.eod_line != df.eod_line_r11).sum()),
    "eod_label_rows": int(df.eod_label.sum()), "eod_label_rows_spacex_zalopay": int((df.eod_label & spz).sum()),
    "eod_label_tickers": sorted(set(df[df.eod_label].ticker)),
    "eod_changed_only_by_label": int(((df.eod_line != df.eod_line_r11)
                                      & (df.eod_line.str.split(" · số CP quý").str[0] == df.eod_line_r11)).sum()),
    "eod_label_examples": [f"{x.acct} {x.ticker} {x.plan_date}: {x.eod_line}" for x in df[df.eod_label].head(4).itertuples()],
    "plan_echo_vs_eod_line_differs": int((df.plan_line != df.eod_line).sum()),
}
json.dump(s, open(f"{OUT}/impact_r12_summary.json", "w"), ensure_ascii=False, indent=1, default=str)
print(json.dumps(s, ensure_ascii=False, indent=1, default=str))
