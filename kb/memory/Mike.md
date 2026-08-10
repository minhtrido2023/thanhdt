# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-10 (cuối ngày, sau daily retro bước 3/3)

## Daily retro 08-10 — XONG
7 sự cố, 3 pattern. Wags verify GAPS FOUND → đã sửa (bổ sung sự cố #7
`approve_plan_simple.sh` false-block SHB-PARK SpaceX, commit `52190a1d`, tự sửa cùng ca; đính
chính mtime `plan_ZaloPay_2026-08-11.json` 19:08 ICT → 12:08:51 UTC, TRƯỚC 2 escalation không phải
SAU — chẩn đoán gốc check `plan_state_source_mismatch` không đổi). File:
`kb/incidents/retro/retro-2026-08-10.md`, commit `05ce4c9f`.

**Pattern 1 — "việc đã xong nhưng thiếu event đóng trên bus"**: 2 ca cùng ngày (#5 ZaloPay plan,
#6 coord-2026-08-10 saga) — không phải sự cố nghiêm trọng, chỉ nhắc kỷ luật đóng `question` bằng
`answer` event ngay khi xác nhận xong.

**Pattern 2 (KHẨN NHẤT) — SpaceX T+1 mất tích 2 ngày liên tiếp**: cùng hình dạng lỗi 08-09→08-10,
lần này (cho 08-11) VẪN CHƯA xử lý tới cuối ngày (đã qua cả 2 deadline 21:00/23:00 ICT).

**Pattern 3 — ESCALATED, sang retro thứ 3 vẫn treo**: backlog "chưa ghi file kb/incidents/" không
giảm (16→20, dù đóng thêm 2 file). Wags đã triage đầy đủ + khuyến nghị (nghiêng về "chấp nhận retro
backfill là đủ, sửa quy tắc 1-sự-cố-1-file") nhưng bus question `retro-pattern-recurring-2-days`
VẪN CHƯA có answer — đủ dữ kiện để CHỐT ngay, chỉ thiếu người quyết.

## Việc treo sang 08-11 (ưu tiên, KHẨN)
1. **KHẨN NHẤT**: SpaceX T+1 (2026-08-11) hoàn toàn KHÔNG có plan — 2 lần escalation
   `plan-t1-not-ready-SpaceX` không có answer, đã qua cả 2 deadline. Dispatch DollarBill sinh plan
   NGAY khi vào phiên tiếp theo, TRƯỚC 09:05 ICT (giờ bot chạy).
2. `retro-pattern-recurring-2-days` — Wags đã đưa khuyến nghị đầy đủ, cần user chọn (a) auto-stub
   file kb/incidents/ hay (b) chấp nhận retro backfill đủ + sửa quy tắc. Đưa cho user quyết dứt
   điểm, đừng escalate lại.
3. `verify_finding.sh` JSON trailing-comma bug — TÁI PHÁT LẦN 2, fix nhỏ đã biết (strip trailing
   comma trước json.loads), chưa ai vá — làm được ngay, không cần quyết chính sách.
4. `plan_state_source_mismatch` check (`send_plan_report.sh` ~168-176) — carryover 2 ngày, chưa
   sửa (so giá trị `state` thay vì chuỗi mô tả).
5. Park-trim patch (Taylor, job `Taylor_20260810_113500`) — chờ user/Taylor + quant-skeptic duyệt
   trước khi wire, KHÔNG tự áp.
6. 20 sự cố tồn đọng (7 từ 08-07 + 7 từ 08-09 + 6 từ 08-10) cần file `kb/incidents/` riêng — không
   khẩn nếu (2) chốt hướng (b).

## Kế thừa lâu hơn (theo dõi định kỳ, không cần hành động ngay)
- Sự cố #1 `compute_active_nav.py` availableCash bug — verify lại trạng thái thật trước khi dùng.
- ZaloPay park-trim display-only + plan ZaloPay 08-07 0 fill — chưa ai điều tra.
- Job cancel guard round 9 (commit `9e20bbf0`) — fail-closed an toàn nhưng chưa CONFIRMED tuyệt đối.
- Verify độc lập fix VHM (NAV-report + LotBook corp-action) — vẫn chưa có ai verify ngoài Taylor.
- lag-sizing-basis-lech-2-account (SpaceX %active_nav sai mẫu số) — cần xác nhận.
- Mafee live-lever-order test vẫn CHUA_KET_LUAN, cần user cấp quyền Bash đặt lệnh thật.
- PNJ TTL anomaly_flags (~08-23 review).
- coord-2026-08-07 saga bị arch-reviewer bounce 2 vòng, im lặng từ đó.
- BACKLOG kiến trúc (Wags): pin-theo-inode không hoạt động thật trong production (9/11 job
  pin_failed=1) — đề xuất bắt buộc pin lúc dispatch.sh tạo job, bỏ tree-match cũ. Quyết định thiết
  kế, chưa dispatch.

