---
kind: project
owner: Taylor
status: closed-nogo
updated: 2026-11-16
title: "LAG thoát sớm / stop-loss theo Bayes — NO-GO (user duyệt 16/11/2026 10:43 ICT, `decided_by: user`)"
---
# LAG thoát sớm / stop-loss theo Bayes — NO-GO (user duyệt 16/11/2026 10:43 ICT, `decided_by: user`)
Câu hỏi user: sau mua LAG bao lâu / lỗ bao nhiêu % thì biết deal lỗ, có luật thoát sớm theo xác suất không. Job `Taylor_20261116_031549` (opus). **Chưa qua quant-skeptic** — vì kết luận NO-GO nên không có gì để wire.

## Kết luận
- **Giữ nguyên LAG T+25 phiên, không stop-loss** (phương án A). Không làm B (cảnh báo display) hay C (thoát 50%).
- Biết "sẽ lỗ" sau ~5-7 phiên (AUC cum 0,71-0,75): lỗ >5% ở phiên 7 ⇒ P(lỗ cuối) 0,64-0,67; >10% ở phiên 10 ⇒ 0,77; phiên 15 ⇒ 0,84.
- **Nhưng E[lợi suất còn lại nếu GIỮ] dương ở mọi ô (phiên × mức lỗ)** (vd phiên 10 lỗ >10%: +6,5% CrI90 [4,2; 8,7]) — deal lỗ sâu sớm hay hồi phục. Spearman(cum, còn lại) 0,00-0,10. Feature thêm (mdd/drawdown từ đỉnh/rel VNINDEX/volume/rvol/gap/ADV/state) không vượt lỗ lũy kế.
- 0/60 luật checkpoint hơn giữ ở cả pin0% và pin1M (tốt nhất pin1M +3,8bp, DSR 0,07; pin0% −4,2bp); 0/60 dương cả IS+OOS; PBO 0,30/0,29. Stop cứng −10%: −159bp/deal (pin1M), 67% lần bán thấp hơn giá cuối, 70% lần vị thế >20% GTGD phiên bán (engine lạc quan). Placebo circular-shift: thoát ngẫu nhiên không tệ hơn (p 0,53-1,00).
- N: 668/663 deal, 88 cụm tháng vào, N_eff ~162 (ICC 0,47), N_trial 125; live 11 deal (2 đóng) chỉ mô tả. Không chạy NAV backtest (không luật nào qua mức deal).

## Artifact
Nhánh `research/lag-early-exit-20261116` @`f037ad41f` (KHÔNG merge, giữ làm tham khảo); REPORT (worktree đã xoá 19/11, đọc từ nhánh): `git show research/lag-early-exit-20261116:agents/Taylor/research/lag_early_exit_bayes_20261116/REPORT.md`; ledger gốc `80f509ec` (pin0%).

## Đừng đề xuất lại trừ khi
Có dữ liệu mới đáng kể (≥2-3 mùa BCTC live đóng đủ deal) hoặc PREREG riêng với feature ngoài giá (tin tức PIT, thay đổi dự báo). Liên quan: cổng DD ≤ tâm lúc MUA (`lag-dd-zone-gate-20261109.md`) là hướng khác, xử lý phía vào lệnh.
