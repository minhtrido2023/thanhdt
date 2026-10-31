#!/usr/bin/env python3
"""R8 bước 7 (job Taylor_20261031_025427): ảnh hưởng bật live QUA CALLER THẬT, sau khi caller khai price_date.
Universe_pit có giá tại phiên T (= asof). Bốn chân, mỗi chân là output _dcf_check_for_order (status/MoS/robust):
  FIN   knob fin (hiện hành)
  NOPD  live, caller KHÔNG khai price_date (send_plan_report/eod_trading_report: ref_price của plan)
  PD    live, price_date = phiên của giá (lag_dd_pack/due_diligence qua _ref_price_session; custom_basket.dcf_at
        price_date=d) — asof = T, giá Price phiên T
  PDM1  live, chạy SÁNG phiên T+1 trước sync BQ: asof = T+1, giá Price phiên T, price_date = T (khoá lịch H1
        bắt sự kiện ex đúng T+1)
Dùng: python measure_impact_r8.py <dir_code_outer> asof..."""
import os, sys, contextlib, io, json
code, dates = sys.argv[1], sys.argv[2:]
sys.path.insert(0, code)
import dcf_valuation as dv
sys.path.insert(0, code)                                   # H3: dcf_valuation chèn WORKDIR canonical
import duckdb, pandas as pd
import oshares_dcf as osd
import trading_bot.strategies as st
import trading_bot.due_diligence as dd
for m in (dv, osd, st, dd):
    assert os.path.abspath(m.__file__).startswith(code + "/"), m.__file__
dd.DATA_DIR = "/home/trido/thanhdt/WorkingClaude/data"
HERE = os.path.dirname(os.path.abspath(__file__))
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache"


def universe_prices(asof):
    c, y = duckdb.connect(), asof[:4]
    u = c.execute(f"""SELECT DISTINCT ticker FROM read_parquet('{C}/universe_pit/{y}.parquet')
                      WHERE in_universe AND time = (SELECT max(time) FROM read_parquet('{C}/universe_pit/{y}.parquet')
                                                    WHERE time <= DATE '{asof}')""").df().ticker
    p = c.execute(f"""SELECT ticker, Price, CAST(time AS VARCHAR) AS pdate FROM read_parquet('{C}/ticker/{y}.parquet')
                      WHERE time = (SELECT max(time) FROM read_parquet('{C}/ticker/{y}.parquet') WHERE time <= DATE '{asof}')""").df()
    nxt = c.execute(f"""SELECT CAST(min(time) AS VARCHAR) FROM read_parquet('{C}/ticker/{y}.parquet')
                        WHERE ticker='VNINDEX' AND time > DATE '{asof}'""").fetchone()[0]
    return p[p.ticker.isin(set(u))].dropna().set_index("ticker"), nxt[:10]


def leg(src, tk, asof, px, pd_):
    dv.OSHARES_SOURCE = src
    kw = {} if pd_ is None else {"price_date": pd_}
    chk = st._dcf_check_for_order(tk, px, asof, **kw)
    fv = dv.fair_value(tk, asof, price=px, **kw)
    return chk, fv


summary = {}
for asof in dates:
    px, nxt = universe_prices(asof)
    osd.prime(list(px.index), nxt)
    rows, err = [], io.StringIO()
    for tk, r0 in px.iterrows():
        p, pdate = float(r0.Price), r0.pdate[:10]
        with contextlib.redirect_stderr(err):
            legs = {"FIN": leg("fin", tk, asof, p, None), "NOPD": leg("live", tk, asof, p, None),
                    "PD": leg("live", tk, asof, p, pdate), "FINM1": leg("fin", tk, nxt, p, None),
                    "PDM1": leg("live", tk, nxt, p, pdate)}
        row = {"ticker": tk, "price": p, "price_date": pdate, "asof_m1": nxt}
        for k, (chk, fv) in legs.items():
            row.update({f"st_{k}": chk["status"], "rb_" + k: chk["robust"], "mos_" + k: chk["margin_of_safety"],
                        "fv_" + k: chk.get("fair_value_ps"), "osh_" + k: fv.get("oshares"),
                        "meth_" + k: fv.get("oshares_method"), "ferr_" + k: fv.get("oshares_frame_error")})
        rows.append(row)
    dv.OSHARES_SOURCE = "fin"
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(HERE, f"out_impact_r8_{asof}.csv"), index=False)
    s = {"universe": len(d), "asof_m1": nxt}
    for live, base in (("NOPD", "FIN"), ("PD", "FIN"), ("PDM1", "FINM1")):
        ok = d[d[f"st_{base}"] != "NOT_COMPUTED"]
        s[live] = {"dcf_ok": int(len(ok)),
                   "nc_changed": int((d[f"st_{base}"].eq("NOT_COMPUTED") != d[f"st_{live}"].eq("NOT_COMPUTED")).sum()),
                   "fv_changed": int((ok[f"fv_{live}"] != ok[f"fv_{base}"]).sum()),
                   "status_flip": sorted(f"{r.ticker}:{r[f'st_{base}']}->{r[f'st_{live}']}" for _, r in ok.iterrows()
                                         if r[f"st_{base}"] != r[f"st_{live}"]),
                   "robust_change": sorted(f"{r.ticker}:{r[f'rb_{base}']}->{r[f'rb_{live}']}" for _, r in ok.iterrows()
                                           if r[f"rb_{base}"] != r[f"rb_{live}"]),
                   "rich_robust_new": sorted(r.ticker for _, r in ok.iterrows()
                                             if r[f"st_{live}"] == "RICH" and r[f"rb_{live}"] and not
                                             (r[f"st_{base}"] == "RICH" and r[f"rb_{base}"])),
                   "methods": ok[f"meth_{live}"].value_counts().to_dict(),
                   "h1_calendar_fallback": sorted(r.ticker for _, r in ok.iterrows()
                                                  if "ISS doi khung gia" in str(r[f"ferr_{live}"]))}
    s["stderr_shouts"] = err.getvalue().count("!!!!! [dcf_valuation]")
    summary[asof] = s
    print(f"== asof {asof} (T+1 = {nxt}): {json.dumps(s, ensure_ascii=False)}", flush=True)
json.dump(summary, open(os.path.join(HERE, "impact_r8_summary.json"), "w"), ensure_ascii=False, indent=1)
