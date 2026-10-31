#!/usr/bin/env python3
"""Đo lại ảnh hưởng fin→live SAU R4 (bỏ nhánh announced) + R5 (khoá khung ex-date), job Taylor_20261030_155013.
Ba chân trên universe_pit có giá tại asof: fin | live không khai price_date | live price_date = phiên thật của giá.
Dùng: python measure_impact_r5.py <dir_code_outer> asof..."""
import os, sys, contextlib, io
code, dates = sys.argv[1], sys.argv[2:]
sys.path.insert(0, code)
import duckdb, pandas as pd
import oshares_dcf as osd
import dcf_valuation as dv
assert os.path.dirname(dv.__file__) == code and os.path.dirname(osd.__file__) == code, (dv.__file__, osd.__file__)
HERE = os.path.dirname(os.path.abspath(__file__))
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache"


def universe_prices(asof):
    c, y = duckdb.connect(), asof[:4]
    u = c.execute(f"""SELECT DISTINCT ticker FROM read_parquet('{C}/universe_pit/{y}.parquet')
                      WHERE in_universe AND time = (SELECT max(time) FROM read_parquet('{C}/universe_pit/{y}.parquet')
                                                    WHERE time <= DATE '{asof}')""").df().ticker
    p = c.execute(f"""SELECT ticker, Price, CAST(time AS VARCHAR) AS pdate FROM read_parquet('{C}/ticker/{y}.parquet')
                      WHERE time = (SELECT max(time) FROM read_parquet('{C}/ticker/{y}.parquet') WHERE time <= DATE '{asof}')""").df()
    return p[p.ticker.isin(set(u))].dropna().set_index("ticker")


for asof in dates:
    px = universe_prices(asof)
    fin = dv._load_financials()
    osd.prime(list(px.index), asof)
    rows = []
    err = io.StringIO()
    for tk, r0 in px.iterrows():
        price = float(r0.Price)
        dv.OSHARES_SOURCE = "fin"
        a = dv.fair_value(tk, asof, price=price, fin=fin)
        dv.OSHARES_SOURCE = "live"
        with contextlib.redirect_stderr(err):
            n = dv.fair_value(tk, asof, price=price, fin=fin)
            b = dv.fair_value(tk, asof, price=price, fin=fin, price_date=r0.pdate)
        row = {"ticker": tk, "price": price, "price_date": r0.pdate, "ok_fin": a["ok"], "ok_live": b["ok"]}
        if a["ok"] and b["ok"]:
            sa, ra = dv.classify_dcf(a["margin_of_safety"], a["sensitivity"], price)
            sb, rb = dv.classify_dcf(b["margin_of_safety"], b["sensitivity"], price)
            row.update(osh_fin=a["oshares"], osh_nodate=n["oshares"], osh_live=b["oshares"],
                       fv_ratio=b["fair_value_ps"] / a["fair_value_ps"], st_fin=sa, st_live=sb, rb_fin=ra, rb_live=rb,
                       method=b.get("oshares_method"), frame_error=b.get("oshares_frame_error"),
                       nodate_method=n.get("oshares_method"))
        rows.append(row)
    dv.OSHARES_SOURCE = "fin"
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(HERE, f"out_impact_r5_{asof}.csv"), index=False)
    ok = d[d.ok_fin & d.ok_live]
    ch = ok[(ok.fv_ratio - 1).abs() > 1e-9]
    print(f"== asof {asof}: phiên giá {sorted(d.price_date.unique())} | universe có giá {len(d)} | DCF ok {len(ok)} "
          f"| ok_fin!=ok_live {int((d.ok_fin != d.ok_live).sum())}")
    print(f"   chân KHÔNG price_date: osh != fin ở {int((ok.osh_nodate != ok.osh_fin).sum())} mã; "
          f"method {ok.nodate_method.value_counts().to_dict()}; số dòng kêu stderr {err.getvalue().count('!!!!! [dcf_valuation]')}")
    print(f"   chân price_date: FV đổi {len(ch)}; >1% {int(((ch.fv_ratio - 1).abs() > 0.01).sum())}; "
          f">5% {int(((ch.fv_ratio - 1).abs() > 0.05).sum())}; lật status {int((ok.st_fin != ok.st_live).sum())}; "
          f"đổi robust {int((ok.rb_fin != ok.rb_live).sum())}; frame_error {int(ok.frame_error.notna().sum())}")
    show = ch.reindex(ch.fv_ratio.sub(1).abs().sort_values(ascending=False).index)
    print(show[["ticker", "osh_fin", "osh_live", "fv_ratio", "st_fin", "st_live", "rb_fin", "rb_live", "method"]]
          .round(4).to_string(index=False))
