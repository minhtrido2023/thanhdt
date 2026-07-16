# -*- coding: utf-8 -*-
"""Probe read-only DNSE OpenAPI endpoints for asset-summary / 'Trứng vàng'.

Job Mafee_20260716_170856. GET only. Tries plausible REST paths on the SAME
base URL + HMAC auth already proven working for balances()/positions().
"""
import json
import sys

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dnse_api import DNSEClient, DNSEError

ACCOUNTS = {"ZaloPay": "0001743768", "SpaceX": "0002023347"}

PATHS = [
    "/accounts/{acc}/assets",
    "/accounts/{acc}/asset-summary",
    "/accounts/{acc}/assets-summary",
    "/accounts/{acc}/total-assets",
    "/accounts/{acc}/net-asset",
    "/accounts/{acc}/net-assets",
    "/accounts/{acc}/deposits",
    "/accounts/{acc}/deposit",
    "/accounts/{acc}/cash",
    "/accounts/{acc}/cash-statement",
    "/accounts/{acc}/money",
    "/accounts/{acc}/money-market",
    "/accounts/{acc}/summary",
    "/accounts/{acc}/portfolio",
    "/accounts/{acc}/investments",
    "/accounts/{acc}/golden-egg",
    "/accounts/{acc}/savings",
    "/assets/{acc}",
    "/asset-summary/{acc}",
]

QUERY_VARIANTS = [
    ("/accounts/{acc}/balances", {"assetType": "ALL"}),
    ("/accounts/{acc}/balances", {"accountType": "ALL"}),
    ("/accounts/{acc}/balances", {"includeDeposit": "true"}),
]


def main():
    c = DNSEClient.from_credentials_file()
    results = {}
    for label, acc in ACCOUNTS.items():
        print(f"===== {label} ({acc}) =====")
        for tpl in PATHS:
            path = tpl.format(acc=acc)
            try:
                r = c._request("GET", path)
                print(f"  HIT  {path}\n       {json.dumps(r, ensure_ascii=False)[:800]}")
                results.setdefault(label, []).append((path, r))
            except DNSEError as e:
                print(f"  {e.status}  {path}  {str(e)[:120]}")
        for tpl, q in QUERY_VARIANTS:
            path = tpl.format(acc=acc)
            try:
                r = c._request("GET", path, query=q)
                keys = sorted(r.keys()) if isinstance(r, dict) else type(r).__name__
                print(f"  OK   {path}?{q} -> keys={keys}")
            except DNSEError as e:
                print(f"  {e.status}  {path}?{q}  {str(e)[:120]}")
    if results:
        with open("/home/trido/thanhdt/WorkingClaude/mike/agents/Mafee/probe_trung_vang_hits.json",
                  "w", encoding="utf-8") as f:
            json.dump({k: [{"path": p, "resp": r} for p, r in v]
                       for k, v in results.items()}, f, ensure_ascii=False, indent=2)
        print("hits saved -> probe_trung_vang_hits.json")
    else:
        print("NO HITS")


if __name__ == "__main__":
    main()
