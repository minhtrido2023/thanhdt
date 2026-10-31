"""R12/việc 1: nhãn 'số CP quý' trên FPT 2026-09-23 + PHR/AIG lật CHEAP->RICH (live)."""
import dcf_valuation as dv
from trading_bot.strategies import _dcf_check_for_order, format_dcf_check
for tk, asof, px in [("FPT", "2026-09-23", 66600), ("PHR", "2026-09-15", 31100), ("AIG", "2026-08-06", 47000),
                     ("HT1", "2026-10-29", None), ("VNM", "2026-10-29", None)]:
    if px is None:
        px, _ = dv.latest_price_session(tk, asof)
    pd_ = dv.price_session_for(tk, asof, px)
    d = _dcf_check_for_order(tk, px, asof, price_date=pd_)
    print(tk, asof, px, pd_, {k: d.get(k) for k in ("status", "status_fin", "margin_of_safety", "margin_of_safety_fin",
                                                    "robust", "robust_fin", "oshares_divergence")})
    print("   LINE:", format_dcf_check(d, "buy", ticker=tk))
