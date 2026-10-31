#!/usr/bin/env python3
"""R12: ở knob fin (env DCF_OSHARES_SOURCE=fin — mặc định PROD nay là live), output các đường R11 đổi của
nhánh == main, từng byte (repr), toàn universe_pit ở các asof:
  dcf_check(t, a, price=Close)      (converge/alphalens; nhánh: khớp phiên chỉ khi live)
  _dcf_check_for_order(t, p, a)     main  vs  nhánh _dcf_check_for_order(t, p, a, price_date=price_session_for(...))
                                    (plan echo / EOD / paper; fin bỏ qua price_date)
  dcf_check(t, a) (tự đọc giá)
Dùng: python3 byte_identical_r11.py <dir_code> <main|branch> <out.pkl> asof..."""
import os, pickle, sys
code, mode, outp, dates = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3]), sys.argv[4:]
assert os.environ.get("DCF_OSHARES_SOURCE") == "fin", "env phải = fin"
sys.path.insert(0, code)
import dcf_valuation as dv
sys.path.insert(0, code)
import trading_bot.strategies as st
for m in (dv, st):
    assert os.path.abspath(m.__file__).startswith(code + "/"), m.__file__
assert dv.OSHARES_SOURCE == "fin"
import duckdb
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache"
out = {}
for asof in dates:
    c, y = duckdb.connect(), asof[:4]
    p = c.execute(f"""SELECT t.ticker, t.Price, t.Close FROM read_parquet('{C}/ticker/{y}.parquet') t
                      JOIN (SELECT DISTINCT ticker FROM read_parquet('{C}/universe_pit/{y}.parquet')
                            WHERE in_universe AND time = (SELECT max(time) FROM read_parquet('{C}/universe_pit/{y}.parquet') WHERE time <= DATE '{asof}')) u
                      USING (ticker)
                      WHERE t.time = (SELECT max(time) FROM read_parquet('{C}/ticker/{y}.parquet') WHERE time <= DATE '{asof}')
                      AND t.Price IS NOT NULL""").df()
    for tk, px, cl in zip(p.ticker, p.Price, p.Close):
        out[("dcfc_px", asof, tk)] = repr(dv.dcf_check(tk, asof, price=float(cl)))
        kw = {"price_date": dv.price_session_for(tk, asof, float(px))} if mode == "branch" else {}
        out[("chk", asof, tk)] = repr(st._dcf_check_for_order(tk, float(px), asof, **kw))
        out[("dcfc", asof, tk)] = repr(dv.dcf_check(tk, asof))
        kw2 = {"price_date": dv.PRICE_SESSION_UNKNOWN} if mode == "branch" else {}   # R12 plan echo
        d2 = st._dcf_check_for_order(tk, float(px), asof, **kw2)
        out[("plan", asof, tk)] = repr(d2)
        out[("fmt", asof, tk)] = repr(st.format_dcf_check(d2, "buy"))
pickle.dump(out, open(outp, "wb"))
print(mode, len(out))
