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

- [2026-10-25T03:36:34Z] 25/10 10:50 rà bus: đã đóng selfcheck-red production_manifest (T0 egg_transfer_alert, 8519f33de). Chờ user: ack MCH/MSR hash mới bị classifier chặn (cần user xác nhận), auto-exit-inject approval, wakeup-gate A, hard-boundary cq-10-18/10-25, coord-10-19/20 (injector TV1 clamp), dt5g writer 15:25 T7 chưa rõ nguồn, phs_flash_api selfcheck=connect timeout flashapi.phs.vn
- [2026-10-25T04:31:47Z] 25/10 11:35 bus pending=0. Đã: merge auto-exit-inject (0a137b3d5), wakeup prevention (8367200c6), cpi_vn PIT (WC 2cafe5c53+c681cb7be, registry), hard-boundary 4 commit. TV1 injector band = FALSE alarm (UPCOM 15%). CÒN: gap relay retro→user (retro_escalate.py không đẩy options+recommendation tới user) chờ user chọn kênh; plan T2 chưa có MCH (cần dựng lại+duyệt trước 08:45); Wags đề xuất dt5g_publish_runs.log chờ user; 5 nợ prevention (c)(d)(e) còn.
- [2026-10-25T04:37:54Z] 25/10 11:45 user duyệt: relay retro→Trading Daily (Wags_20261025_043745), log publish tay dt5g + fix prompt DollarBill đọc ack sizing LAG_LO 8% (Taylor_20261025_043744, HẠN merge trước 18:30). Vòng plan CN 19:00 SẼ dựng lại plan T2 (gồm MCH) và gỡ dấu duyệt → sau ~20:45 kiểm plan: SCL/MCH phải 8%, báo user duyệt lại. Không dựng plan tay riêng vì 19:00 sẽ ghi đè.
- [2026-10-25T05:29:31Z] 25/10 TV1: Winston vugia_cascade xác nhận A Vương+SB4/SB4A THƯỢNG nguồn SB5 (QĐ 1865/2019 Đ24.2: SB5 xả theo kế hoạch A Vương/SB4); SB5 hữu ích 2,45 tr m³. Chỉ báo Q4: bản tin Công Thương 'mực nước hồ thủy điện' (A Vương, SB4 lưu lượng về hồ) + KTTV dự báo lũ. Chờ user duyệt PREREG chu kỳ hàng hoá (MSR): bản đồ mã-hàng hoá + thử nghiệm pha đầu.
- [2026-10-25T06:12:49Z] 25/10 13:15 user duyệt: Winston_20261025_061238 gom bản tin Công Thương AVC/SB4 (backfill từ 01/10, CHỈ đề xuất tự động hoá, chưa cron); Taylor_20261025_061240 PREREG chu kỳ hàng hoá DRI/MSR/PVT (opus medium). Xong Taylor → quant-skeptic phản biện rồi báo user.
- [2026-10-25T06:15:04Z] 25/10 13:20 Winston avc_bulletin: bản tin Công Thương ĐÃ NGỪNG sau 07/12/2023, phủ 0/25 ngày 10/2026. Chờ user chọn nguồn thay (EVNGENCO2/Cục KTAT, thông báo xả lũ Quảng Nam, hydro.gov.vn). Taylor PREREG còn chạy.
- [2026-10-25T06:21:31Z] 25/10 13:25 Taylor commodity-cycle PREREG xong: FAIL 6/6 no edge (underpowered); MSR không bắt được vì thiếu chuỗi vonfram APT (fleet không có); post-hoc 1,05/3M +12pp chỉ là giả thuyết. Chờ user: giao Winston dựng feed APT vonfram + BDTI/BDI ngày; PREREG-2 paper từ 11/2026; chọn nguồn thay bản tin A Vương.
- [2026-10-25T06:28:33Z] 25/10 13:30 user duyệt việc 1+2: Winston_20261025_062823 feed vonfram APT+BDTI/BDI (đề xuất cron, chưa cài); Taylor_20261025_062825 PREREG-2 ô 1,05/3M + paper program trên nhánh riêng (KHÔNG merge, Mike review→user). Còn chờ user: nguồn thay bản tin A Vương.
