# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike (dọn cuối ngày 24/10)
## Chờ USER
- Bus `retro-pattern-recurring-wakeup-gate-not-mechanical` (đề xuất A: Taylor làm (a)+(b); đã escalate lại 24/10). Trả lời xong đóng cả `...-owned-recovery-path` (18/10) + `...-recovery-path-recurring` (19/10).
- Lãi CCTG A/B (6,8% vs 5,9%; mặc định giữ 6,80/7,40).
- Rights alert NB mở: auto_exit_inject.py:343 '>'→'>='; send_plan_report.sh:1007-1015; reconcile_equity chân tiền credit≠payment; N4 chưa wire dividend_adjusted_return.
- Livermore-cổ-phiếu NO-GO sát biên: thử tiếp = PREREG mới, chờ user.
## T2 26/10 (quan trọng nhất)
- Plan T2 (SpaceX HT1 2700/SCL 1100/VPB 1500; ZaloPay HT1 1600/SCL 700/VPB 900) chờ user DUYỆT trước 08:45; Trứng vàng = tiền: chuyển egg ≥107,1tr SpaceX / ≥65,3tr ZaloPay (xem logs/egg_transfer_alert.log). Gate 09:05 chặn cả plan nếu quên chuyển.
- SCL sửa tay LAG_HI 10%→LAG_LO 8% (backup state/plan_redo_20261024). RỦI RO: sunday_plan_round CN 25/10 19:00 có thể dựng lại SCL 10% — KIỂM (lần chạy đầu + selfcheck của nó >7' cần điều tra).
- MCH/MSR ack ACK_STALE: chạy lại lag_dd_pack, ghi lại ack MCH (PROCEED LAG_LO 8%) + MSR DROP cùng source. SCL vào ~26/10 (hủy nếu VinCons chậm trả); user tự mua quyền, báo Mike số CP.
- VPB LAG ZaloPay: lệnh bán cap 282→0cp (sellable 0) — xem lại. HT1 FUNDING_ALERT DEFER.
## Theo dõi / nợ
- Sáng 25/10: kiểm notify_thread_errors.log không còn msg=Retro (verify fix #1).
- ĐIỀU TRA: dt5g-live-writer-late (vnindex_5state_dt5g_live bị ghi 15:08/15:17 ICT ngoài cửa sổ, writer_class=OTHER).
- PREVENTION CHƯA LÀM: (a) nav_scripts_2account_selfcheck.py backup tên duy nhất/flock; (b) dispatch.sh --bg cảnh báo 'CHƯA đặt ScheduleWakeup'; (c) cổng NAV ngoài cửa sổ EOD; (d) cổng plan-vs-WorkingClaude/data/lag_dd/ack.json; (e) quét script khác in cảnh báo ra stdout (như cpi_vn).
- context_pack ~45KB sát trần: cần trim; known_red deposit_fallback dọn; coord-10-19: injector TV1 chưa kẹp biên độ ngày.
- FPT Q3 BCTC ~28/10; DRI/TV1 ~30/10 (DRI LNST<22 tỷ→bán 50%). 2 question Wags treo coord-2026-10-19/20.
## Mốc
- nav-loss-brake 11-09; DT CRISIS commit sớm ~11/10; Livermore chấm ~19/11; review BĐS 11-26; LAG checkpoint 12-15; measurement audit ~12-27. Architecture digest 18:00 ICT.

