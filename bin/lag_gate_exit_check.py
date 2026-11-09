#!/usr/bin/env python3
"""lag_gate_exit_check.py — đọc-chỉ: tháng nào của LAG (neo known_date, nhân quả) có lợi suất 25 phiên TB > 0?

Luật user 09/11/2026 (kb/projects/lag-dd-zone-gate-20261109.md): chưa có dấu hiệu đáy; khi có 1 THÁNG DƯƠNG
trở lại ⇒ xem xét lại candidate của quý đó (user quyết, KHÔNG tự tắt cổng); mốc 15/12 xét lại.
Tháng DƯƠNG = TB ret > 0 VÀ số sự kiện >= MIN_N (tháng ít sự kiện chỉ là nhiễu). Chỉ IN, không ghi gì.
"""
import sys
import pandas as pd
MIN_N = 30
f = sys.argv[1] if len(sys.argv) > 1 else "/home/trido/thanhdt/WorkingClaude/data/lag_edge_health.csv"
d = pd.read_csv(f, parse_dates=["entry", "known_date"])
g = d.groupby(d["known_date"].dt.to_period("M")).ret.agg(mean="mean", n="count", win=lambda s: (s > 0).mean() * 100)
g = g.tail(8)
print(f"nguồn {f}; known_date cuối = {d.known_date.max().date()}; entry cuối = {d.entry.max().date()}")
print(g.round(2).to_string())
last = g.index[-1]
pos = g[(g["mean"] > 0) & (g["n"] >= MIN_N)]
print(f"\nTHÁNG DƯƠNG đủ mẫu (n>={MIN_N}) trong 8 tháng gần nhất: {[str(i) for i in pos.index] or 'KHÔNG'}")
print("=> " + ("CÓ tháng dương ⇒ báo user xem lại candidate quý đó" if len(pos) and pos.index[-1] == last
               else "chưa có tháng dương mới nhất ⇒ giữ cổng"))
