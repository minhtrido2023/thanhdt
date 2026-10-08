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
- [2026-10-08T04:23:28Z] 08/10 11:23: job Taylor_20261008_032221 TIMEOUT giữa r2 (chưa merge); Mike commit WIP 779a31ea trong wt-await-1008; redispatch resume Taylor_20261008_042322 (opus medium, timeout 3600).
- [2026-10-08T05:50:39Z] 08/10 12:50: Taylor_20261008_042322 DONE nhưng DỪNG ở arch-review (NEEDS_CHANGES), CHƯA merge; head 25cf9a22 wt-await-1008. 4 blocking B1-B4 (alert.sh:237/458 state-write lỗi nói sai+khoá DRIFT cũ chặn ≤7 ngày; :560 dùng [ -n $DRIFTS ]; test khe 1-2 phiên; chạy lại dry-run trên r3). CHỜ USER cho phép vòng r4 (cần DISPATCH_ROUND_CAP_OVERRIDE).
- [2026-10-08T05:53:17Z] 08/10 12:53: user duyệt vòng r4 cuối — dispatch Taylor_20261008_055312 (opus medium, override round-cap). NEEDS_CHANGES lần nữa ⇒ dừng hẳn, báo user.
- [2026-10-08T07:13:09Z] 08/10 14:1x: adjfactor AWAITING_TRADE MERGED master 18f2317c (r4 arch-review APPROVED; selfcheck master 570/570 Mike tự chạy). Kiểm lượt cron thật đầu 07:10 ICT 09/10: 8 mã chờ giao dịch lại gộp 1 dòng info, DRI/DVN/SHC/VHF vẫn DRIFT. Worktree wt-await-1008 có thể dọn.
- [2026-10-08T07:41:17Z] 08/10 14:4x: kiểm lại DRI/DVN/SHC drift theo câu admin (làm tròn): vendor hệ số ĐÚNG (DRI 1,0725 vs ta 1,072464; DVN 1,0580 vs 1,05848; SHC 1,05), KHÔNG phải làm tròn (10đ ≤0,04% < tol 0,3%) mà trường Price thô lệch Close 1-2 bước giá (DRI 09-10/11/14, DVN 06-19..23) hoặc đứng giá (SHC 06-30..07-09, KL≈0); cả ngày không sự kiện DRI 09-25/09-30/10-06 Close=Price+100. Đề xuất detector nhãn 'lệch trường Price' thay DRIFT — CHỜ user duyệt.
- [2026-10-08T08:01:14Z] 08/10 15:0x: user duyệt (1)+(2). Dispatch Taylor_20261008_080048 (opus high) nhãn PRICE_FIELD_MISMATCH trong detector, Taylor tự báo. Báo cáo admin reports/bq_admin_price_close_mismatch_20261008.md (2.278 phiên lệch đơn lẻ/887 mã 2026; đề nghị admin lưu giá thô 1 lần + thêm cột adj_factor).
- [2026-10-08T09:57:08Z] 08/10 16:5x: PFM r2 4737f414 NEEDS_CHANGES (arch-review vòng 2), CHƯA merge. Blocker R1: cửa sổ 120 ngày trượt qua cụm PFM ⇒ DRIFT giả (DRI ~08/01/2027). Dry-run: DRI/DVN/SHC/CC1 → PFM, VHF/HC1/PBP/VFR giữ DRIFT. CHỜ USER chọn A (vòng 3 sửa R1, cần DISPATCH_ROUND_CAP_OVERRIDE nếu bị chặn) / B (ghi giới hạn, merge).
- [2026-10-08T10:00:25Z] 08/10 17:00: user chọn A — dispatch Taylor_20261008_100015 (opus medium, vòng 3 cuối) sửa R1 + 6 non-blocker; APPROVED ⇒ merge, NEEDS_CHANGES ⇒ dừng báo user. Bus answer decided_by=user đã đóng.
- [2026-10-08T10:44:35Z] 08/10 17:4x: PFM r3 45179c7d NEEDS_CHANGES lần nữa (lỗi MỚI B1: win0 giữa cụm PFM ≥4 phiên ⇒ DRIFT giả, SHC ~29/10-04/11, hướng báo thừa). R1 đã sửa. CHỜ USER: (B) sửa câu sai alert.sh:56+docstring rồi merge [Mike đề xuất] / (A) vòng 4 / chế độ B opus high.
- [2026-10-08T10:49:38Z] 08/10 17:49: user chọn C — dispatch Taylor_20261008_104928 (opus high, chế độ B, timeout 2h): review toàn nhánh PFM, thiết kế quy tắc không phụ thuộc vị trí cửa sổ, sửa B1+NB1-3+NB5, mô phỏng trượt asof 0 DRIFT giả, arch-review 1 lần. NEEDS_CHANGES ⇒ dừng báo user.
- [2026-10-08T11:50:09Z] 08/10 18:5x: PFM MERGED master d484fb41 (chế độ B, arch-review APPROVED high 0 blocker). Mike tự chạy selfcheck master 822/822 env -u TZ. Kiểm cron 07:10 ICT 09/10: DRI/DVN/SHC/CC1 → 1 dòng info PFM, VHF/HC1/PBP/VFR DRIFT. Non-blocker còn: cron_registry.md:138 thân dòng + adjfactor_drift_daily.sh:4-8 vẫn ghi 00:10.
- [2026-10-08T12:02:44Z] 08/10 19:03: user yêu cầu sửa non-blocker PFM rồi merge — dispatch Taylor_20261008_120235 (sonnet medium, chế độ A): NB1-6 + mutation Mk/Mc/Md, arch-review 1 lần, topic bus adjfactor-pfm-nonblockers.
- [2026-10-08T12:34:45Z] 08/10 19:3x: non-blocker PFM vòng 1 NEEDS_CHANGES (B1 test ≥2 cụm span d0/d1). Dispatch vòng 2 sonnet test-only + 2 sửa nhỏ, user đã cho phép 19:02.
- [2026-10-08T13:14:43Z] 08/10 20:1x: non-blocker PFM MERGED master 787ddac4 (arch-review r2 APPROVED, 843/843, mutation 142/142). Còn 1 chú thích nhỏ alert.sh ~57-59. Kiểm cron 07:10 ICT 09/10.
- [2026-10-08T13:31:13Z] 08/10 20:4x: user hỏi rà kiến trúc vận hành — báo cáo reports/ops_architecture_review_20261008.md (5 phát hiện: context_pack 78KB vượt OKF 2×, 20% job là vòng review lặp, retro 3 LLM job/ngày, không telemetry token, 20 phiên Discord sống). 6 đề xuất, CHỜ user chọn làm mục nào.
- [2026-10-08T13:37:01Z] 08/10 20:4x: user DUYỆT plan ops-review — làm mục 4+1 trước. Dispatch Wags_20261008_133633 (telemetry token per-job, dispatch.sh+spend_report) + Wags job context_pack trim (≤25KB, cổng 30KB current_ops+canonical). Cả 2 opus high chế độ B, arch-review 1 lần, NEEDS_CHANGES ⇒ dừng báo. Đính chính: spend_report.py ĐÃ có tổng token (4,08 tỷ, cache 97%) + retry 19%; thiếu là per-job. Mục 2,3,5,6 làm sau khi telemetry chạy ~1 tuần.
- [2026-10-08T13:56:52Z] 08/10 20:5x: context_pack trim Wags_20261008_133659 NEEDS_CHANGES (8 required, chưa merge; nhánh chore/context-pack-trim-20261008 f10b0326, wt agents/Wags/wt-ctxtrim-1008). Đạt 78→46KB, chưa tới 25KB (sàn 39KB nếu giữ nguyên mọi mục mở). CHỜ USER: duyệt vòng 2 sonnet sửa 8 điểm + đóng 3 mục cũ (arm VPB đã [], runbook rc=5 đã live, canonical park 0,30 lỗi thời) + có bỏ INDEX.md khỏi pack không. Telemetry Wags_20261008_133633 vẫn chạy.
