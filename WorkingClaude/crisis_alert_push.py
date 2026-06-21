#!/usr/bin/env python3
"""
crisis_alert_push.py — daily Telegram push for the DT5G x 8L capitulation signal.
Pushes ONLY on a live WATCH/STRONG signal (build_market_alert returns None when
DORMANT), so it's silent on normal days. Wire into papertrade_daily.bat.
"""
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from dna_report import build_market_alert

msg = build_market_alert()
if not msg:
    print("capitulation: DORMANT — no push."); sys.exit(0)
print(msg)
try:
    from telegram_recommend import send_telegram_text, load_config
    cfg = load_config()
    ok = send_telegram_text(cfg["bot_token"], cfg["chat_id"], msg).get("ok")
    print("telegram push ok:", ok)
except Exception as e:
    print("telegram push skipped:", e)
