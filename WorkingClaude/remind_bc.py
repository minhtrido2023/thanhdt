#!/usr/bin/env python3
"""remind_bc.py — one-shot Saturday reminder (Telegram) to run 8L rating overlays (B) & (C).
Scheduled via Windows Task 'Remind_8L_BC' for 2026-06-06. Self-deletes the task after firing.
"""
import sys, subprocess
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
MSG = ("⏰ <b>Nhắc thứ Bảy — 8L rating overlays</b>\n"
       "Chạy &amp; backtest prod-spec 2 ý tưởng còn lại cho v11/v12.1:\n"
       "• <b>(B) distress-exclusion</b>: loại rating-5 (lỗ cả năm/đòn bẩy cực đoan) khỏi pick momentum — "
       "test cắt tail-risk mà không giết winner.\n"
       "• <b>(C) regime-conditional sizing</b>: rating điều tiết size CHỈ trong BEAR/CRISIS (Ngũ Hành≤2); "
       "bull để momentum chạy tự do.\n"
       "Chi tiết: memory rating_8l_credit_scale_2026 (mục ⏰ TODO THỨ BẢY).")
try:
    from telegram_recommend import send_telegram_text, load_config
    cfg = load_config()
    print("telegram:", send_telegram_text(cfg["bot_token"], cfg["chat_id"], MSG).get("ok"))
except Exception as e:
    print("telegram failed:", e)
# self-cleanup the one-shot task
try:
    subprocess.run('schtasks /delete /tn "Remind_8L_BC" /f', shell=True, capture_output=True, text=True)
except Exception: pass
