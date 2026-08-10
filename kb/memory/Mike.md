# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-09 (cuối ngày, sau daily retro bước 3/3)

## Daily retro 08-09 — XONG
7 sự cố, 4 pattern. Wags verify GAPS FOUND → đã sửa (commit gán sai row #3 aa0afea→319e1b2; row #4
đã chốt fail-closed cùng ngày, không còn "treo"; bổ sung 2 sự cố bị bỏ sót #6/#7 từ finding
DollarBill). File: `kb/incidents/retro/retro-2026-08-09.md`, commit `a7863c1c`.

**Pattern 1 (CAO) — `availableCash` dùng nhầm làm "tiền mặt thật"**: 2 lần độc lập cùng ngày
(`compute_active_nav.py` — Winston, CHƯA VÁ; pool L1 park-trim — Taylor, đã vá commit `df7d92b4`).
Đề xuất Prevention: hàm chung `get_true_cash()` trong `brokers.py` + audit grep toàn repo.

**Pattern 2 (CAO NHẤT) — Mike tự dispatch trùng lặp cùng file, 3 lần (07-08→2 lần hôm nay)**. Lần
gần nhất do tin `jobs.sh status=failed` giả (watchdog timeout ≠ process chết), chạm `executor.py`.
Đề xuất kỹ thuật của Taylor: `dispatch.sh`/watchdog kiểm `kill -0 <pid>` trước khi đánh dấu failed.
CHƯA tự sửa (đây là draft-only), cần quyết hành động thật sớm, không chờ thêm 1 retro.

**Pattern 3 — ESCALATED**: backlog "chưa ghi file kb/incidents/" 2 retro liên tiếp không giảm
(9→16 sự cố tồn đọng). Bus question `retro-pattern-recurring-2-days` đã gửi, chờ user/Mike chọn
hướng Prevention (stub tự động vs chấp nhận retro-là-đủ).

## Việc treo sang 08-10 (ưu tiên, KHẨN)
1. **KHẨN NHẤT**: bus question `spacex-plan-0810-thieu-216524d-sau-khi-go-L1` (Taylor, 16:55:59Z
   08-09) CHƯA có answer — deadline "trước 09:05 ICT" đã/sắp qua (hôm nay 2026-08-10). Xử lý TRƯỚC
   TIÊN khi vào phiên tiếp theo.
2. Sự cố #1 `compute_active_nav.py` availableCash bug — verify lại trạng thái thật trước khi dùng
   `active_nav` cho báo cáo/sizing (đừng tin memory, có thể đã đổi).
3. ZaloPay park-trim display-only (câu hỏi `Q2-zalopay-park-trim` của DollarBill) + plan ZaloPay
   08-07 0 fill — cả 2 chưa ai điều tra, cần dispatch Mafee/Winston.
4. Pattern 2 (dispatch collision) — cân nhắc áp fix `kill -0` cho `dispatch.sh`/watchdog sớm.
5. 16 sự cố tồn đọng (9 từ 08-07 + 7 hôm nay) cần file `kb/incidents/` riêng, ưu tiên #2b/#3 (chạm
   executor.py/tiền thật).
6. `selfcheck_weekly_baseline_check.sh` — run-id chống ghi đè + guard interpreter sai (nhỏ, không khẩn).
7. `plan_state_source_mismatch` (`send_plan_report.sh` ~168-176) — chưa sửa.

## Kế thừa lâu hơn (theo dõi định kỳ, không cần hành động ngay)
- Verify độc lập fix VHM (NAV-report + LotBook corp-action) — vẫn chưa có ai verify ngoài Taylor.
- lag-sizing-basis-lech-2-account (SpaceX %active_nav sai mẫu số) — cần xác nhận.
- Paper-main netting fix (Taylor_20260804_094514): cần xác nhận LIVE end-to-end.
- Mafee live-lever-order test vẫn CHUA_KET_LUAN, cần user cấp quyền Bash đặt lệnh thật.
- PNJ TTL anomaly_flags (~08-23 review).
- coord-2026-08-07 saga bị arch-reviewer bounce 2 vòng, im lặng từ đó — theo dõi có lặp không.

- [2026-08-10T11:27:56Z] 2026-08-10 EOD: đề xuất nới trần LAG phiên 2/3 lên anchor×1,03 = NO-GO xét lợi nhuận (backtest NAV +0,08pp, CI chứa 0, PBO 0,775, quant-skeptic CONFIRMED cao); patch KHÔNG áp, nằm ở pending_lag_anchor_widen_20260810/. Việc còn treo, ưu tiên cao hơn: (1) sửa đường cấp vốn phiên-1/park_trim (lý do THẬT gây mất 173tr LAG 08-06, không phải trần giá) — chưa ai làm; (2) verify_finding.sh có bug JSON trailing-comma TÁI PHÁT lần 2, âm thầm hạ CONFIRMED→INCONCLUSIVE trên bus — cần sửa parser (strip trailing comma trước json.loads), chưa dispatch; (3) HARD_CEILING_BLOCK bị commit HYBRID (0f54cb7+717307f) nuốt mất trong 4 selfcheck/7 dòng — chặn paper rehearsal cho đề xuất anchor, live không bị (paper-gate) nhưng cần Taylor tự sửa fixture trước khi rehearsal bất kỳ đề xuất nào chạm paper mode.
- [2026-08-10T14:28:21Z] 2026-08-10: Token-usage review 5 việc XONG (~8h, đa số cho item #1). Kết quả: #2/#4 spend_report.py effort=high warning + fix orphaned-duration (commit 254e0e6d); #5 Taylor audit opencode = KHÔNG auto-route (chỉ 1.8% compute đủ điều kiện); #1 kill-0/liveness guard = 9 vòng arch-reviewer, mỗi vòng bug thật, dừng ở commit 9e20bbf0 theo khuyến nghị Wags (fail-closed an toàn, KHÔNG CONFIRMED tuyệt đối); #3 nudge smoke-test dispatch.sh (commit 00dced61).
- [2026-08-10T14:28:21Z] BACKLOG kiến trúc (từ Wags, chưa làm): 9/11 live job record có pin_failed=1 -> cơ chế pin-theo-inode (nguồn xác thực MẠNH cho liveness guard) không hoạt động thật trong production, buộc guard phải dựa vào tree-match (yếu, đã bị khai thác ở round 9). Đề xuất Wags: bắt buộc pin ngay lúc dispatch.sh tạo job, bỏ hẳn lớp tree-match cũ -- đây là quyết định thiết kế, không phải thêm 1 bản vá. Chưa dispatch, cần user/Mike quyết khi có thời gian.
