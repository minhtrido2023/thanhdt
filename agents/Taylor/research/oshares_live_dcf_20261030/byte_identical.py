#!/usr/bin/env python3
"""fair_value mặc định (env DCF_OSHARES_SOURCE trống) của nhánh == bản canonical, từng byte (repr dict),
trên universe_pit có giá tại các asof. Dùng: python3 byte_identical.py <dir_code> <out.pkl> asof..."""
import os, pickle, sys
code, outp, dates = sys.argv[1], sys.argv[2], sys.argv[3:]
sys.path.insert(0, code)
import dcf_valuation as dv
assert os.path.dirname(dv.__file__) == code, dv.__file__
import duckdb
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache"


def universe_prices(asof):          # bản sao measure_impact.universe_prices (tránh import oshares_dcf)
    c, y = duckdb.connect(), asof[:4]
    u = c.execute(f"""SELECT DISTINCT ticker FROM read_parquet('{C}/universe_pit/{y}.parquet')
                      WHERE in_universe AND time = (SELECT max(time) FROM read_parquet('{C}/universe_pit/{y}.parquet')
                                                    WHERE time <= DATE '{asof}')""").df().ticker
    p = c.execute(f"""SELECT ticker, Price FROM read_parquet('{C}/ticker/{y}.parquet')
                      WHERE time = (SELECT max(time) FROM read_parquet('{C}/ticker/{y}.parquet') WHERE time <= DATE '{asof}')""").df()
    return p[p.ticker.isin(set(u))].dropna().set_index("ticker").Price


fin = dv._load_financials()
out = {}
for a in dates:
    for tk, p in universe_prices(a).items():
        out[(a, tk)] = repr(dv.fair_value(tk, a, price=float(p), fin=fin))
pickle.dump(out, open(outp, "wb"))
print(dv.__file__, getattr(dv, "OSHARES_SOURCE", "<chua co knob>"), len(out))
