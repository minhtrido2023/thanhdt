# Working memory — Spyros
> Sổ tay việc ĐANG MỞ. File này bơm vào đầu MỌI phiên/dispatch của Spyros ⇒ mỗi dòng thừa là
> context phải trả tiền lại từ đầu, mỗi lần.

## Ghi gì vào đây (đọc 1 lần)
- Chỉ 2 loại: (a) việc CÒN TREO — đang chờ ai, chờ gì; (b) chốt làm ĐỔI CÁCH LÀM về sau.
- KHÔNG ghi "job X XONG, commit Y". git log + bus + `agents/Spyros/research/` đã giữ đủ; chép lại
  vào đây chỉ làm mọi phiên sau phải đọc lại một lần nữa.
- Mỗi entry ≤ 2 dòng: KẾT LUẬN trước, bỏ quá trình.
- Việc treo mà xong rồi thì XOÁ dòng đó, đừng ghi đè một dòng "đã xong" lên trên.
- Quy tắc dùng cho CẢ ĐỘI ⇒ đề xuất vào `kb/coding_guidelines.md` (§13: ghi ra `.proposed`),
  không nuôi riêng trong file này.
- Quá 12 entry thì phần cũ tự sang `kb/memory/archive/Spyros_history.md` — không mất, không auto-load.

- [2026-06-27T02:59:37Z] DONE: MGE=2.0 tail review (2026-06-27). VERDICT: REJECT 2.0, APPROVE 1.5 conditional. Key: S4 at 2.0x fires at -6.4% price (vs -31.5% at 1.3x) = W-bottom routine trigger not tail backstop; 2026H1 -3.7pp live warning. Cap MGE=1.5 (HARD=1.65, episode breaker -15%). 2.0x gate: revisit after 12M clean 1.5x track. BLOCKER-2 episode breaker needs update: -15% (not -12%) for 1.5x. BACKLOG: implement risk_monitor.py BLOCKER-2 update when Taylor/user approve 1.5x; EOD->BQ; recon fill<->ticker.
- [2026-07-21T12:15:48Z] EOD mismatch ZaloPay 07-21 đã audit xong: FALSE POSITIVE do bug eod_trading_report.sh không filter account_no khi đọc dnse_raw chung. ZaloPay fills đúng 100%. Code fix cần làm ở eod_trading_report.sh dòng ~184. BACKLOG: risk monitor realtime, EOD->BQ, recon fill<->ticker.
- [2026-07-21T12:17:52Z] DONE: eod-mismatch-SpaceX-07-21 audit (job Spyros_20260721_121033) — FALSE POSITIVE. Root cause: eod_trading_report.sh không filter account_no khi đọc dnse_raw → cộng nhầm ZaloPay fills vào SpaceX broker_filled. SpaceX execution OK (100% fill, no risk breach). BUG TO FIX: dispatch Mafee patch eod_trading_report.sh thêm filter account_no. BACKLOG: risk monitor realtime, EOD->BQ, recon fill<->ticker.
- [2026-07-24T01:24:11Z] [2026-07-24T01:30Z] DONE: DGC risk audit 07-23 (job Spyros_20260724_012025). Verdict: KHÔNG HALT. Root cause: khởi tố 3 lãnh đạo tại chức (CEO+HĐQT+Phó TGĐ). Vị thế: ZaloPay excluded ~10K cp, 379.5M VND (45% total NAV ZaloPay). Thanh khoản OK (1.3% daily vol, thoát 1 phiên). Không margin forced-sale. CẦN USER QUYẾT: có thoát DGC trước ĐHĐCĐ 13/08 không. Monitor: giá DGC daily, tin vụ án, CF_OA Q3/2026. BACKLOG: risk monitor realtime, EOD->BQ, recon fill<->ticker.
- [2026-07-28T01:24:26Z] DONE [2026-07-28T01:20Z]: VND IDIOCRASH audit 07-27 (job Spyros_20260728_012023). Verdict: HOLD_UNTIL_REBAL. Root cause: Q2 earnings FVTPL-driven (NP +139% YoY nhưng CF_OA -783B → đảo từ +4085B Q1), FSCORE 8→6. Vị thế: 400cp SpaceX ~6.14M VND (~0.4% NAV) — trivial. Liquidity OK. Không có pháp lý/hình sự. Risk_Rating=4 → nên review loại khỏi basket tại rebal 08-05. BACKLOG: risk monitor realtime, EOD->BQ, recon fill<->ticker.
