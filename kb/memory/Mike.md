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
- [2026-08-30T11:41:29Z] 30/08 18:41 user duyệt Phase A+B stress-test V2.4 qua khủng hoảng cơ cấu 2007-2012+2018 -> dispatch Taylor_20260830_114100 (timeout 1h). Phase A: DT5G state replay cấp chỉ số ~2007-2008, kiểm gate behavior + trụ Mỹ 2018. Phase B: V2.4 backtest cấp cổ phiếu từ ~2008-2009 (không phải 2007-04, anchor thật cụm = 2012-01). User cho rằng golden floor 8L lọc mã sắp huỷ niêm yết -> ghi rõ đây là GIẢ ĐỊNH chưa verify được (BQ không còn data cơ bản mã chết), không tự nhận confirm. Câu hỏi Phase B là ĐỘ BỀN, không phải CAGR đẹp.
- [2026-08-30T11:51:27Z] 30/08 18:52: Stress-test khủng hoảng 2007-2012 XONG cả 2 phase. Phase A: DT5G tự vệ đúng 2 điểm then chốt (khoá CRISIS 06/2008-05/2009 ngăn false-ease; cap bắn trước giá 4.5 tháng 03/2011); XÁC NHẬN thực nghiệm điểm mù 2018 (DT5G=DT4 base bit-identical suốt 2013-2019, macro overlay không đóng góp gì). Phase B: tái dùng backtest đã CONFIRMED sẵn (AUDIT_START 2008), phát hiện cơ chế sống sót = TRÁNH NÉ không phải HẤP THỤ — chỉ đầu tư 9.8% số phiên, 2008/2009/2011 đầu tư=0 tuyệt đối (bỏ lỡ cả VNI+57.9% năm 2009), MaxDD cụm chỉ -7.86%, return cụm chỉ +1.49% (bảo toàn vốn). Giả định user về golden-floor lọc mã huỷ niêm yết VẪN KHÔNG kiểm chứng được (quá ít hoạt động đầu tư trong window này). Drilldown Phase B CHƯA qua quant-skeptic — chờ user xem trước khi dispatch verify.
- [2026-08-30T12:16:24Z] 30/08 19:15: User yêu cầu tìm cơ chế production cho 2 episode: 2009 rally bị bỏ lỡ + 2018 điểm mù. Bobby BLIND read XONG (file vn_macro_regime_history_2009_2018_phases.md, đính chính EP-2018-01 -> EXTERNAL_CYCLE; 2009 nhận ra được từ T9-10 qua premium chợ đen+trade deficit+tín dụng; 2018 MSCI EM đỉnh 26/01 trước VN 2 tháng, bẫy Vinhomes deal -> phải dùng bán ròng KHỚP LỆNH). Dispatch Taylor_20260830_121551 (1h): câu A tách nguyên nhân 2009 (gate đè vs data artifact, lưu ý EASING_FLOOR đã tắt có chủ đích), câu B chỉ báo vá 2018 pre-register + false-positive toàn lịch sử. Không wire, chờ user quyết.
- [2026-08-30T12:24:52Z] 30/08 19:25: production mechanism 2009/2018 research XONG. Câu A 2009: nguyên nhân THẬT = SIGNAL_V11 gate cứng đòi state BULL/EXBULL mà DT5G không bao giờ đạt 2008-2013 (không phải state-gate đè, không phải data artifact chính). Ứng viên: valuation-gated tier-unlock qua pb_z (KHÔNG revive EASING_FLOOR đã bác đúng) — nhưng chưa verify được cho 2009 (thiếu warm-up). Câu B 2018: bán ròng khớp lệnh KHÔNG khả thi data (nguồn chỉ từ 08/2018); DIVERGE VN-vs-EM bắt đúng 22/03/2018 (đúng tuần đỉnh) nhưng FP 37% toàn lịch sử; thêm DXY/UST confirm giảm FP nhưng xoá early-warning. 2 hướng mở chờ user quyết: (1) valuation-gated tier-unlock, (2) DIVERGE test cấp chiến lược. Không wire gì.
- [2026-08-30T12:43:43Z] 30/08 19:43 user duyệt cả 2 hướng mở -> dispatch song song: Taylor_20260830_124256 (valuation-gated tier-unlock SIGNAL_V11, giải warm-up trước, pre-register trước khi nhìn 2009) + Taylor_20260830_124326 (DIVERGE indicator cấp chiến lược, pre-register cơ chế cap bổ sung, đo NAV impact ròng 27 episode qua walk-forward IS/OOS). Cả 2 không đụng production, bắt buộc quant-skeptic trước wire.
