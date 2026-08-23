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

