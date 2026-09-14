# -*- coding: utf-8 -*-
"""trading_bot — bot giao dịch theo plan V2.3, broker PHS FLEX (DNSE sau này).

Pipeline:
  1. EOD: data/trade_plans/plan_<account>_<T+1>.json do DollarBill lập (strategy "V2.4").
         (bot_prepare_plan.py + V23Strategy đã gỡ 2026-09-13, cq-20260913-remove-v23.)
  2. Trong phiên T+1:
         python bot_execute.py                 → cắt lệnh nhỏ, đặt/đuổi/hủy, journal

Mode:
  paper (mặc định) — quote thật từ PHS, khớp mô phỏng, tiền ảo (data/bot_paper_account.json)
  live             — đặt lệnh thật qua PHS FLEX (cần client_id/secret PHS cấp + Smart OTP)
"""

__version__ = "0.1.0"
