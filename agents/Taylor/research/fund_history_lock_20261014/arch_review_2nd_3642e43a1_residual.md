# Arch-review lần 2 (agent a13d14d496b048ff0) — commit 3642e43a1, 14/10 ~10:40 ICT — NEEDS_CHANGES
Chỉ ghi phần CHƯA nằm trong REVIEW.md vòng 1 / job vòng 2 (Taylor_20261014_033336). Phần "đạt" đã kiểm độc lập: 07-02 −4.429.292đ, 08-06 950.871.323 / 937.070.077, 18 số Δ=0, selfcheck 5 bộ x 3 TZ rc=0, mutant 78/78, md5 data thật không đổi.

## R1 (chặn, mới) — khoá không tự kiểm, không mốc ngoài kho
- sổ/manifest/.superseded/nav_history_corrections.jsonl bị gitignore (*.csv, *.jsonl) ⇒ không git, không backup.
- Thử sandbox: chốt --immutable rồi xoá CẢ file sổ + manifest ⇒ đối chiếu in "0 dòng ... khớp", rc=0 (docstring hứa bắt được xoá — chỉ đúng khi xoá riêng file sổ).
- Cần: (a) mốc ngoài kho mỗi lần seal/restate (SEAL_MD5 lên bus — đã có ở B13 vòng 2; thêm: pin_ledger.py vào data/pinned_ledgers có git HOẶC bus event); (b) lệnh đối chiếu chỉ-đọc có chế độ `verify-anchors`: so với mốc ngoài, rc≠0 khi mốc nói "đã chốt" mà file/manifest mất — (Mike tự lo phần cron, KHÔNG làm crontab); (c) daily_nav_snapshot ghi đè dòng quá khứ: Mike QUYẾT ĐỊNH KHÔNG sửa daily_nav_snapshot.py (giữ = master) ⇒ phát hiện bằng đối chiếu thay vì chặn.
## R2 (chặn, mới) — bảng D thiếu kênh Discord EOD
- list_reports chỉ quét mike/reports/*.md (báo cáo ngày có file từ 08-11). Tin EOD Discord là số đã công bố: eod_trading_report.log.1.gz:899 "NAV 2026-08-07: 961,311,265 VND (+0.12%)". Sau chèn 08-06: +1,098% ⇒ Δ +0,97 điểm % >0,5 = bậc 3 theo khoá "day".
- Cần: thêm hàng EOD 08-07 vào bảng D; quét/ghi nhận mọi dòng "NAV <ngày>: ... (±x% so với hôm trước)" trong eod_trading_report.log* cho ngày 07-02..08-17 để tìm các bậc 3 tương tự; output impact ghi rõ phạm vi quét (.md từ 08-11; Discord EOD qua log).
## Không chặn mới (ngoài REVIEW.md): N2 _is_real_dir (đã ở B2 vòng 2), N3 đối chiếu chỉ-đọc không lấy khoá (B12), N5 khoá chung (B4), N6 cổng chốt không kiểm giá trị — nên bắt buộc cash_identity (bước 6) trước seal thật, N7 ghi "agent đổi mốc, phần dư không đổi" cho acks, N8 delete ngày không tồn tại coi là "already" ⇒ phải lỗi (G19), N9 .md.bak_sent_* (B7), N10 nguồn 2 VHM (B11).
