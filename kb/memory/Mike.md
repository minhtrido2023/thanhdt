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
- [2026-10-08T14:07:07Z] 08/10 21:0x: telemetry Wags_20261008_133633 NEEDS_CHANGES (0 blocker, 3 should-fix: job xong bị ghi cancelled nếu SIGTERM trong cửa sổ telemetry; thiếu whitelist key ghi job record/tách bin/job_telemetry.py; xếp hạng chuỗi tách sai chain_tokens) — nhánh feat/dispatch-token-telemetry-20261008 bba411f3 wt agents/Wags/wt-tokentel-1008, chưa merge. Đo: dispatch sonnet trả 'OK' tốn $0,27, gần hết là 66,7K token context nạp đầu. CHỜ USER duyệt vòng 2 cho CẢ 2 nhánh (trim + telemetry).
- [2026-10-08T14:33:26Z] 08/10 21:3x: user DUYỆT vòng 2 cả 2 nhánh. Trim: Wags_20261008_143309 (sonnet medium; 8 fix + đóng 3 mục cũ + bỏ INDEX đã-đóng khỏi pack, mục đang-mở chuyển current_ops, INDEX vào kb_recall). Telemetry: job opus medium (3 should-fix + 2 test). NEEDS_CHANGES ⇒ dừng báo, không vòng 3.
- [2026-10-08T14:43:09Z] 08/10 21:4x: trim vòng 2 Wags_20261008_143309 NEEDS_CHANGES (8 cũ đã sửa đúng; pack 78→43KB; còn 1 blocker canonical:59 V2.5 thiếu NO-GO + 4 should-fix văn bản: rail R3 đã có code đọc từ adb125b7, consolidate warn nuốt cảnh báo, pin R3/neo DD đo @0,30 còn live 0 chưa re-pin, current_ops:55 mất pointer). Nhánh e143a7cb chưa merge. Đề xuất user: Mike tự sửa 6 chỗ văn bản + verify + merge (không dispatch vòng 3). Telemetry Wags_20261008_143324 còn chạy.
- [2026-10-08T15:01:38Z] 08/10 22:0x: telemetry vòng 2 Wags_20261008_143324 NEEDS_CHANGES: 3 should-fix ĐÃ sửa đúng (47/47, dispatch thật khớp $0,2529); còn chặn: docstring ví dụ spend_report.py:244 làm dispatch_round_cap_selfcheck FAIL + nit (try/except mục report, đổi marker +Nk, docstring gộp chuỗi bắc cầu). Nhánh eacd6dfb wt-tokentel-1008 chưa merge. CHỜ USER 'ok tự sửa' cho CẢ 2 nhánh (trim e143a7cb + telemetry eacd6dfb) — Mike tự sửa + chạy selfcheck + merge, không dispatch vòng 3. Không còn job nền.
- [2026-10-08T15:23:46Z] 08/10 22:3x: XONG ops-review mục 1+4. Telemetry merged mike 99742afe (dispatch thật Winston_20261008_152121: 1 lượt $0,25, cache_creation 62K ⇒ mỗi dispatch GHI cache mới, không tái dùng). Trim merged 4446e0fa, context_pack 78→44KB, current_ops+canonical 71→42KB, INDEX đã-đóng ra khỏi pack. Mike tự sửa vòng cuối (user duyệt 22:14), không dispatch vòng 3. CÒN MỞ cần user: re-pin R3/neo DD ở park 0. Mục 2/3/5/6: làm ~15/10 sau 1 tuần telemetry (spend_report.py --days 7 mục Top chuỗi).
- [2026-10-08T15:39:07Z] 08/10 22:5x: rà R&D bị loại vs pin R3 hạ → reports/rnd_rejected_vs_corrected_r3_review_20261008.md. Kết luận: bug OShares có HƯỚNG theo bank-share ⇒ Q-sleeve/sector-cap/pool-widen bị phạt oan (chưa chạy lại); hurdle live = Trứng vàng 8,5%. Đề xuất 5 nhánh, chờ user chọn (ưu tiên: re-pin park=0 + chân egg-rate; BAL>12 tên khi LAG đói deal; đọc sổ paper DC-book quá hạn review).
- [2026-10-08T15:54:42Z] 08/10 22:5x: user duyệt làm TUẦN TỰ 5 nhánh R&D (report rnd_rejected_vs_corrected_r3_review_20261008.md). Nhánh 1 = re-pin R3 park=0, idle = dep1m Big-4 PIT (user: KHÔNG dùng lãi egg 8,5%) — dispatch Taylor job Taylor_20261008_155435 (opus high, --bg). Xong ⇒ verify_finding quant-skeptic ⇒ trình user ⇒ mới sang nhánh 2 (BAL>12 tên khi LAG đói deal).
- [2026-10-08T16:21:56Z] 08/10 23:2x: Nhánh 1 XONG — Taylor_20261008_155435 (commit 555bd103), quant-skeptic CONFIRMED medium (log verify_20261008_162033). park0: sàn 22,12% / trần 25,42%; neo DD GIỮ −25,2%; park0 vs 0,3 dưới dep1m không phân biệt được. Registry .proposed chưa ghi. CHỜ USER duyệt pin + có chạy 2 rerun skeptic gợi ý (W2b noise floor park0; leg 2019-03+ không bridge) không. Sau đó mới nhánh 2.
- [2026-10-08T16:32:25Z] 08/10 23:4x: Nhánh 1 ĐÓNG — user duyệt 23:30, pin park0 vào kho (537e349b/a6ba34d8), registry outer main 7d62f6fc, KB canonical mike 175107ac, neo DD giữ −25,2%. Nhánh 2 (BAL MAX_POS>12 khi LAG idle) dispatch Taylor_20261008_163222 opus high — có cổng rẻ bước 0 (ứng viên rank13-20 bị chặn bởi trần). Xong ⇒ verify_finding --topic bal-maxpos-lag-idle ⇒ trình user. Sau đó nhánh 3 (DC-book đọc sổ paper).
