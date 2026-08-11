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

- [2026-08-11T03:01:05Z] 2026-08-10: Áp dụng #4+#5 của đề xuất effort-drift (theo yêu cầu user, #2+#3 hoãn chờ báo sau). #5: thêm mục 5d vào Friday editorial review (bin/kb_nightly.sh, commit eca755bb) — check %effort=high per-agent qua spend_report.py sống, mirror 5b/5c fable/opus-drift. #4: ghi kỷ luật 'mặc định effort=medium cho dispatch tương tác' thành luật cụ thể vào MIKE.md (commit b00171f6), tự nhận lỗi đã phạm trong saga Wags cùng ngày.
- [2026-08-11T03:13:28Z] 2026-08-10: Hoàn tất #2+#3 của đề xuất effort-drift. #2: nudge động trong dispatch.sh (commit 0159582a) — chỉ nổi khi 10 dispatch gần nhất của 1 agent ≥70% high VÀ lần này cũng high, tránh lờn cảnh báo (đã verify bắn đúng '7/10' cho Taylor thật, im lặng khi medium). #3: rà 6 script tự động dispatch opus/high (ops_autofix/wags_autofix/fearbuy/paper_checkpoint/weekly_ops_audit/kb_nightly-ctxbloat) — 5/6 ĐÃ scoped đúng, chỉ 1 lệch thật (check_report_cadence.sh nhánh tuần: hạ model sonnet 08-04 nhưng quên effort vẫn high) → đã tách EFFORT theo nhánh, commit 3f8a74c4. Kết luận: vấn đề 'tùy tiện opus+high' nằm ở dispatch TƯƠNG TÁC (Taylor R&D qua Mike), không phải script tự động — #2+#4 đã target đúng chỗ.
- [2026-08-11T05:19:50Z] 2026-08-11: arch-reviewer NEEDS_CHANGES/high trên write-isolation fix (job_workspace.py, worktree wt-1536246356098814022, commit 460df6ed+af03a4ee) — 2 bug tôi tự vá (cherry-pick tip-only mất commit, conflict để lại cây chung dở dang) ĐÚNG nhưng còn killer objection: abort chỉ vá nhánh conflict, lỗi khác (vd index.lock của chính consolidate.sh) làm abort cũng fail, để lại .git/sequencer trong repo CHUNG, làm job lành kế tiếp bị gắn conflict giả kẹt vĩnh viễn. Thêm F1 meaningful_dirty lọc nhầm tầng (check ?? state//bus/ đã gitignore = dead code, rác thật là file TRACKED như kb/fleet_status.md). F3 cách ly KHÔNG cưỡng chế được với provider claude (chỉ cd + prompt). F7 235MB/job không dọn, tạo TRƯỚC 3 guard abort dispatch = rác mồ côi. 0 caller --write-scope. CHƯA PUSH GitHub, giữ nguyên local trong worktree, chờ quyết định: tiếp tục vá theo required_changes hay đơn giản hoá kiến trúc (tái dùng worktree theo agent/thread có sẵn thay vì per-job).
