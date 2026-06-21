# -*- coding: utf-8 -*-
"""trading_bot — bot giao dịch theo plan V2.3, broker PHS FLEX (DNSE sau này).

Pipeline:
  1. EOD (sau khi golive_recommend_v23 + pt_v22_dt5g chạy xong):
         python bot_prepare_plan.py            → data/trade_plans/plan_<T+1>.json
  2. Trong phiên T+1:
         python bot_execute.py                 → cắt lệnh nhỏ, đặt/đuổi/hủy, journal

Mode:
  paper (mặc định) — quote thật từ PHS, khớp mô phỏng, tiền ảo (data/bot_paper_account.json)
  live             — đặt lệnh thật qua PHS FLEX (cần client_id/secret PHS cấp + Smart OTP)
"""

__version__ = "0.1.0"
