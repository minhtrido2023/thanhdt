# Brief — Refactor topic "New deals" (user DUYỆT 17/11/2026 17:2x ICT, decided_by: user)

Vấn đề: `/home/trido/thanhdt/WorkingClaude/newdeals_daily_report.py` (cron 06:00 ICT T2-T6, topic new_deals) đăng sổ paper ĐÓNG BĂNG
(AlphaLens hết hạn 30/09 nhưng vẫn đăng; DC Book seed chụp 26/06), không gắn DD, không có mốc "tuổi dữ liệu".
Dữ liệu nền thì MỚI (ticker_financial có 2026Q3 ~1131 mã, rating_8l.csv 16/11, DCF season 15/11).

## 4 phần user đã duyệt
1. **Gỡ AlphaLens** hẳn khỏi báo cáo (giữ file data để audit, ghi lý do hết hạn). DC Book chuyển từ seed cố định sang **sổ theo mùa**
   (đặt lại mỗi mùa BCTC; lưu seed của mùa trước vào lịch sử, KHÔNG xoá).
2. **Kích hoạt theo mùa BCTC**: khi BCTC quý mới phủ ≥~80% watchlist (đo từ ticker_financial, quý mới nhất / watchlist), một cron/hook
   chạy vòng làm mới: tính lại rating 8L, dựng lại tập Golden/Strong + double-confirm, so với vòng trước → danh sách mã VÀO/RA/ĐỔI HẠNG.
   Idempotent theo (mùa), không chạy lặp; tái dùng `dcf_refresh_gate.py --season` làm mẫu slot-by-season nếu hợp.
3. **DD cho mã đổi trạng thái**: mã mới vào/đổi hạng → xếp hàng DD theo skill `due-diligence` (đọc `~/.claude/skills/due-diligence/SKILL.md` bản
   MỚI NHẤT 11/11 + `dd-investor-report` nếu cần báo cáo): Bobby sector MÙ → Taylor DD → fundamental-skeptic. **TRẦN 5 mã/mùa** (ưu tiên
   double-confirm có MoS tốt; phần dư xếp hàng mùa sau, ghi rõ). Kết quả ghi `dd_price_zones.json` kèm quý BCTC đã dùng. Phần BUILD chỉ dựng
   hàng đợi + hook gọi + ghi "dd_asof_quarter" — KHÔNG tự chạy DD hàng loạt trong lượt build (báo Mike danh sách mã để Mike dispatch DD).
4. **Chặn nhãn cũ**: báo cáo hằng ngày thêm (a) cột/nhãn "DD asof <quý>" per mã, (b) dòng đầu về độ tươi: BCTC phủ x%, rating ngày nào, DCF mùa nào,
   tuổi sổ (ngày). Mã có DD cũ hơn quý BCTC mới nhất ⇒ gắn "⚠️ DD cũ (Qx)" và KHÔNG hiện ACCUMULATE/STRONG như hợp lệ (user chọn: gắn cảnh báo,
   không ẩn hẳn).

## Ràng buộc
- RESEARCH/MONITOR ONLY: không đụng custom30V/BAL/LAG/rating_8l.py/trading_rules/lệnh. Không cài cron mới — chỉ ĐỀ XUẤT dòng cron (Mike cài sau arch-review).
- Giữ cổng `report_return_gate` (§21) fail-closed như cũ; selfcheck cho phần mới (kể cả TZ `env -u TZ`); mutation test cho nhãn "DD cũ" và trigger mùa.
- Dùng worktree riêng (`git worktree add`), commit + push nhánh, KHÔNG sửa trực tiếp main. Tra `kb/data_registry/` trước khi chọn nguồn dữ liệu.
- Sổ paper tiếp tục theo khung ngày chuẩn; ghi rõ khung ngày khi so với production (như hiện tại).
- Không có file `dd_price_zones.json`-schema mới tuỳ tiện: đọc schema hiện có (grep trong mike/bin) và tái dùng.
## Deliverable
Nhánh + diff + selfcheck pass + REPORT.md ngắn (đã đổi gì, dòng cron đề xuất, danh sách mã đổi trạng thái mùa Q3 hiện tại + tuổi DD hiện có từng mã). Ghi bus finding khi xong.
