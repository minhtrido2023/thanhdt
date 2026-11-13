# Luồng A3 — làm 3 việc quant-skeptic khuyến nghị trước khi đặt mặc định LIQ_ZERO_BLOCK=lag + LAG_ADV_SRC=pit (user duyệt 13/11/2026 09:1x ICT, phương án (a))
PAPER-ONLY. Nhánh nền: feat/live-gap-exec-A2-20261113 (4f7609c34; repo /home/trido/thanhdt, worktree riêng). Báo cáo A2: agents/Taylor/research/live_gap_exec_A2/REPORT.md; skeptic CONFIRMED (bus live-gap-exec-A2-20261112). KHÔNG merge, KHÔNG đổi neo sizing −25,2%.
1. Quét LAG_ADV_MINP ∈ {10,20,40} (pit, LIQ=lag), pin0% và pin1M: CAGR, IS/OOS, 2015, DD5 bootstrap (circular L=21,B=4000,seed 12345, in 2 chữ số thập phân). Cơ sở chọn MINP phải khớp adv_vnd live — nêu rõ.
2. Chạy L3 (adj v2 = cơ sở LAG cache điều chỉnh đang live trên main 97b2a7197) với LAG_ADV_SRC=pit + LIQ=lag: số mới cho dải và DD5 sàn trên đúng cơ sở production. Control byte-identical, self-check 0 VND.
3. Bootstrap lại mọi chân A2 ở 2 chữ số thập phân để phân giải chênh DD5 <0,1pp.
4. Sửa câu cơ chế 2015 trong REPORT/registry: fill ảo không trần của CẢ HAI loại (ADV≤0 và ngày NULL), không chỉ ADV≤0.
5. Chuẩn bị (CHƯA merge) commit đặt mặc định LIQ_ZERO_BLOCK=lag + LAG_ADV_SRC=pit trên nhánh, knob lùi LIQ_ZERO_BLOCK=off / LAG_ADV_SRC=bq giữ byte-identical số pin cũ; tên file output phải mang trục (CLAUDE_GUIDELINES §8). Registry: ghi mục mới có ledger_md5 hoặc no_ledger (cổng pin-artifact-gate).
Báo cáo REPORT.md + bus finding live-gap-exec-A3-20261113 (heartbeat mỗi 4-5 tool call). Quy ước dải: chỉ trích số kèm pin0%/pin1M.
