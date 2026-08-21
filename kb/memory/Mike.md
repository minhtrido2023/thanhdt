# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái sau 2026-08-21 12:39 ICT — KHÔNG CÒN VIỆC TREO

### Wake-up simplification — HOÀN TẤT 100%
- Fleet commit 541b50f3: gỡ push-wake/reconciler/debounce, MIKE.md §8 rút gọn.
- ccdb commit 6a709e7: retry session mới khi "No conversation found" — ĐANG CHẠY (restart 12:39 ICT, health ok).
- Doc: 40bd95b0 wakeup_simplification_proposal_20260821.md.

## Known-red còn lại (KHÔNG do thay đổi này — triage riêng khi cần)
- lag_live_schedule_selfcheck.py B6 (LAG domain — Taylor triage nếu cần).
- phs_flash_api_selfcheck.py: chờ PHS production credentials (ngoài tầm).
- daily_retro_wake_metrics_selfcheck.sh: _batch_unknown unbound (batch-id revert residual).

## Bối cảnh còn hiệu lực
- GDKHQ D1-D3 LIVE 08-17. TV1 Rule A LIVE 08-15. CASH_VENDOR gate ĐÓNG.
- BAL signal shadow-track (VPI) review 09-16. signal_holds BAL+VPI until 09-16.
- OKF split mandate: file >40KB tự split.

- [2026-08-21T11:11:45Z] 2026-08-21 18:20 ICT: PLAN discord stamp/format by-construction (agents/Mike/research/discord_outbound_format_by_construction_plan_20260821.md) — chờ user chốt 3 điểm §7 rồi mới implement (ccdb outbound_format.py ở event_processor RESULT + /api/notify; gỡ prose). CHƯA sửa code.
- [2026-08-21T12:25:45Z] 2026-08-21 19:4x ICT: Discord timestamp by-construction lớp 2 (thân tin): ccdb 4e6f2cb (_normalize_times UTC→ICT, ~Ns→phút, embed) + fleet 34037199 (dispatch.sh ETA ICT+phút, utc_text_gate.sh pre-commit). ĐANG restart ccdb-mike; SAU restart: verify E2E bằng notify_thread tin thử '12:14 UTC (~435s)' rồi đọc lại qua /api/threads/<tid>/messages; lounge closing note.
- [2026-08-21T12:26:39Z] 2026-08-21 19:27 ICT: XONG Discord timestamp by-construction (ccdb 56e3b29+4e6f2cb, fleet cb346fa4+34037199). E2E verified sau restart. Không còn việc treo về chủ đề này.
- [2026-08-21T16:27:34Z] 2026-08-21 23:4x ICT: Lỗi giờ LẦN 3 (loại C: LLM suy luận sai, nhãn ICT đúng). RCA: [now:] injection KHÔNG chạy cho tin text-only (prompt_builder early-return), host/ccdb TZ=UTC, lịch sử Discord bơm UTC không nhãn. PLAN S1-S4 ở agents/Mike/research/discord_time_reasoning_by_construction_plan_20260821.md — CHỜ user duyệt rồi dispatch Wags (S2/S3/S4) + Taylor (S1 audit). Fable plan-only, không tự implement.
