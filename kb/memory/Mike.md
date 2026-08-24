# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (2026-08-24, đầu ngày)

### Go-live V2.4 lever — LIVE TỪ HÔM NAY 08-24
- fill_timing → FALSE, extreme_regime_enabled → TRUE, capit_margin_lever.enabled → TRUE (SpaceX + ZaloPay)
- Mỗi ngày có CAPIT margin: `approve_margin_day.py --account <acct> --date <date> --approved-by "John"` TRƯỚC bot — ngày đầu tiên chạy thật, theo dõi sát.

### Signal holds — KHÔNG tự đổi
- VPI/BAL: HOLD đến 2026-09-16. SpaceX + ZaloPay: HOLD_ALL (theo VPI hold).

### Việc đã lên lịch
- **Thứ Bảy 2026-08-29**: implement code chính sách margin đơn mã discretionary (`kb/projects/discretionary-margin-policy-20260823.md` §"VIỆC KẾ TIẾP") — nhánh cấp phép riêng, KHÔNG tái dùng apply_capit_lever, 4 rào chắn số (vị thế ≤3% NAV, sleeve ≤5% NAV, exit tự áp -20%), selfcheck + cân nhắc arch-review. Dời có chủ đích để tránh đụng plan.py/executor.py đúng lúc capit_margin_lever LIVE lần đầu.

### Còn hở nhỏ (low priority, không cần chủ động nhắc)
- `order_book_execution_shadow`: 0/40 outcome coverage
- `probe_linger_live_gate`: vẫn True (paper-only)
- `PHSBroker.get_nav()` vẫn dùng get_cash()-based (§25 gap) — rủi ro 0 (toàn paper mode), escalate nếu có account PHS live tương lai

### Đóng sổ 08-23 (KHÔNG tự nêu lại)
- Margin-valuation-spread Phase 1: NO-GO wire (6 vòng, quant-skeptic CONFIRMED). Chính sách margin đơn mã discretionary: POLICY DUYỆT, CHƯA CODE.
- Code-quality Tier 1+2: LIVE, cron Sun 10:00 ICT. Chu kỳ đầu tiên đóng hoàn chỉnh (finding→fix→verify).
- Retro 2026-08-23 (2 sự cố: §25 tái diễn lần 3 ở DNSEBroker.get_nav() — đã fix; Wags verify-live self-referencing — đã fix, rule mới OPS_HEALTH_DRY_RUN=1 bắt buộc khi verify chạm dispatcher). Wags verify GAPS FOUND (1 gap nhỏ, ngày checkpoint) đã sửa. File: `kb/incidents/retro/retro-2026-08-23.md`.

- [2026-08-24T00:13:23Z] 2026-08-24 07:15 ICT: đính chính KB margin-valuation-spread (commit 3f3dc416, merged) theo phản biện user với số liệu CPI/lãi suất liên NH 10/2010 thật. Trục mới: phòng-thủ-có-mục-tiêu (2020 COVID, 2022 SCB - dễ hồi) vs cơ-cấu-tự-cộng-dồn (2007-2012, multi-year). 3/7 episode có thể là 1 khủng hoảng, N thật ~4-5. Không đổi NO-GO Phase 1. Candidate nghiên cứu SAU (không phải hôm nay - go-live capit_margin_lever sáng nay): gộp episode theo cụm khủng hoảng liên tục, đo fwd-return từ điểm cơ cấu THẬT bắt đầu xử lý, PIT-hoá trục 2 bằng văn bản chính sách lúc đó.
- [2026-08-24T00:44:13Z] 2026-08-24 07:47 ICT: Tạo agent native macro-strategist (~/.claude/agents/macro-strategist.md, commit b789dd9b MIKE.md routing merged) — user duyệt sau phát hiện Taylor vừa đọc vĩ mô vừa chạy backtest (đồng thuận sớm, bỏ sót trục phòng-thủ vs cơ-cấu). Vai trò: đọc vĩ mô ĐỘC LẬP, KHÔNG biết forward-return/giả thuyết đang test, khác quant-skeptic/fundamental-skeptic (không phải công tố). Deliverable: kb/data_registry/market-state/vn_macro_regime_history.md (chưa tạo file, agent tự tạo lần đầu dùng). Smoke test lần đầu FAIL — agent chưa xuất hiện trong danh sách Agent tool phiên này (harness cache, giống pattern fundamental-skeptic hôm qua). CẦN: thử lại phiên sau hoặc lượt sau để xác nhận hoạt động, rồi giao việc đầu tiên: đọc lại độc lập 7 episode margin-valuation-spread.
- [2026-08-24T01:02:57Z] 2026-08-24: điều tra heartbeat 'Vẫn đang xử lý' cho user — KHÔNG phải regression bug 07-17 (_finished guard vẫn hoạt động, log 00:13:41 fire → 00:13:43 cancel). Root cause kiến trúc: timer 120s append-only, mù completion + mù activity, message không bao giờ xoá → 1-6 lần/ngày heartbeat dính sát Done card. Đề xuất fix ccdb: (1) edit-in-place 1 message/run, (2) xoá message trong set_done/set_error/cleanup, (3) optional activity-aware skip. CHỜ user duyệt mới sửa ccdb (shared infra, cần restart ccdb-mike).
- [2026-08-24T01:09:43Z] 2026-08-24 08:07 ICT: Bobby (macro-strategist) đặt tên xong (commit acd867c6/f6d9c1d2). Smoke-test PASS thật: phân loại độc lập episode 2022-05 SCB → CONFIDENCE_LIQUIDITY+CONTAINABLE, KHỚP CHÉO với bảng Mike tự đọc hôm qua (không biết nhau). Registry kb/data_registry/market-state/vn_macro_regime_history.md tạo xong, entry đầu (commit b3bfd62f). Còn 4 episode chưa phân loại độc lập (2007-08, 2011-12, 2018, 2020) — dispatch Bobby riêng từng cái khi cần, giữ nguyên tắc blind-to-outcome. Vai trò Bobby CHÍNH THỨC hoạt động, sẵn sàng dùng.
- [2026-08-24T01:20:00Z] 2026-08-24 08:18 ICT: XONG fix heartbeat ccdb — commit 6ad86bb merged main, ccdb-mike.service đã restart sạch (verified log + resume đúng session). edit-in-place + delete-on-cleanup + lock, 23/23 test pass. Chưa làm activity-aware skip (tuỳ chọn, để sau nếu cần).
- [2026-08-24T02:55:13Z] 2026-08-24 09:5x ICT: XONG fix false-positive paper-main early-check — commit 1c640f54, merged master. Root cause: Monday net-BUY-only ngày (factor 0.85>0.70 Friday) → mọi mã net BUY, chân SELL netting về 0, journal chỉ HYBRID_DEFER vì hybrid_buy_blocks không mở tới 11:00 ICT — checker cũ coi đây = ghost-guard/TZ bug (07-08/09), SAI. Đã thêm nhánh phân biệt: journal thuần HYBRID_DEFER + còn block phía trước → ℹ️ benign thay vì 🔴, exit 0, reset streak. Verify: 4 unit test synthetic + live-test journal thật hôm nay đều đúng. Đã tự trả lời user luôn trong Trading Daily qua chính lần chạy test thật.
