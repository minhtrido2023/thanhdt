# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (chuỗi 30/08 lớn, đã đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate: bin/discretionary_candidate_funnel.py — PB OR-logic (cutoff=70%, trần=1.2,
  cơ sở universe_pit∩Volume>0) đã WIRE, commit 714b5889. 113->136 mã. TV1/DGC lọt nhưng cả 2
  hiện marginable=NO qua DNSE. Risk-auditor CONDITIONAL-APPROVE 2 cụm ngành (CTCK/hoá chất) —
  hard cap KHÔNG implement (user chốt 16:55: DD workflow là đủ, cảnh báo informational đủ dùng).
  3 vòng quant-skeptic: REFUTED->REFUTED(hẹp)->CONFIRMED. Item đóng hẳn.

## Đang chạy
- Taylor_20260830_103253: gộp 7 episode dd52 lịch sử theo CỤM khủng hoảng liên tục (không theo
  lần chạm ngưỡng riêng lẻ), đo N độc lập thật + forward return từ đúng điểm bắt đầu xử lý.
  Chỉ để hiểu bản chất — KHÔNG mở lại margin theo giai đoạn thị trường.

## Chuỗi R&D 30/08 khác — đóng
- custom30V accrual-quality: 3/3 phép thử NO-GO. Sector sweep: đóng, coverage 20/20.
- C1 (DC-swap): củng cố REFUTED. Insider cluster-buy: NO-GO.
- Audit 8L thresholds: KHÔNG cần adaptive mới (trục value đã rank/z-score based sẵn).
- NPL/CAR: không nguồn khác ngoài vnstock (user xác nhận), giữ proxy ROE_Min3Y/Gordon-PB.

## Vận hành — dọn sạch 30/08 17:32, không còn việc treo lỗi thời
- capit-lever selfcheck 2: CLOSED-FIXED từ 08-28 (memory cũ báo sai là "đang chờ").
- retro-pattern checker hardcode lần 3: CLOSED 08-28 bởi Wags (lint rule + checklist).
- job_cancel_guard_selfcheck: chỉ là noise đã dismiss trong audit tuần trước, không phải item riêng.
- dt5g-writer-la-1931 (writer bí ẩn ghi DT5G production): ĐIỀU TRA RA + ĐÓNG — là UPDATE thủ công
  đã user duyệt (backfill asof_date sau fix bug MERGE 4bc6d2f4), không phải writer lạ. Trước đó
  bị dispatch NHẦM sang việc khác nên chưa từng điều tra thật — nay đã đóng đúng bus question
  với bằng chứng (time-travel diff BQ + checksum khớp tuyệt đối).
- Security leak VM: user có VM riêng, chỉ theo dõi thụ động, không cần hành động.
- job quant-skeptic_20260830_085357: bookkeeping cosmetic (process chết sau verdict CONFIRMED,
  record kẹt hiển thị running/OVERDUE) — không sửa được (bị classifier chặn), không quan trọng,
  đã verify substance qua log trực tiếp. Không cần theo dõi thêm.

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

- [2026-08-30T10:51:28Z] 30/08 17:52: episode clustering re-analysis XONG. N=7->N=5 (gộp cụm 2007-2012 = 1, giữ 2018-05 riêng thành nhóm C thứ 3 vì không phòng-thủ-được VÀ không gộp cụm được). Tách bạch RÕ hơn nhị phân cũ: min(B phòng-thủ +26.3%) > max(A∪C +21.2%) ở mốc 12m. Trung thực N=1 cho 2 nhóm — mô tả định tính, không CONFIRMED thống kê. Verdict cũ KHÔNG đổi (Phase1/margin-valuation-spread vẫn NO-GO). Toàn bộ chuỗi hôm nay 30/08 ĐÃ XONG, không còn job chạy.
