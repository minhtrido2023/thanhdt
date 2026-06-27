#!/usr/bin/env python3
"""Probe DNSE margin/loan_packages cho tất cả tiểu khoản.
Kết quả: loan_package_id, initial/maintenance margin, collateral eligibility custom30V.
"""
import json, sys, os

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dnse_api import DNSEClient, DNSEError

# custom30V basket (latest rebal 2026-05-05, excludes PC1 per hard_ban + DGC per legal_review)
CUSTOM30V = [
    "ACB","BID","CTG","DBC","DCM","EVF","HAH","HDB","HHV","HPG",
    "IDC","LPB","MBB","MBS","MSB","PVT","SHB","SHS","TCB","TPB",
    "VCB","VGC","VHC","VHM","VIB","VIX","VND","VPB"
]
# Note: DGC + PC1 removed (legal_review / hard_ban from trading_rules.json)

def run():
    c = DNSEClient.from_credentials_file()

    # 1. Danh sách tiểu khoản
    accs_resp = c.accounts()
    accounts = accs_resp.get("accounts", []) if isinstance(accs_resp, dict) else []
    if not accounts:
        # fallback: response IS the list
        accounts = accs_resp if isinstance(accs_resp, list) else []

    print(f"[accounts raw keys]: {list(accs_resp.keys()) if isinstance(accs_resp, dict) else type(accs_resp)}")
    print(json.dumps(accs_resp, ensure_ascii=False, indent=2)[:800])

    result = {"accounts": []}

    for acc in accounts:
        acc_id = acc.get("id") or acc.get("accountNo") or acc.get("sub_account_no")
        if not acc_id:
            continue
        acc_info = {"id": acc_id, "type": acc.get("type","?"), "margin_enabled": False,
                    "loan_packages": [], "collateral_check": {}}

        # 2. loan_packages
        try:
            lp_resp = c.loan_packages(acc_id)
            pkgs = lp_resp if isinstance(lp_resp, list) else lp_resp.get("loanPackages", lp_resp.get("data",[]))
            acc_info["loan_packages"] = pkgs
            acc_info["margin_enabled"] = len(pkgs) > 0
            print(f"\n[{acc_id}] loan_packages ({len(pkgs)} gói):")
            print(json.dumps(pkgs, ensure_ascii=False, indent=2)[:1200])
        except DNSEError as e:
            acc_info["loan_packages_error"] = str(e)
            print(f"[{acc_id}] loan_packages ERROR: {e}")

        # 3. Collateral check — thử 5 mã đại diện custom30V
        sample = ["VCB","HPG","ACB","MBB","CTG"]
        for sym in sample:
            try:
                lp_sym = c.loan_packages(acc_id, symbol=sym)
                pkgs_sym = lp_sym if isinstance(lp_sym, list) else lp_sym.get("loanPackages", lp_sym.get("data",[]))
                acc_info["collateral_check"][sym] = {
                    "eligible": len(pkgs_sym) > 0,
                    "packages": pkgs_sym
                }
            except DNSEError as e:
                acc_info["collateral_check"][sym] = {"eligible": False, "error": str(e)}

        result["accounts"].append(acc_info)

    # Save
    out = "/home/trido/thanhdt/WorkingClaude/mike/agents/Mafee/probe_margin_result.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n[saved] {out}")
    print("\n=== SUMMARY ===")
    for a in result["accounts"]:
        n_pkg = len(a.get("loan_packages",[]))
        print(f"  {a['id']} (type={a['type']}): margin_enabled={a['margin_enabled']}, {n_pkg} loan_packages")
        for sym, cv in a.get("collateral_check",{}).items():
            print(f"    collateral {sym}: eligible={cv.get('eligible')}")
    return result

if __name__ == "__main__":
    run()
