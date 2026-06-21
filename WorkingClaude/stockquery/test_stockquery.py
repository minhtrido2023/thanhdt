"""Smoke test for stockquery_agent.StockQuery — verifies vnstock + cafef APIs."""
import sys
import time
import traceback

from stockquery_agent import StockQuery


def section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def safe_run(label, fn, *args, **kwargs):
    print(f"\n>> {label}")
    t0 = time.time()
    try:
        out = fn(*args, **kwargs)
        elapsed = time.time() - t0
        if hasattr(out, "shape"):
            print(f"   OK [{elapsed:.2f}s] shape={out.shape}, columns={list(out.columns)[:12]}")
            print(out.head(3).to_string())
        else:
            print(f"   OK [{elapsed:.2f}s] type={type(out).__name__}")
        return out
    except Exception as e:
        elapsed = time.time() - t0
        print(f"   FAIL [{elapsed:.2f}s] {type(e).__name__}: {e}")
        traceback.print_exc(limit=3)
        return None


def main():
    section("Init StockQuery")
    sq = StockQuery(start_date="2025-01-01")
    print(f"start_date={sq.start_date}, end_date={sq.end_date}")

    section("1. Intraday history (15m) for VNINDEX — primary use case")
    df_15m = safe_run("VNINDEX 15m", sq.get_historical_symbol, "VNINDEX", interval="15m")

    section("2. Intraday history (5m) for HPG ticker")
    df_5m = safe_run("HPG 5m", sq.get_historical_symbol, "HPG", interval="5m")

    section("3. Daily history (1D) for HPG — sanity check")
    df_1d = safe_run("HPG 1D", sq.get_historical_symbol, "HPG", interval="1D")

    section("4. Symbols by exchange")
    df_ex = safe_run("symbols_by_exchange", sq.symbols_by_exchange)

    section("5. Symbols by group (VN30)")
    df_vn30 = safe_run("symbols_by_group VN30", sq.symbols_by_group, "VN30")

    section("6. Unadjusted price (cafef) for VNM")
    df_un = safe_run("get_unadjust_price VNM", sq.get_unadjust_price, "VNM")

    section("7. Enrich VNINDEX (cafef PE + trading session)")
    df_idx = safe_run("get_enrich_vnindex", sq.get_enrich_vnindex)

    section("Summary")
    results = {
        "VNINDEX 15m": df_15m,
        "HPG 5m": df_5m,
        "HPG 1D": df_1d,
        "exchange list": df_ex,
        "VN30 group": df_vn30,
        "unadjust VNM": df_un,
        "enrich VNINDEX": df_idx,
    }
    passed = sum(1 for v in results.values() if v is not None)
    print(f"\n   {passed}/{len(results)} API calls passed.")
    for k, v in results.items():
        flag = "OK" if v is not None else "FAIL"
        rows = v.shape[0] if v is not None and hasattr(v, "shape") else "-"
        print(f"   [{flag:4}] {k:20} rows={rows}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
