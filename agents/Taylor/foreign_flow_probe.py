#!/usr/bin/env python3
"""
foreign_flow_probe.py  (Taylor, job Taylor_20260723_074919)

Probe: does vnstock (installed 2.4.9, sources VCI/KBS) expose foreign-investor
(khoi ngoai) and proprietary-desk (tu doanh) trading flow — on the CASH market
(VNINDEX / stocks) and/or the DERIVATIVES market (VN30F) — with enough historical
depth to research a leading signal?

VERDICT (see foreign_flow_data_probe.md): NO usable HISTORICAL series.
  - Trading(source=...).foreign_trade(...) and .prop_trade(...) => NotImplementedError
    (stub methods; NO provider — neither VCI nor KBS — implements them).
  - The ONLY foreign data path is Trading.price_board([...]) => a REAL-TIME SNAPSHOT
    of the CURRENT session's accumulated foreign_buy/sell_volume + _value per stock.
    No date-range arg, no history, resets each session. tu doanh: not available at all.
  - Derivatives (VN30F): no separate foreign/prop endpoint at all.

Because there is no historical depth, an IC / walk-forward test (the discipline used
for VN30F basis) is impossible from vnstock. This script documents the exact API
behaviour so the probe is reproducible.
"""
import sys

def probe():
    from vnstock import Trading

    print("=== 1. foreign_trade / prop_trade across allowed sources ===")
    for src in ("VCI", "KBS"):
        try:
            t = Trading(source=src)
        except Exception as e:
            print(f"  init {src}: ERR {e!r}")
            continue
        prov_methods = [m for m in dir(t._provider)
                        if not m.startswith("_") and callable(getattr(t._provider, m))]
        print(f"  {src} provider implements: {prov_methods}")
        for m in ("foreign_trade", "prop_trade"):
            try:
                getattr(t, m)("VCB")
                print(f"    {src}.{m}('VCB'): OK (unexpected)")
            except Exception as e:
                # unwrap tenacity RetryError -> NotImplementedError
                print(f"    {src}.{m}('VCB'): {type(e).__name__} -> stub, not supported")

    print("\n=== 2. price_board snapshot (the only foreign path) ===")
    t = Trading(source="VCI")
    pb = t.price_board(["VCB", "FPT", "HPG"])
    cols = [("listing", "symbol"),
            ("match", "foreign_buy_volume"), ("match", "foreign_sell_volume"),
            ("match", "foreign_buy_value"), ("match", "foreign_sell_value")]
    print("  columns present:", all(c in pb.columns for c in cols))
    print(pb[cols].to_string())
    print("\n  NOTE: snapshot = current session accumulated only. No history, no date arg.")

if __name__ == "__main__":
    try:
        probe()
    except Exception as e:
        print("PROBE FAILED:", repr(e))
        sys.exit(1)
