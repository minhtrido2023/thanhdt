# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái cuối ngày 26/11 (retro: kb/incidents/retro/retro-2026-11-26.md, 8 sự cố)

### GẤP sáng 27/11
- [2026-11-26T17:38:45Z] [27/11 00:45] topic 1575558136297689179: user đổi rổ CAPIT VGC->PVT (QNS giữ; SIP trượt FSCORE 4). Diff chờ user 'bắt đầu': agents/Mike/capit_swap_20261127/ (python3 swap.py 7.52724E10 --apply, rồi dry.py cần proposed lại; gửi lại plan report --plan-date 2026-11-27; kiểm golive_v23_status còn PVT trước 09:05). Plan chưa duyệt.
- data/dd_zone_candidates_latest.json (WC root) còn là FIXTURE (selfcheck dd_price_zone_watch đè 26/11 19:54) → bản 08:00 sai tới cron 19:45; mỗi lần chạy selfcheck đó lại đè. CHƯA sửa.
- VPB ZaloPay: plan-position-drift 20:50 = DRIFT (2 hệ giá 19.700/20.250, KL 930), SpaceX CANNOT_CHECK — kiểm trước 09:05.
- Claude CLI hết hạn đăng nhập khoảng 03–06/12: nhắc user `claude auth login` / `setup-token`.

### Chờ user
- POW: skeptic r4 REFUTED (hồi tố 2.454,7 đếm 2 lần, tâm ≈8.549) — chờ duyệt rev5-sửa + center_adj E17 + sổ + báo cáo. Bản NĐT 26/11 KHÔNG gửi; DD chỉ email khi user báo. Topic 1575064839301365845.
- auto-resume phiên Discord LIVE; ca thread ARCHIVED chờ user Close topic test 1575408554289143828. Lần hết quota thật đầu: logs/session_limit_resume.log + resume_pending.log.
- Nâng mốc config/trading_calendar_confirmed.json (hiện 2026-12-04); sửa file này phải chạy lại selfcheck đọc nó.

### Còn mở
- Selfcheck ĐỎ: dt5g_publisher_gate_selfcheck.sh, dd_ledger_append_center_adj_selfcheck.py, freshness_ops_selfcheck.py (thiếu prune_depth_gate.py trong sandbox).
- Báo giả: send_plan_report so md5 ("PLAN ĐÃ THAY ĐỔI"), kb_ingest_lag, watchdog.sh:119 mỗi 10'. Escalation chờ user: retro-pattern-recurring-guard-judges-by-proxy-not-artifact.
- Repo mike: 130 file staged chưa commit (gồm code đang chạy production) — chủ chưa rõ; commit phải kèm pathspec.
- [11c] macro_healthcheck báo base STALE (20/25/26-11) chưa điều tra; vn_interbank_3m cũ.
- plan-gate P3 đã ĐÓNG (3973d192a): theo dõi logs/plan_gate_recovery.log. send_plan_report sau 00:00 PHẢI kèm --plan-date.
- pit2 ĐÓNG: 01/12 08:23 lượt thật đầu → logs/paper_cell_monthly_pit2.log (giữ worktree wt-dcf-lvens2-pit2-20261126).
- DCF-VN hành vi: topic 1575099485153927261 (Taylor_20261125_104308) — theo dõi ở topic đó.
- DD chờ: NT2 (BCTC 2026), TCH/DRI/VGS (dữ kiện), PVP (NQ/BB sau ĐHĐCĐ 30/11).
- Tồn: prevention retro 22/11, grep ngưỡng cứng 200, backup 24/11 lỡ chu kỳ.
- Giữ nguyên: DRI bán hết/TV1 không giữ; 4 quy tắc 02/11 (kb/projects/dd-flag-rules-20261102.md); park 0%.

- [2026-11-26T17:54:01Z] [27/11 00:55] VGC->PVT ĐÃ ÁP + gửi lại báo cáo plan 27/11 (chưa duyệt). Blacklist cờ bất thường chuyển topic 1575570310676217860 (đã wake). Còn ở topic 1575558136297689179: cron 08:30 kiểm golive_v23_status còn PVT; mirror duyệt plan vào topic 1521183164364754974; hạn 19:00 27/11 golive có thể đưa VGC trở lại (topic mới xử).
- [2026-11-26T18:03:12Z] [27/11 01:05] topic 1575570310676217860 (cờ CAPIT): đã đo + trình phương án A (gỡ cờ có user duyệt) + B (rút cờ giả VPB), diff agents/Mike/capit_flag_blacklist_20261127/ — CHỜ user 'bắt đầu'; HẠN 19:00 27/11 (golive loại PVT => VGC quay lại; cờ PVT hết TTL từ asof 30/11).
