# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — CHỐT 30/08, LIVE
- Per-name cap: 5% NAV exposure (từ 08-29). Sleeve cap: 10% NAV (nới từ 5%, 08-30 11:52 ICT,
  commit 022c48e7). f hard-cap 1.3, %ADV≤10%, exit -20% tự áp.
- Trigger mở 15%: ≥3 case marginable đồng thời THẬT (Mafee xác nhận từng case, không phải giả
  định) → escalate Mike/user xem xét, KHÔNG tự động nới. Ghi trong code comment + 2 policy doc.
- Cơ sở: forensic combined-margin (margin ratio không chặn kể cả 15%) + correlation-risk thật
  (ρ crisis 0.17-0.19, risk-auditor CONDITIONAL-APPROVE, khuyến nghị 10% hợp lý hơn nhảy 15%).
- Selfcheck 23/23 PASS. Không chạm plan.py/executor.py/trading_rules.json.

## Chuỗi R&D 30/08 — đóng
- custom30V accrual-quality: 3/3 phép thử (gate pooled, tiebreak, gate sector-neutral) NO-GO.
  Đóng hẳn trục này, không đề xuất thêm biến thể.
- NPL/CAR: không nguồn free — giữ proxy ROE_Min3Y/Gordon-PB.
- Sector sweep: đóng hẳn, coverage đủ 20/20.
- C1 (DC-swap): củng cố REFUTED.

## Đang chờ / mở nhỏ
1. capit-lever selfcheck 2 FAIL (Wags/capit-lever-selfcheck-2-remaining-fail-permission-blocked):
   Urgency THẤP-TRUNG BÌNH, user chưa cho ý kiến.
2. Security leak VM: user đã tạo VM riêng, theo dõi tiến độ khi có cập nhật.
3. bus question retro-pattern-recurring-checker-hardcode-diagnosis-3 (Pattern A, lần 3 checker
   hardcode chẩn đoán) — chờ Mike/user quyết biện pháp mạnh hơn.
4. dt5g-writer-la-1931-ngoai-moi-cua-so-20260828 — writer LA ghi bảng DT5G production 19:31 ICT,
   dữ liệu không hỏng, chờ data-ops truy JOBS_BY_PROJECT.
5. job_cancel_guard_selfcheck FLAKY — theo dõi.
6. §16 gate tốt-nghiệp — Wags_20260830_033008 (opus/high) đang chạy song song: lint chặn
   datetime.now() trần vào pre-commit + ratchet + baseline audit 2 repo + arch-reviewer. Chưa xong.

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

- [2026-08-30T05:28:10Z] 30/08 12:27 §16 gate: CANCEL Wags_20260830_033008 sau 5 vòng arch-review NEEDS_CHANGES liên tiếp (9→2→8→1→7 mục, không hội tụ, vượt ngưỡng Pattern C). Git state sạch: mike 83c50fc4, WC e66b0256. Selfcheck 99/99 PASS thật (verify độc lập). Gate CHƯA CONFIRMED, đề xuất review tay thay vì dispatch tiếp. Chờ user quyết: review tay / dispatch người khác / bỏ.
- [2026-08-30T05:43:32Z] 30/08 12:43 user duyệt #1+#2 (wire marginability + lắp phễu candidate sleeve, Taylor_20260830_054255) + #3 (insider cluster-buy scoping, Taylor_20260830_054316) song song. #4 (backtest full universe kể cả mã chết) để sau, cần data mã huỷ niêm yết riêng.
- [2026-08-30T05:46:57Z] 30/08 12:47: #3 insider cluster-buy XONG — NO-GO, kết quả ngược giả thuyết (spread ÂM có ý nghĩa ở đúng subset dd52<=-20%, cả 4 định nghĩa, t=-3.6 đến -4.73). Không đầu tư writer/reader. #1+#2 marginability+funnel (Taylor_20260830_054255) vẫn đang chạy.
- [2026-08-30T05:49:46Z] 30/08 12:52 §16 gate REVIEW TAY XONG — APPROVED, giữ nguyên trạng (mike 83c50fc4, WC e66b0256). Mike tự chạy 20 test: detection 7/7, ratchet 2 chiều đúng, escape hatch đúng thiết kế (warn KHÔNG nâng baseline), R5-1 killer đã vá thật (SyntaxError không xoá baseline), 0 false-positive/400 file, shim F1 đã vá (repo ngoài track thật, không còn DNA_PYEXE), E2E pre-commit chặn+pass đúng, selfcheck 99/99 + mutation 27/27 KILLED. Gate LIVE, không cần dispatch thêm. Lưu ý nhỏ: files filter mike ^(bin|hooks|agents)/ phủ 612/612 hôm nay nhưng là giả định ngầm. Gap có chủ đích: pd.Timestamp.now() không chặn (ngoài phạm vi duyệt).
