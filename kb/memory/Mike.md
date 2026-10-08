# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (cập nhật 2026-10-08 00:42 ICT, cuối ngày 07/10 — dọn sau retro)
- Broker corp-action PRIMARY: r7-r10 MERGED mike master bacf6e99 (07/10 13:1x-14:4x), mặc định SHADOW
  (`MIKE_CA_BROKER_SOURCE` chưa set). Cron 19:25 tối 07/10 đã chạy bản mới lần đầu, rc=0, registry
  sha không đổi (shadow, không ảnh hưởng live). Còn để sau live: 7 đột biến tương đương/nhẹ.
- DT5G FROZEN giả 19:03 ICT 07/10 (cửa sổ rỗng → NaT) đã vá merge WC b28d436f + breadth guard
  universe_pit cache merge WC a06c3ba3. **Kiểm sáng 08/10**: `data/refresh_v34b_linux_2026-10-08.log`
  không còn dòng "breadth guard inactive" + sync log đêm 07/10 có delta universe_pit OK.
- Sell-split BID ZaloPay: ĐÃ XÁC MINH XONG 07/10 13:50 ICT — bot bán đủ đúng 2 lệnh tách
  20@1258+7@1826, vị thế về 0. Không còn carry-over.
- Retro 2026-10-07 ghi xong: kb/incidents/retro/retro-2026-10-07.md (commit 8a207d01), Wags GAPS
  FOUND (3) đã sửa. Escalation selfcheck-red-backlog ĐÃ MỞ lần đầu — topic
  `retro-pattern-recurring-selfcheck-red-backlog-not-closed` (16 câu mở, cũ nhất 10 ngày).

## Đang chờ
- USER: phản hồi escalation `retro-pattern-recurring-selfcheck-red-backlog-not-closed` (cần giao
  chủ sở hữu cố định rà selfcheck đỏ, thay vì suppress 14 ngày tự trôi).
- USER: Pattern E (DT5G/macro_health báo SEV giả do edge-case ngày/giờ, tái diễn lần 4) — đề xuất
  job quét tổng call-site `get_gated_state`/`macro_health` thiếu guard cửa sổ rỗng/ngày lễ, chưa
  user duyệt có làm hay không.
- Plan funnel 8L discretionary: ĐÃ CHỐT (header sửa, merge mike 83533429) — chỉ còn chờ user duyệt
  bản cutloss cuối sau 5 phiên shadow (~12/10).
- Shadow cutloss (intraday_price_watch) chạy từ 06/10 11:10; tổng kết ~12/10. Tin "SHADOW ..." KHÔNG
  phải lệnh thật.
- Selfcheck-red backlog: 16 câu mở (cũ nhất 09-27), 0 đóng 07/10 — xem escalation trên.
- sbv-weekly-check 07/10 fetch_failed (fallback "assumed unchanged") — nếu lặp lại ngày tiếp theo,
  escalate cho Winston/data-ops điều tra nguồn feed SBV refi rate.
- Cron tuần 12/10 08:05 ICT (CCTG/Big-4 prompt mới, 6M song song 12M) — kiểm Winston ghi đúng.

## Next
- Sáng 08/10: kiểm log refresh_v34b không còn "breadth guard inactive" (xem trên).
- Thêm bước "kiểm lịch trading-day trước khi ghi gap dữ liệu" vào checklist retro (Pattern D
  07/10 — 3 retro liên tiếp 10-02/05/06 treo nhầm "corp-action feed thiếu 03-04/10" vì không ai
  chạy `date` để biết đó là Thứ Bảy/Chủ Nhật).
- KHÔNG đặt wakeup thăm dò khi không có job nền (user 10-05).

- [2026-10-08T02:11:26Z] 08/10 09:1x: user duyệt B — backlog selfcheck-red có chủ cố định (Wags mike/bin, Taylor gốc WC), cron Thứ Sáu 16:30 ICT bin/selfcheck_red_owner_sweep.sh (commit 523d9524), question đã đóng decided_by=user. Kiểm lượt đầu 09/10 tối: logs/selfcheck_red_owner_sweep.log + 2 finding selfcheck-red-owner-sweep-2026-10-09-*.
- [2026-10-08T02:22:31Z] 08/10 09:2x: cảnh báo VNINDEX intraday-watch 09:15:01 là lỗi giây-mở-phiên (DNSE phát bar sau khi phút đóng), KHÁC lỗi cache 07/10; vá merge mike 8912f6ae (grace 2' ở 09:15/13:00). Kiểm 13:00 hôm nay + 09:15 ngày 09/10: không còn HEALTH vnindex trong data/intraday_watch/shadow_*.jsonl.
- [2026-10-08T03:18:26Z] 08/10 10:2x: kiểm lời bq_admin 'mã không giao dịch nên vendor chưa điều chỉnh' trên 16 mã adjfactor drift 07/10 — đúng 9 (VHF IRC HES CKV INC PLE PIS PPS QHW), SAI 3 vendor_missing đã giao dịch lại vẫn lệch (DRI đang nắm 2 TK −0,70%/12 phiên, DVN −1,01%/19, SHC −12,1%/8), 4 mã chiều our_table_missing (CC1 HC1 PBP VFR). Đề xuất nhãn 'chờ giao dịch lại' trong detector — CHỜ user duyệt.
- [2026-10-08T03:22:28Z] 08/10 10:22: user duyệt sửa detector nhãn 'chờ giao dịch lại' — dispatch Taylor_20261008_032221 (opus high, thread này, arch-review + merge). Taylor tự báo kết quả. Kiểm sau: alert 07:10 ICT 09/10 chỉ còn DRI/DVN/SHC ở DRIFT.
