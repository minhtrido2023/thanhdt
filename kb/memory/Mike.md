# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (dọn cuối ngày 2026-10-08, sau retro)
- **Retro 2026-10-08 ghi xong**: kb/incidents/retro/retro-2026-10-08.md. 1 sự cố (backup
  `mike-fleet` kẹt 1 lượt push vì PAT hết hạn, tự lành lượt kế 00:00 ICT 09/10 — xem
  `logs/backup.log:4284-4285`), 1 pattern tái diễn (backup-silent-failure shape thứ 5, cơ chế
  phát hiện ĐÚNG thiết kế, chỉ thiếu alert real-time tại điểm fail). Wags GAPS FOUND (2, đã sửa:
  root cause + đếm bus event). Chưa escalate (lần đầu gặp Pattern F).
  Đề xuất còn mở: thêm alert ngay khi `fleet_backup.sh` gặp `FAIL fleet push` (hiện chỉ biết qua
  freshness-check 8,5h sau) + xác nhận cơ chế renew PAT.
- **5 nhánh R&D hậu re-pin park0 đang chạy** (user duyệt làm tuần tự, report
  `reports/rnd_rejected_vs_corrected_r3_review_20261008.md`):
  1. re-pin R3 park=0 (dep1m PIT) — ĐÓNG, pin vào kho 537e349b/a6ba34d8.
  2. BAL MAX_POS>12 khi LAG idle — NO-GO (skeptic CONFIRMED high), đóng.
  3. DC-book đọc sổ paper state-gated — ĐÓNG (commit 9c9e3878, review event-anchored).
  4. **Rerun nhóm B trên engine đã sửa bug** — job `Taylor_20261008_172556` ĐANG CHẠY (bg, opus
     high, deadline ~2h từ 17:25 ICT 08/10, hb sống). Xong ⇒ `verify_finding --topic
     rerun-groupB-fixed-engine` ⇒ trình user ⇒ sang nhánh 5 (cổ tức tiền).
  5. Cổ tức tiền — chưa bắt đầu.
- PFM (adjfactor PRICE_FIELD_MISMATCH) + non-blocker + AWAITING_TRADE: tất cả MERGED master
  (18f2317c, d484fb41, 787ddac4). Chỉ còn non-blocker văn bản nhỏ `alert.sh` ~57-59, không gấp.
- Ops-review mục 1 (token telemetry) + mục 4 (context_pack trim 78→44KB) ĐÃ XONG, merged
  (99742afe, 4446e0fa). Mục 2/3/5/6 làm ~15/10 sau 1 tuần telemetry.
- Selfcheck-red backlog: ĐÃ CHỐT chủ sở hữu cố định (Wags mike/bin, Taylor gốc WC), cron Thứ Sáu
  16:30 ICT `bin/selfcheck_red_owner_sweep.sh` (commit 523d9524). Lượt đầu 09/10 tối — kiểm log.

## Đang chờ
- Job `Taylor_20261008_172556` (nhánh 4 rerun nhóm B) — chờ xong, không cần wakeup thăm dò (user
  10-05: không poll rỗng khi không có job nền; job NÀY thì có, nhưng tool poll sẽ tự biết qua
  jobs.sh khi cần, không cần ScheduleWakeup lặp).
- Plan funnel 8L discretionary: chờ user duyệt bản cutloss cuối sau 5 phiên shadow (~12/10).
- Shadow cutloss (intraday_price_watch) chạy từ 06/10 11:10, tổng kết ~12/10.
- sbv-weekly-check 07/10 fetch_failed (fallback "assumed unchanged") — nếu lặp ngày tiếp theo,
  escalate Winston/data-ops.
- Cron tuần 12/10 08:05 ICT (CCTG/Big-4, 6M song song 12M) — kiểm Winston ghi đúng.
- Pattern E (DT5G/macro_health SEV giả do edge-case ngày/giờ, tái diễn lần 4, retro 07/10) — đề
  xuất job quét tổng call-site thiếu guard, CHƯA user duyệt có làm hay không.

## Next
- Kiểm job nhánh 4 (Taylor_20261008_172556) khi xong → verify_finding → trình user.
- Sáng 09/10: kiểm `logs/selfcheck_red_owner_sweep.log` (lượt đầu cron Thứ Sáu).
- KHÔNG đặt wakeup thăm dò khi không có job nền đang chờ kết quả (user 10-05).

- [2026-10-08T18:15:56Z] 09/10 01:2x: Nhánh 4 xong — Taylor_20261008_172556 c8e096e7, skeptic CONFIRMED high (verify_20261008_181403). Q8/Q12 hết ý nghĩa, QF8/fc30 NO-GO hẹp, L1b chưa chứng minh (DSR<0.95), claim breadth sai OOS. CHỜ USER: duyệt sửa câu canonical breadth + .proposed registry + nhánh 5.
- [2026-10-09T03:08:11Z] 09/10 10:1x: user duyệt cả 2: (1) registry nhánh 4 + đính chính breadth — WC bb9fbd95, mike 7feee631 (q-sleeve.md + INDEX). (2) nhánh 5: snapshot corp-action daily ĐÃ có từ 08-17 (52 vintage) ⇒ không cần cron mới; vendor thêm first_disclosure_datetime 09-14 (15.894 dòng từ 2015) ⇒ dispatch Taylor_20261009_030802 (opus medium) thẩm định cột này PIT hay không; A ⇒ study chạy ngay thay vì chờ 2027-08. Xong ⇒ trình user (chưa chạy study).
- [2026-10-09T03:19:01Z] 09/10 10:2x: Nhánh 5 ĐÓNG — first_disclosure_datetime = C (không PIT), bẫy ghi data_registry + INDEX (commit trên). Cả 5 nhánh R&D hậu re-pin park0 ĐÃ ĐÓNG; còn mở theo trigger: DC-book event-anchored, L1b@≤0,3 khi trigger park lãi hạ, announcement study ≥2027-08.
- [2026-10-09T03:59:36Z] 09/10 11:0x: user duyệt dọn mục B — đính chính answer adjfactor-round3 (correction_of 75c17009), comment wags_autofix.sh:464 (e6748e86), đóng wags-fix-not-confirmed coord-10-08 + 10-09. Bus còn 19 pending, toàn selfcheck-red.
- [2026-10-09T05:50:05Z] 09/10 12:5x: user duyệt dòng phụ DT gate 'nền xấu N phiên liền (xoay BEAR<->CRISIS)' + ngưỡng xem lại ≥15 phiên & VNINDEX ≤−5% ⇒ chạm thì đề xuất user giao Taylor backtest luật gộp bộ đếm. WC 53e2b305 (dna_report.py, hiển thị). Replay: từng chạm 12/2014, 07/2018 (gần đáy, sau đó hồi).
- [2026-10-09T09:35:05Z] 09/10 16:4x: rà việc tồn. (1) sweep selfcheck-red 16:30 hỏng do OAuth refresh race (tự lành 16:31) — xoá marker .done, chạy lại: Wags_20261009_093350 + Taylor_20261009_093353 (tự báo Architecture). BUG nhỏ: sweep ghi .done khi 'sent' chứ không khi job done ⇒ job hỏng bị bỏ cả tuần — đề xuất user. (2) Shadow cutloss 4/5 phiên: hạ tầng ổn, nhưng 3 trigger đều PNJ (excluded, không giữ), 0 điều tra/0 lệnh dự định ⇒ chưa có mẫu thật; phiên 5 = 12/10. (3) SBV weekly fetch_failed MỌI tuần từ ≥08-07 mà vẫn stamp last_verified — đề xuất Winston sửa/đổi nhãn, chờ user. (4) macro_health FAILED 15:00-15:30 hôm nay do bq lỗi thoáng qua trong cron SBV, sau đóng cửa, 15:30 HEALTHY lại.
- [2026-10-09T09:48:55Z] 09/10 16:5x: user duyệt 3 việc. (a) Taylor_20261009_094633 replay lịch sử cutloss intraday (opus high, 2h) ⇒ xong thì quant-skeptic verify ⇒ trình user. (b) Winston_20261009_094651 gộp kiểm lãi điều hành NHNN vào cron tuần Thứ Hai 08:05 (verified_at vs attempted_at, stale>21 ngày cảnh báo, retire fetch Thứ Sáu) — hạn trước 08:05 12/10, kiểm artifact sáng T2. (c) sweep selfcheck-red: stamp lưu job_id + lượt bù 18:52 T6 — mike adca34f7 + crontab (backup state/crontab_backup_*_sweep_retry.txt). (d) Việc 3: user chấp nhận cảnh báo backup 8h; Mike đề xuất cảnh báo TRƯỚC khi PAT hết hạn (header github-authentication-token-expiration = 2026-11-15) — chờ user duyệt.
- [2026-10-09T10:47:41Z] 09/10 17:5x: replay cutloss xong (Taylor_20261009_094633, commit de182a88). quant-skeptic REFUTED medium (verify_20261009_104604): số tái lập đúng, không look-ahead, NHƯNG headline 'cutloss thua hold' do ~60 ca LAG micro/penny <1B ADV; ADV≥10B (202 ca) T1 +0,04% T5 +0,98% T20 +1,28% CI chứa 0. Kết luận thực tế giữ: KHÔNG live, shadow tiếp. CHỜ USER: (1) có cho Taylor chạy lại cắt theo thanh khoản trên danh mục đang giữ không; (2) sbv-policy-source-b-window A/B/C; (3) cảnh báo PAT trước hạn 15/11.
- [2026-10-09T11:03:15Z] 09/10 18:0x: user duyệt cả 3 + sửa lỗ hổng. Dispatch: Taylor_20261009_110243 (sửa 3 lỗ hổng intraday_price_watch shadow + replay v2 theo ADV/danh mục thật, phải merge trước 09:00 12/10 — xong thì Mike chạy verify_finding --topic intraday-cutloss-replay-v2); Winston_20261009_110301 (SBV source B 120 ngày, đóng question decided_by user); Wags_20261009_110303 (cảnh báo PAT ≤14/≤3 ngày trong backup_freshness_check, PAT hết hạn 15/11).
