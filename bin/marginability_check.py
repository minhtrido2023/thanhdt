#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Marginability annotate — VIỆC 1 của discretionary-sleeve-candidate-funnel-20260830.

Trước script này, không có cách hệ thống nào biết trước 1 mã có được DNSE cho vay margin hay
không — `discretionary_margin_gate.py` yêu cầu `--marginability-confirmed-by` là chuỗi TAY
(Mafee tự probe từng case). Script này tự động hoá đúng phép probe đó qua
`DNSEClient.loan_packages(account, symbol=X)` (GET /accounts/{acc}/loan-packages — đọc thuần,
KHÔNG cần trading-token/OTP, xem kb/data_registry/trading-bot/dnse_openapi_v2_calling_guideline.md).

TIÊU CHÍ marginable (xác nhận bằng probe LIVE 2026-08-30 trên account SpaceX 0002023347):
  - field `type` ("N"/"M") KHÔNG đáng tin — trên SpaceX (account margin), CẢ gói tiền mặt 1841
    LẪN gói margin 1840 "RocketX" đều trả `type="M"`; trên ZaloPay (cash-only) mọi gói trả
    `type="N"`. `type` là thuộc tính ACCOUNT, không phải per-symbol.
  - Field đáng tin = `initialRate` (tỷ lệ ký quỹ ban đầu): 1.0 = không có đòn bẩy (dù tên gói là
    gì), <1.0 = margin thật. Probe thật:
      TV1 (UPCOM)            -> chỉ 1 gói id=1122, KHÔNG có field initialRate      -> NOT marginable
      DGC (HOSE, hạn chế)    -> 1 gói "RocketX" id=1840 nhưng initialRate=1.0     -> NOT marginable
      MBB (mainboard bình thường) -> 2 gói, 1840 initialRate=0.5                  -> marginable
    Khớp đúng 2 case NON-marginable đã biết (TV1 UPCOM, DGC HOSE-hạn chế) — xem
    kb/projects/discretionary-margin-policy-20260823.md.
  marginable(ticker) := any(pkg.initialRate is not None and pkg.initialRate < 1.0 for pkg in packages)

CACHE: danh sách marginable đổi CHẬM (chính sách vay/hạn chế sàn, không phải giá) — cache
`data/marginability_cache.json`, mặc định làm mới sau 7 ngày lịch (CACHE_MAX_AGE_DAYS), atomic
write (§5 coding_guidelines). Lỗi/timeout DNSE cho 1 mã → ghi `error`, `marginable=None`
(fail-safe: KHÔNG đoán khi không có bằng chứng, §29) — KHÔNG cache kết quả lỗi.

DÙNG:
    python3 mike/bin/marginability_check.py --tickers TV1,DGC,MBB
    python3 mike/bin/marginability_check.py --tickers TV1,DGC,MBB --refresh   # bỏ qua cache
    python3 mike/bin/marginability_check.py --tickers TV1 --json              # in JSON thô

    from marginability_check import check_marginability
    result = check_marginability(["TV1", "DGC", "MBB"])
"""

import argparse
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, WC_ROOT)

ICT = ZoneInfo("Asia/Ho_Chi_Minh")                        # §16: neo múi giờ tường minh

CACHE_PATH = os.path.join(WC_ROOT, "data", "marginability_cache.json")
DEFAULT_ACCOUNT = "0002023347"       # SpaceX — account margin DUY NHẤT, đồng bộ ONLY_ACCOUNT
                                       # trong discretionary_margin_gate.py (ZaloPay cash-only,
                                       # loan_packages() ở đó luôn trả toàn gói type="N" vô nghĩa)
CACHE_MAX_AGE_DAYS = 7


def _now_ict_iso():
    return dt.datetime.now(ICT).isoformat()


def _load_cache():
    if not os.path.exists(CACHE_PATH):
        return {}
    try:
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:            # §5: ghi nguyên tử
        json.dump(cache, f, ensure_ascii=False, indent=2)
    os.replace(tmp, CACHE_PATH)


def _entry_stale(entry, max_age_days):
    checked_at = entry.get("checked_at")
    if not checked_at:
        return True
    try:
        checked = dt.datetime.fromisoformat(checked_at)
    except ValueError:
        return True
    if checked.tzinfo is None:
        checked = checked.replace(tzinfo=ICT)
    age_days = (dt.datetime.now(ICT) - checked).total_seconds() / 86400.0
    return age_days > max_age_days


def _probe_symbol(client, account, symbol):
    """1 probe thật qua DNSE — trả entry dict, KHÔNG bao giờ raise (lỗi -> entry có 'error')."""
    from dnse_api import DNSEError
    try:
        raw = client.loan_packages(account, symbol=symbol)
    except DNSEError as e:
        return {"marginable": None, "error": f"DNSEError: {e}", "checked_at": _now_ict_iso()}
    except Exception as e:                                  # network/timeout/khác — fail-safe
        return {"marginable": None, "error": f"{type(e).__name__}: {e}",
                "checked_at": _now_ict_iso()}

    pkgs = raw if isinstance(raw, list) else \
        raw.get("loanPackages", raw.get("data", raw.get("packages", [])))
    if not isinstance(pkgs, list):
        pkgs = [pkgs] if pkgs else []
    pkgs = [p for p in pkgs if isinstance(p, dict)]

    margin_pkgs = [p for p in pkgs
                   if isinstance(p.get("initialRate"), (int, float)) and p["initialRate"] < 1.0]
    marginable = bool(margin_pkgs)
    best = min(margin_pkgs, key=lambda p: p["initialRate"]) if margin_pkgs else None

    return {
        "marginable": marginable,
        "package_id": best.get("id") if best else None,
        "initial_rate": best.get("initialRate") if best else None,
        "interest_rate": best.get("interestRate") if best else None,
        "maintenance_rate": best.get("maintenanceRate") if best else None,
        "liquid_rate": best.get("liquidRate") if best else None,
        "n_packages_total": len(pkgs),
        "error": None,
        "checked_at": _now_ict_iso(),
    }


def check_marginability(tickers, account=DEFAULT_ACCOUNT, cache_path=CACHE_PATH,
                         max_age_days=CACHE_MAX_AGE_DAYS, force_refresh=False):
    """Trả {ticker: entry} — entry từ cache (nếu còn tươi) hoặc probe DNSE mới.

    entry = {"marginable": bool|None, "package_id", "initial_rate", "interest_rate",
             "maintenance_rate", "liquid_rate", "n_packages_total", "error", "checked_at"}
    marginable=None nghĩa là KHÔNG XÁC ĐỊNH ĐƯỢC (lỗi API) — khác False (đã probe, không có
    gói margin). Caller (funnel) PHẢI coi None như "chưa biết", không phải "không marginable".
    """
    tickers = list(dict.fromkeys(tickers))          # unique, giữ thứ tự
    cache = {} if force_refresh else _load_cache()
    cache_key = f"{account}"
    acct_cache = cache.setdefault(cache_key, {})

    to_probe = [t for t in tickers
                if force_refresh or t not in acct_cache or _entry_stale(acct_cache[t], max_age_days)]

    if to_probe:
        from dnse_api import DNSEClient
        client = DNSEClient.from_credentials_file()
        for sym in to_probe:
            acct_cache[sym] = _probe_symbol(client, account, sym)
        _save_cache(cache)

    return {t: acct_cache[t] for t in tickers if t in acct_cache}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tickers", required=True, help="Danh sách mã, phân cách dấu phẩy")
    ap.add_argument("--account", default=DEFAULT_ACCOUNT)
    ap.add_argument("--refresh", action="store_true", help="Bỏ qua cache, probe lại toàn bộ")
    ap.add_argument("--max-age-days", type=int, default=CACHE_MAX_AGE_DAYS)
    ap.add_argument("--json", action="store_true", help="In JSON thô thay vì bảng")
    args = ap.parse_args()

    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    result = check_marginability(tickers, account=args.account,
                                  max_age_days=args.max_age_days, force_refresh=args.refresh)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"{'ticker':8} {'marginable':10} {'pkg_id':7} {'init_rate':9} {'maint_rate':10} error")
    for t in tickers:
        e = result.get(t, {})
        marg = e.get("marginable")
        marg_s = "YES" if marg is True else ("NO" if marg is False else "UNKNOWN")
        print(f"{t:8} {marg_s:10} {str(e.get('package_id') or ''):7} "
              f"{str(e.get('initial_rate') or ''):9} {str(e.get('maintenance_rate') or ''):10} "
              f"{e.get('error') or ''}")


if __name__ == "__main__":
    main()
