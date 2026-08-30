# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate: bin/discretionary_candidate_funnel.py — PB threshold giờ là OR-logic ĐÃ WIRE
  (cutoff=70%, trần=1.2, cơ sở universe_pit∩Volume>0), thay PB<1.0-only cũ. Commit 714b5889.
  113->136 mã (+23). TV1(pb1.084/pct50.3%)/DGC(pb1.006/pct46.1%) đều lọt.
  Trải qua 3 vòng quant-skeptic: REFUTED(data-snoop 2 bậc)->REFUTED(hẹp, chỉ trần)->CONFIRMED.
- **PHÁT HIỆN QUAN TRỌNG**: TV1 VÀ DGC đều marginable=NO qua DNSE hiện tại — dù lọt phễu, không
  dùng được margin lúc này.
- Quality/insider/marginability 23 mã mới: 17/23 pass floor literal, 9/23 nếu golden_floor
  production nghiêm ngặt.
- Risk-auditor CONDITIONAL-APPROVE 2 cụm ngành: CTCK (ρ crisis 0.49-0.78, đề xuất cap count≤1 AND
  exposure≤5%NAV), hoá chất/phân bón (ρ 0.38-0.78, đề xuất cap≤1 margin-armed HOẶC ≤2 cash-funded).
- **CHƯA IMPLEMENT hard cap** — Taylor chủ động dừng đúng chỗ (funnel stateless, không biết case nào
  đang ARM thật; enforcement thật phải ở discretionary_margin_gate.py, file khác, cần thêm khái
  niệm funding-type margin/cash cho cụm hoá chất). Đã thêm cảnh báo INFORMATIONAL thay thế
  (unit-tested, fire đúng). Rủi ro CHƯA hiện hữu (0 cảnh báo fire hôm nay).
- **CHỜ USER QUYẾT**: có làm job riêng thiết kế+implement hard cap thật ở discretionary_margin_gate.py
  ngay không, hay để sau.

## §16 gate tốt-nghiệp — ĐÓNG (review tay APPROVED 30/08 12:52, gate LIVE)

## Chuỗi R&D 30/08 khác — đóng
- custom30V accrual-quality: 3/3 phép thử NO-GO, đóng hẳn trục này.
- NPL/CAR: không nguồn free — giữ proxy ROE_Min3Y/Gordon-PB.
- Sector sweep: đóng hẳn, coverage đủ 20/20.
- C1 (DC-swap): củng cố REFUTED.
- Insider cluster-buy: NO-GO — spread ÂM có ý nghĩa đúng subset dd52<=-20%.

## Đang chờ / mở nhỏ
1. capit-lever selfcheck 2 FAIL (Wags/capit-lever-selfcheck-2-remaining-fail-permission-blocked):
   Urgency THẤP-TRUNG BÌNH, user chưa cho ý kiến.
2. Security leak VM: user đã tạo VM riêng, theo dõi tiến độ khi có cập nhật.
3. bus question retro-pattern-recurring-checker-hardcode-diagnosis-3 (Pattern A, lần 3 checker
   hardcode chẩn đoán) — chờ Mike/user quyết biện pháp mạnh hơn.
4. dt5g-writer-la-1931-ngoai-moi-cua-so-20260828 — chờ data-ops truy JOBS_BY_PROJECT.
5. job_cancel_guard_selfcheck FLAKY — theo dõi.
6. job quant-skeptic_20260830_085357: bookkeeping bug (process chết sau verdict CONFIRMED nhưng
   record kẹt running/OVERDUE) — không sửa được (bị chặn), không quan trọng, đã verify substance
   qua log trực tiếp.

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

- [2026-08-30T09:55:54Z] 30/08 16:55: user chốt KHÔNG cần implement hard cap ở discretionary_margin_gate.py — phễu chỉ chọn candidate, quyết định đầu tư thật đi qua DD workflow -> DollarBill lập plan -> user duyệt. Cảnh báo informational hiện có (đã wire, unit-tested) là đủ. Item đóng hẳn — PB-adaptive threshold chain (3 vòng quant-skeptic + wire + risk-auditor) HOÀN TẤT KHÔNG CÒN VIỆC MỞ.
- [2026-08-30T10:08:42Z] 30/08 17:08: user hỏi 8L có nên adaptive như PB không -> đã trả lời nguyên tắc phân loại (neo GIÁ = ứng viên adaptive; neo KINH TẾ TUYỆT ĐỐI ROE>=0/CF>0 = fix đúng; rating<=3 gate = user khoá chủ đích 07-27 không mở lại) + dispatch Taylor_20260830_100832 audit read-only: kiểm kê ngưỡng cứng rating_8l.py, câu hỏi trung tâm = bins rating 1-8 cắt bằng cutoff tuyệt đối hay rank cross-sectional. Không sửa code.
- [2026-08-30T10:13:38Z] 30/08 17:14: audit 8L thresholds XONG — verdict KHÔNG CẦN ADAPTIVE MỚI. Trục value đã adaptive từ 06-16 (rank pct + pb_z vs 5Y chính mã), không có cutoff tuyệt đối neo giá nào. Tỷ số vận hành (ROIC/ROE/FSCORE cutoff) có trôi 2-4x theo chu kỳ NHƯNG là tín hiệu kinh tế thật — adaptive-hoá sẽ xoá tín hiệu chu kỳ, KHÔNG đề xuất. Không mở hướng nghiên cứu mới. Item đóng.
