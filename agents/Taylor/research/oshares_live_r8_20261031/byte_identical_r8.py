#!/usr/bin/env python3
"""R8: ở knob fin (env DCF_OSHARES_SOURCE trống), output đường tiền của nhánh == canonical, từng byte (repr):
  fair_value(price=p)              main  vs  nhánh fair_value(price=p, price_date=phiên giá)
  _dcf_check_for_order(t, p, a)    main  vs  nhánh _dcf_check_for_order(t, p, a, price_date=phiên giá)
  dcf_check(t, a) (tự đọc giá)     main  vs  nhánh (latest_price_session mới)
  due_diligence._ref_price_for     main  vs  nhánh _ref_price_session()[0]
Dùng: python3 byte_identical_r8.py <dir_code> <main|branch> <out.pkl> asof..."""
import os, pickle, sys
code, mode, outp, dates = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3]), sys.argv[4:]
assert not os.environ.get("DCF_OSHARES_SOURCE"), "env phải trống"
sys.path.insert(0, code)
import dcf_valuation as dv
sys.path.insert(0, code)                       # dcf_valuation chèn WORKDIR canonical lên đầu (H3)
import trading_bot.strategies as st
import trading_bot.due_diligence as dd
for m in (dv, st, dd):
    assert os.path.abspath(m.__file__).startswith(code + "/"), m.__file__
assert dv.OSHARES_SOURCE == "fin"
dd.DATA_DIR = "/home/trido/thanhdt/WorkingClaude/data"   # worktree không có data/bq_cache: cả hai bản đọc CÙNG dữ liệu PROD
import duckdb
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache"


def universe_prices(asof):
    c, y = duckdb.connect(), asof[:4]
    u = c.execute(f"""SELECT DISTINCT ticker FROM read_parquet('{C}/universe_pit/{y}.parquet')
                      WHERE in_universe AND time = (SELECT max(time) FROM read_parquet('{C}/universe_pit/{y}.parquet')
                                                    WHERE time <= DATE '{asof}')""").df().ticker
    p = c.execute(f"""SELECT ticker, Price, CAST(time AS VARCHAR) d FROM read_parquet('{C}/ticker/{y}.parquet')
                      WHERE time = (SELECT max(time) FROM read_parquet('{C}/ticker/{y}.parquet') WHERE time <= DATE '{asof}')""").df()
    p = p[p.ticker.isin(set(u))].dropna()
    return [(r.ticker, float(r.Price), r.d[:10]) for r in p.itertuples()]


fin = dv._load_financials()
out = {}
for a in dates:
    for tk, p, d in universe_prices(a):
        br = mode == "branch"
        out[("fv", a, tk)] = repr(dv.fair_value(tk, a, price=p, fin=fin, **({"price_date": d} if br else {})))
        out[("chk", a, tk)] = repr(st._dcf_check_for_order(tk, p, a, **({"price_date": d} if br else {})))
        out[("dcfc", a, tk)] = repr(dv.dcf_check(tk, a))
        out[("ref", a, tk)] = repr(dd._ref_price_session(tk, a)[0] if br else dd._ref_price_for(tk, a))
pickle.dump(out, open(outp, "wb"))
print(dv.__file__, st.__file__, dv.OSHARES_SOURCE, len(out), {k: sum(1 for x in out if x[0] == k) for k in ("fv", "chk", "dcfc", "ref")})
