import dcf_valuation as dv
for a, pdt in (("2026-10-20", "2026-10-17"), ("2026-09-23", "2026-09-22")):
    px = dv.latest_price_session("FPT", pdt)
    r = dv.fair_value("FPT", a, price=px[0], price_date=px[1])
    print(a, px, {k: r.get(k) for k in ("oshares", "oshares_fin", "oshares_method", "oshares_source", "quarter", "oshares_divergence")})
