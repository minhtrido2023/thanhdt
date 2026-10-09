# Dự án Q-sleeve (rổ nhỏ chất lượng cao)
> Dự án đã đóng — tách khỏi context_pack 2026-07-12. Chi tiết gốc từ kb/current_ops.md.
> Status: CLOSED. NO-GO cả 2 trục, quant-skeptic CONFIRMED.

## Dự án "Q-sleeve" (rổ nhỏ chất lượng cao, cảm hứng AlphaLens) — ĐÓNG, NO-GO cả 2 trục (2026-07-12)
User đề xuất thêm 1 sleeve buy-and-hold rổ nhỏ chất lượng cao (lấy cảm hứng AlphaLens) bổ sung cạnh
BAL/LAG. Scope xong (`plan_quality_sleeve_20260712.md`), family N=5 pre-registered đã duyệt và
chạy: Q8-NEU/Q12-NEU/QF8-NEU (rổ nhỏ thay custom30V) + Q12-BULLEXT (mở rộng giữ cả lúc BULL) + LOO.

**VERDICT: NO-GO cả 2 trục, quant-skeptic CONFIRMED (không có phản bác).**
- **Trục rổ nhỏ thay custom30V**: cả 3 cách chọn đều kém control 2.9-6.8pp IS, LOO âm mọi năm bỏ-ra,
  phần "thắng" ở OOS chỉ là carry thuần từ năm 2021 (+20-24pp riêng năm đó) — đúng chữ ký lỗi đã bác
  ở MOM/fa8l trước đây. Cơ chế: rổ 30 mã hiện tại thắng nhờ breadth/diversification, cô đặc còn 8-12
  mã mất phần đó mà không có gì bù lại.
  ⚠️ **ĐÍNH CHÍNH 2026-10-09 (user duyệt, quant-skeptic CONFIRMED high)**: số trên đo trên engine còn bug custom30V double-count (control nặng bank bị thổi). Chạy lại trên engine đã sửa (job `Taylor_20261008_172556`, registry mục "2026-10-09 — NHÁNH 4"): Q8/Q12 **ngang** custom30V toàn kỳ (Δ +0,20/+0,18pp pin0%, −0,63/−0,36pp pin1M, trong nhiễu) ⇒ verdict cũ HẾT Ý NGHĨA; breadth chỉ thắng IS 2014-19 (−2,1…−3,9pp), **đảo OOS 2020+** (+1,4…+4,4pp) ⇒ câu "thắng nhờ breadth" KHÔNG còn đứng. QF8 vẫn NO-GO hẹp (−0,46/−0,57pp). Không có lý do đổi vehicle (live park=0).
- **Trục mở rộng BULL/EXBULL**: NO-GO lần thứ 5 liên tiếp (tiền lệ: bull-park, custom30B vehicle, R5,
  DC-book CÂU 1, giờ thêm Q-sleeve) — chết đúng năm tiền lệ hay chết (2025 −19.5pp).
- Diagnostic phụ: excess vốn-điều-chỉnh ÂM so custom30V, 1 mã chiếm 13.24% NAV vượt namecap 10%.

Không đụng production/canonical/trading_rules. Registry đã ghi mục "2026-07-12 — Q-SLEEVE". N-ledger
5/5 đóng sổ, không mở thêm trial.
