# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái cuối ngày 2026-10-02
- Retro 2026-10-02 đã chạy đủ 3 bước (draft → Wags verify GAPS FOUND → finalize đã sửa gap),
  entry `kb/incidents/retro/retro-2026-10-02.md` + index.md, commit `8d44565e`.
- Pattern 1 (corp_action_daily feed_dead, 6 ngày đứng) TÁI ESCALATE — topic đã có sẵn
  `retro-pattern-recurring-corp-action-feed-vendor-dead-cascade`, KHÔNG mở question mới. Đề xuất
  B (chuyển sang broker-làm-nguồn-xác-định, tự động hoá) đang chờ user/Mike quyết.
- Sự cố mới cần theo dõi: #3 `compute_active_nav.py` không tự đọc `corp_actions.json` (chưa giao
  ai gỡ khoá); #5 `check_sbv_weekly.sh` nhiễm trace_id xuyên-agent (nguyên nhân 2 tầng chưa rõ,
  đề xuất Winston/Wags điều tra thêm — chưa dispatch).
- Pattern 2 (chi phí review đa vòng) — prevention `dispatch-routing` skill mới ship cùng ngày
  10-02; retro 10-03 cần kiểm xem số vòng polish có giảm không.

## Từ phiên trước (2026-10-01), còn mở
- Taylor job 041603 kill-switch A vòng 4 (CCTG silent-drop/range guard) — trạng thái CHƯA xác
  nhận lại trong phiên này, cần kiểm lúc mở phiên kế tiếp.
- Rủi ro Trứng vàng vượt trần đề xuất legal-vn (sleeve ≤10% NAV) — chưa user chốt.
- verify_account_snapshot nghi không bắt lệnh bán SCL tay — báo cáo tháng 09 SpaceX cần kiểm lại.

## Chờ user
- Định nghĩa "xu hướng hạ" lãi suất (trigger park quay lại).
- rating_8l/DCF dùng effective rate (bảng diff registry cctg_rate_vn.md).
- Discretionary DRI/TV1.
- Phương án A/B/C cho corp_action_daily feed dead (xem Pattern 1 trên).

## Backlog
- 9 topic selfcheck-red cần triage.
- VNM exright note cho Winston.

