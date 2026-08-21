# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Wake-up simplification (2026-08-21) — ĐÃ TRIỂN KHAI, còn 1 việc: restart ccdb
Kiến trúc mới "kết quả là DỮ LIỆU, không phải lượt đánh thức" (user duyệt). Gỡ push-wake +
reconciler cron */5 + debounce. Đã commit:
- Fleet: 541b50f3 (dispatch.sh/verify_finding.sh gỡ push-wake; git rm wakeup_reconcile.py +
  2 selfcheck; wake_thread.sh giữ primitive TAY; MIKE.md §8 135→52 dòng; cron_registry; daily_retro 2d).
- ccdb (repo /workspace/claude-code-discord-bridge): 6a709e7 — choke-point chung retry session
  mới khi "No conversation found". 2109 test pass (+2 mới). CHƯA RESTART.
- Doc: 40bd95b0 wakeup_simplification_proposal_20260821.md.

## CÒN LẠI (1 việc, không gấp)
- **Restart ccdb-mike.service** để kích hoạt fix 6a709e7 — HOÃN sau 15:05 ICT (ngoài giờ giao dịch;
  restart ngắt mọi session Discord vài giây). Lệnh: systemctl --user restart ccdb-mike (service ở
  máy sgms, WorkingDirectory=/workspace/ccdb-mike). Cần user trigger hoặc cho phép.
- **Unblock NGAY Trading Daily** (trước restart): user gõ /backend claude ở thread 1521470705563340910
  → xoá session codex kẹt (01a01157…). 4 thread khác cũng kẹt session codex (1518839846, 1532076080,
  1535116481, 1538708408) — restart ccdb sửa hết 1 lần.

## Known-red pre-existing (KHÔNG do thay đổi này, cần triage riêng)
- wake_thread_selfcheck.py ca "3 no explicit suffix" (known_red từ 08-20).
- daily_retro_wake_metrics_selfcheck.sh: _batch_unknown unbound (extract block lỗi thời sau batch-id revert).

## Bối cảnh còn hiệu lực (giữ)
- GDKHQ D1-D3 LIVE 08-17. TV1 Rule A LIVE 08-15. CASH_VENDOR gate ĐÓNG.
- BAL signal shadow-track (VPI) review 09-16. signal_holds BAL+VPI until 09-16.
- OKF split mandate: file >40KB tự split.

