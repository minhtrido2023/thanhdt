# -*- coding: utf-8 -*-
"""READ-ONLY probe: balances for RocketX Deal subaccount 0002023348 vs SpaceX 0002023347.
Job Mafee_20261001_050400. GET only — no orders, no transfers, no enabled flip.
"""
import json
import sys

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dnse_api import DNSEClient, DNSEError

ACCOUNTS = {"SpaceX": "0002023347", "RocketX Deal": "0002023348"}


def main():
    c = DNSEClient.from_credentials_file()

    print("===== accounts() =====")
    try:
        accs = c.accounts()
        print(json.dumps(accs, ensure_ascii=False, indent=2))
    except DNSEError as e:
        print(f"accounts() FAILED: {e}")

    for label, acc in ACCOUNTS.items():
        print(f"\n===== balances({label} / {acc}) =====")
        try:
            bal = c.balances(acc)
            print(json.dumps(bal, ensure_ascii=False, indent=2))
        except DNSEError as e:
            print(f"balances({acc}) FAILED: status={e.status} {e}")

        print(f"----- ppse({label}) skipped (needs symbol/price; balances only per dispatch) -----")


if __name__ == "__main__":
    main()
