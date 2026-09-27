# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (2026-09-28 00:2x ICT) — ĐÃ THỰC THI XONG 6 VIỆC USER DUYỆT 23:51 27/09
- Việc 1 ✅ WC main: merge fail-closed forensic_flags (`custom_basket`), + vá 2 lỗi của chính selfcheck (neo `HEAD` ⇒ FAIL vĩnh viễn sau merge; T1 FAIL giả từ canonical). canonical 22 assertion / worktree 24.
- Việc 2 ✅ `git add -f data/forensic_flags.csv` (commit 2cc1771d, md5 8dd24db0, 11 dòng cờ + header). Quyền đĩa vẫn 600. User TỰ chịu đánh giá rủi ro pháp lý — KHÔNG chờ Wendy.
- Việc 3 ✅ (3 site ƯU TIÊN, merge 18d4a562): `rating_8l.py` forensic fail-CLOSED (opt-out `RATING8L_FORENSIC_FLAGS=""`); `pt_v23_audit_2014.py:41` giữ WORKDIR canonical + CẢNH BÁO to khi cây lệch (+`PT_WORKDIR`); `:1082` cổng LAG fail-closed khi `LAG_FORENSIC_GATE=1`. Selfcheck mới `failopen_failclosed_selfcheck.py` 32 assertion × 4 TZ, 2 chiều (OLD_REF=74dfd6ee^). failc_sweep8 45/0.
- Việc 4 ✅ mike master merge 95547a9a (park R2→R3) SAU khi vá 2 điều kiện: selftest không còn crash trong worktree (gốc suy từ vị trí file) 15/15 mutation; rc≠0 của CẢ chuỗi park giờ TỚI NGƯỜI (Discord `trading_daily` + bus error, giữ rc thật, câu riêng cho rc=7 và cho "thiếu artifact L1"). Selfcheck mới `park_chain_alert_selfcheck.sh` 20/20 (trên master 18/20 FAIL). compute_park_trim 114/0.
- Việc 5 ✅ WC c719d730: văn xuôi `trading_rules.json` đồng bộ về 0.30 (9 chuỗi: `_principle`, `status`, `risk_dial_override.*`, `pending_engine_consistency`) + thêm `default_change_history["2026-09-27_v2.4"]`. **KHÔNG đổi 1 giá trị SỐ nào** (kiểm bằng code: 60 số giống hệt trước/sau). Backup /tmp/trading_rules.bak_20260927_2359.json.
- Việc 6 ✅ không hành động (FAIL-D chỉ báo số −0,02pp, registry đã có mục ở dòng ~7454, KHÔNG re-pin).
- KB mới (mike 4f34b139): case pháp lý ⇒ có BCTC thì phân tích BÌNH THƯỜNG, chỉ WARNING tình trạng pháp lý; KHÔNG nới BANNED/excluded_tickers/forensic_flags; §21 không đổi.

## Còn mở (cần user quyết / chưa làm)
- Fail-open CÒN LẠI ngoài 3 site ưu tiên: ứng viên `trading_bot/plan.py:1651` + `:1756` (`except Exception: pass`) và `trading_bot/due_diligence.py:100`. **plan.py = logic đặt lệnh ⇒ RANH GIỚI CỨNG, không tự sửa** — cần user ký từng site. Kiểm kê đầy đủ "12 call-site" phải quét lại có phương pháp, không đoán.
- `rating8l_icb_pit_selfcheck.py` FAIL bằng `MergeError` dtype `<M8[s]` vs `<M8[us]` — TIỀN TỒN (canonical không có bản vá FAIL y hệt), chưa ai sửa.

## Việc theo lịch
- T2 28/09 19:30 PARK_TRIM + 19:40 jit_unpark: **giờ ĐÃ có cảnh báo Discord khi rc≠0** (vào topic Trading Daily) ⇒ không cần đọc log mù nữa, nhưng sáng T3 vẫn nên soát `logs/park_trim_daily.log` + `logs/jit_unpark_daily.log` lần đầu để xác nhận đường cảnh báo chạy thật lần đầu trên production.
- Xoá cron FiinPro sau 28/09. Đóng AlphaLens 30/09 + ghi registry "PASS on N=1, không đủ bằng chứng sizing".
- Review quý: measurement-integrity audit ~2026-12-27; Bobby structural-risk ~2026-11-26.

## Bẫy đã ghi lại (đừng cắn lần 3)
- Selfcheck neo bản cũ bằng `HEAD`/`main` ⇒ sau merge FAIL vĩnh viễn. Luôn neo `<commit-vá>^` + env override.
- Selfcheck hardcode gốc canonical ⇒ chạy từ worktree test MASTER. Gốc mặc định phải suy từ `__file__`.
- `discord_id_gate` chặn ID Discord trần trong code — dùng TÊN (`trading_daily`) trong `kb/discord_channels.json`.

