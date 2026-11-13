# Luồng A vòng 2 — đo lại LIQ_ZERO_BLOCK=lag sau khi xử lý lỗ NULL Volume_3M_P50 (user duyệt 13/11 01:1x ICT)
PAPER-ONLY. KHÔNG merge, KHÔNG đổi production/trading_rules/neo sizing -25,2%. Worktree riêng từ main (đã có vá mergesort f210c726b). Nhánh cũ tham chiếu: feat/live-gap-exec-A-20261112 (A2 = dbfd9a4af). Báo cáo cũ: agents/Taylor/research/live_gap_exec_A/REPORT.md.
## Bối cảnh (quant-skeptic INCONCLUSIVE, bus live-gap-exec-A-20261112)
BQ ticker.Volume_3M_P50 NULL trên ngày có giao dịch 2015-09..2016-06 (2015-10: 4.479/11.713 dòng, 276 mã, nhiều mã thanh khoản tốt ~2 tỷ/ngày; sau 2022 chỉ ~0,2-0,4%). LIQ_ZERO_BLOCK=lag chặn các mã đó ⇒ LAG 2015Q4 14,2B vs 21,8B, lợi suất 2015 19,4%→5,7%. Live feed hôm nay không chặn các mã này. Còn: simulate_holistic_nav.py:1203 dùng liquidity_lookup[(tk,today)] ở ngày fill (T+1) nên Volume_3M_P50 gồm cả khối lượng ngày fill — đo độ nhạy. pt_v22_dt5g.py:489 hardcode liquidity_require_positive=True (từ 32d65bbf6): sửa câu "blast radius" cho đúng.
## Việc
1. Dựng đường ADV thay thế KHÔNG NULL (vd tự tính từ Volume ngày: trung vị 60 phiên trước t, PIT, KHÔNG gồm ngày fill) — kiểm bằng đối chiếu với Volume_3M_P50 khi không NULL (sai số) và phủ các ngày NULL.
2. Chạy lại ladder L1 (mergesort, LIQ=off) và L2 (LIQ=lag) với ADV thay thế, cả pin0% và pin1M, park 0, AUDIT_END 06-19, threads=1, self-check 0 VND, control byte-identical. So với L2 cũ (5ae929c6/52b39597): IS/OOS, 2015, DD5 bootstrap (circular L=21,B=4000,seed 12345).
3. Tách phần hiện vật NULL khỏi phần "khớp live": báo CAGR/DD5 của L2 sạch NULL. Nêu số mới cho neo sizing (DD5 sàn) — CHỈ báo, không đổi.
4. Có dùng được làm mặc định không? Nêu rõ kết luận + điều kiện; không đổi mặc định trong job này.
Ghi REPORT.md + bus finding live-gap-exec-A2-20261112 (heartbeat mỗi 4-5 tool call). md5 mọi output; nêu lệnh tái lập. Quy ước: chỉ trích số kèm pin0%/pin1M.
