#!/usr/bin/env python3
"""Probe chi tiết: lấy loan_package_id + margin rates từ DNSE."""
import json, sys

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dnse_api import DNSEClient, DNSEError

# Tiểu khoản live từ CLAUDE.md
TARGET_ACC = "0001743768"

# custom30V basket (PC1/DGC loại trừ per rules)
CUSTOM30V = [
    "ACB","BID","CTG","DBC","DCM","EVF","HAH","HDB","HHV","HPG",
    "IDC","LPB","MBB","MBS","MSB","PVT","SHB","SHS","TCB","TPB",
    "VCB","VGC","VHC","VHM","VIB","VIX","VND","VPB"
]

def run():
    c = DNSEClient.from_credentials_file()
    result = {"account": TARGET_ACC, "loan_packages_by_symbol": {}, "collateral_summary": {}}

    # Probe all custom30V symbols
    print(f"=== Probing loan_packages per symbol for account {TARGET_ACC} ===")
    all_pkg_ids = set()
    eligible_tickers = []
    ineligible_tickers = []

    for sym in CUSTOM30V:
        try:
            raw = c.loan_packages(TARGET_ACC, symbol=sym)
            pkgs = raw if isinstance(raw, list) else \
                   raw.get("loanPackages", raw.get("data", raw.get("packages", [])))
            if not isinstance(pkgs, list):
                pkgs = [pkgs] if pkgs else []
            result["loan_packages_by_symbol"][sym] = pkgs
            if pkgs:
                eligible_tickers.append(sym)
                for p in pkgs:
                    if isinstance(p, dict):
                        pid = p.get("id") or p.get("loanPackageId") or p.get("packageId")
                        if pid:
                            all_pkg_ids.add(str(pid))
            else:
                ineligible_tickers.append(sym)
                # Print first empty case to see raw
                print(f"  {sym}: EMPTY packages. raw={json.dumps(raw)[:200]}")
        except DNSEError as e:
            ineligible_tickers.append(sym)
            result["loan_packages_by_symbol"][sym] = {"error": str(e)}
            print(f"  {sym}: ERROR {e}")

    # Print detail for first eligible symbol
    for sym in eligible_tickers[:3]:
        pkgs = result["loan_packages_by_symbol"][sym]
        print(f"\n  {sym}: {len(pkgs)} packages")
        print(f"  {json.dumps(pkgs, ensure_ascii=False, indent=2)[:600]}")

    # Summary
    result["collateral_summary"] = {
        "eligible_count": len(eligible_tickers),
        "ineligible_count": len(ineligible_tickers),
        "eligible_tickers": eligible_tickers,
        "ineligible_tickers": ineligible_tickers,
        "all_loan_package_ids": list(all_pkg_ids)
    }

    print(f"\n=== COLLATERAL SUMMARY ===")
    print(f"  Eligible: {len(eligible_tickers)}/{len(CUSTOM30V)}: {eligible_tickers}")
    print(f"  Ineligible: {ineligible_tickers}")
    print(f"  Loan package IDs found: {list(all_pkg_ids)}")

    # Also try accounts() for type/margin field
    try:
        accs = c.accounts()
        for a in accs.get("accounts",[]):
            if a.get("id") == TARGET_ACC:
                print(f"\n  Account {TARGET_ACC} fields: {json.dumps(a, ensure_ascii=False)[:400]}")
    except Exception as e:
        print(f"  accounts() err: {e}")

    # Also try balances to see if margin data included
    try:
        bal = c.balances(TARGET_ACC)
        print(f"\n  balances fields: {list(bal.keys()) if isinstance(bal, dict) else type(bal)}")
        print(f"  {json.dumps(bal, ensure_ascii=False, indent=2)[:600]}")
    except Exception as e:
        print(f"  balances() err: {e}")

    out = "/home/trido/thanhdt/WorkingClaude/mike/agents/Mafee/probe_margin2_result.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n[saved] {out}")
    return result

if __name__ == "__main__":
    run()
