"""Account ID constants — đọc từ secrets/trading_bot_accounts.json (gitignored).

Import module này thay vì hardcode account number trong selfcheck hay script.
"""
import json
import os

_ACCOUNTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "secrets", "trading_bot_accounts.json")


def _get_account_id(label: str) -> str:
    with open(_ACCOUNTS_FILE, encoding="utf-8") as f:
        accounts = json.load(f)["accounts"]
    for a in accounts:
        if a.get("label") == label:
            aid = a.get("account_id")
            if aid:
                return str(aid)
    raise KeyError(f"account '{label}' không tìm thấy hoặc thiếu account_id trong {_ACCOUNTS_FILE}")


SPACEX = _get_account_id("SpaceX")
ZALOPAY = _get_account_id("ZaloPay")
