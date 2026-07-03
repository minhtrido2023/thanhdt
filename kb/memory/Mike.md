# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái fleet hiện tại (2026-06-30)
- **Taylor**: active (companion R&D)
- **DollarBill**: active, plan SpaceX 2026-07-01 đã tạo (state NEUTRAL)
- **Mafee**: running (paper mode cho đến go-live)
- **Winston/Spyros/Wendy**: native on-demand (daemon đã tắt 2026-06-25)

## Go-live 2026-07-01
- Cron `0 1 1 7 * golive_01jul.sh` — tự flip SpaceX/DNSE + Telegram notify lúc 08:00 ICT
- trading_rules v1.7: applies_to=live, approved_by=user, live_effective=2026-07-01 ✓
- Account SpaceX / 0002023347 / DNSE: 1B VND, enabled=false → flip ngày mai

## Research đã đóng (custom30V sweep 2026-06-30)
- Permanent Exclude × custom30V: không overlap (tất cả 7 tên nằm ngoài top-30)
- Backtest re-run excluding 7 tên: DO NOT WIRE (OOS đi ngang, IS -0.2pp)
- custom30V production giữ nguyên (30 mã, cap 0.10)
- Sector sweep 15 ngành: sector_watchlist_framework.md đã ghi (Taylor)

## Không có gì pending hiện tại
- [2026-07-01T09:28:55Z] TẠM THỜI (2026-07-01): model đổi sang claude-opus-4-8/high vì claude-sonnet-5 bị lỗi classifier 'temporarily unavailable' liên tục (chặn Edit/Bash). File: agents/Mike/.claude/settings.json. RESET lại claude-sonnet-5 vào ngày mai (2026-07-02) nếu lỗi đã hết — user yêu cầu tự reset, không cần hỏi lại.
- [2026-07-01T10:17:32Z] Đang xử lý: 2 patch executor.py (churn-guard + tick-retry + fix đếm-đôi extreme-poll) đã code + quant-skeptic CONFIRMED, CHƯA commit git (uncommitted: trading_bot/executor.py +94/-3, 3 file selfcheck mới chưa track: churn_guard_selfcheck.py, tick_retry_selfcheck.py, extreme_regime_selfcheck.py). Đang hỏi user: commit luôn hay tiếp tục patch#3 (trần đuổi mua 1.5% quá chặt — cần hỏi Taylor trước, không tự quyết) trước khi commit. Restart sang opus-4-8 theo yêu cầu user vì sonnet-5 classifier lỗi 'temporarily unavailable' lặp lại chặn Edit/Bash nhiều lần trong phiên này.
- [2026-07-01T10:32:45Z] Model Mike CHỐT mặc định lâu dài: claude-sonnet-5, effort high (2026-07-01). User đánh giá Sonnet 5 lỗi classifier ít hơn khi gọi agents, lỗi 'temporarily unavailable' là chập chờn hạ tầng Anthropic, chấp nhận sống chung. Đã thử Opus 4.8 không khác biệt rõ rệt. KHÔNG cần đổi qua lại nữa trừ khi user yêu cầu.
- [2026-07-02T15:31:56Z] ĐANG LÀM: user yêu cầu nghiên cứu thông lệ ngành mới nhất về agent management, đối chiếu hệ thống fleet hiện tại → giải pháp chống lỗi kinh niên. Deep-research workflow đang chạy nền (run wf_e0817a45-805). Đã kiểm kê xong incident nội bộ (KNOWLEDGE.md §8 + git log 06/2026 + memory day-1 bugs). Khi workflow xong: tổng hợp gap analysis + đề xuất.
- [2026-07-03T00:43:38Z] XONG: nghiên cứu agent-ops + đối chiếu fleet (2026-07-02/03). Đã vá: (1) coding_guidelines §5 idempotent side-effects, (2) trace_id fix — dispatch.sh/verify_finding.sh/6×CLAUDE.md/mike_json.py/bin/trace.sh (verify bằng dispatch thật, tested), (3) bin/staleness_watch.py + watchdog.sh watch-the-watcher cho macro_health.json (root cause DT5G-stuck-11-ngày). Commit c4216ca + 769354e. Còn treo: P2 (phân loại độ tin cậy bus event theo mức) — chưa làm, không tự mở rộng thêm trừ khi user yêu cầu.
- [2026-07-03T01:23:13Z] XONG toàn bộ P0/P1/P2 nghiên cứu agent-ops (2026-07-02/03): (1) coding_guidelines §5, (2) trace_id fix + bin/trace.sh, (3) staleness_watch.py watch-the-watcher, (4) verdict-prominent rendering + verification_audit.sh coverage report. Commit: c4216ca, 769354e, af5cb75, 98bb1c7. Tất cả đã test bằng dữ liệu thật/giả lập trước khi commit, đã đăng ký vào MIKE.md §Công cụ. Không còn việc treo từ nghiên cứu này.
