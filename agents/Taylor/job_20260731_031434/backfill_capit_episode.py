# -*- coding: utf-8 -*-
"""BACKFILL 1 LẦN: dựng data/capit_episode.json cho episode CAPIT đang mở (entry 2026-07-20).

Vì sao cần: sổ episode chỉ MỞ khi gate chuyển False->True. Gate đã tắt từ 07-29, nên nếu không
backfill thì bản chạy 19:00 hôm nay sẽ thấy sổ rỗng và episode đang giữ THẬT (5 mã, 2 account)
vẫn vô hình — đúng cái lỗ hổng job này vá.

Nguồn input = artifact đã ghi của từng ngày (deploy_golive_dt5g_v4/out/*.csv, book=CAPIT), tức
tái dựng từ bản ghi lịch sử chứ không phải gõ tay. Bằng chứng vị thế/fill do chính module đọc lại
từ broker log. Kết quả đã được replay_capit_episode.py kiểm (PASS) trước khi chạy file này.

Idempotent: chạy lại không tạo episode trùng (khoá theo episode_id).
"""
import os, sys, csv, glob
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
import capit_episode

days = []
for p in sorted(glob.glob(os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "out",
                                       "golive_v23_recommendations_*.csv"))):
    d = os.path.basename(p)[len("golive_v23_recommendations_"):-len(".csv")]
    if d < "2026-07-13":
        continue
    basket, w = [], 0.0
    with open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("book") == "CAPIT":
                basket.append(r["ticker"]); w = float(r["weight_pct"])
    days.append((d, sorted(basket), round(w * len(basket) / 100.0, 4)))

SESSIONS = [d for d, _, _ in days]
for d, basket, size in days:
    out = capit_episode.update(d, bool(basket), basket, size, SESSIONS, workdir=WORKDIR)
print("BACKFILL DONE ->", capit_episode.LEDGER_PATH)
print("episode_open =", out["capit_episode_open"], "| id =", out["capit_episode_id"],
      "| entry =", out["capit_episode_entry_date"], "| sessions_held =", out["capit_sessions_held"])
