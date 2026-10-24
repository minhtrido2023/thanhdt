# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike (dọn cuối ngày 23/10)
## Chờ USER
- Bus `retro-pattern-recurring-wakeup-gate-not-mechanical` (đề xuất A: Taylor làm (a)+(b)). Trả lời xong đóng cả 2 câu cũ `...-owned-recovery-path` (18/10) + `...-recovery-path-recurring` (19/10).
- Lãi CCTG A/B (6,8% vs 5,9%; mặc định giữ 6,80/7,40).
- Rights alert NB mở: auto_exit_inject.py:343 '>'→'>='; send_plan_report.sh:1007-1015; reconcile_equity chân tiền credit≠payment; N4 chưa wire dividend_adjusted_return.
- Livermore-cổ-phiếu NO-GO sát biên: thử tiếp = PREREG mới, chờ user. Chỉnh tỉ lệ Livermore khóa tới >=12 lần chấm.
## Việc theo dõi
- PREVENTION CHƯA LÀM: (a) nav_scripts_2account_selfcheck.py backup tên duy nhất/flock; (b) dispatch.sh --bg cảnh báo 'CHƯA đặt ScheduleWakeup'; (c) cổng dòng NAV ngoài cửa sổ EOD.
- VPB LAG ZaloPay: lệnh bán cap 282→0cp (sellable 0) — xem lại plan 26/10.
- LAG: SCL vào ~26/10 ở LAG_LO 8% (hủy nếu VinCons chậm trả); user tự mua quyền, báo Mike số CP từng account. Đọc TAY plan 26/10 (HT1 FUNDING_ALERT DEFER).
- Livermore cron 19:45 ICT T2-T6 (logs/livermore_trigger.log); DT CRISIS candidate ~11/25, commit sớm nhất ~10/11; baseline 21/10 chấm ~19/11.
- Architecture digest 18:00 ICT (logs/arch_digest.log), chưa re-review vòng 2.
- FPT Q3 BCTC ~28/10; DRI/TV1 BCTC Q3 ~30/10 (DRI LNST<22 tỷ→bán 50%; TV1 chỉ báo AVC/SB4). tav2_bq.ticker đủ ~1294 mã? 2 question Wags treo coord-2026-10-19/20.
- Dọn .bak_pre_rm_bogus_20261022 nếu tìm thấy (23/10 không thấy).
## Mốc
- nav-loss-brake 11-09; review BĐS 11-26; LAG checkpoint 12-15; measurement audit ~12-27. AlphaLens ĐÓNG; ORB paused; expvol ckpt 11-10.

- [2026-10-23T21:23:34Z] [24/10 weekly audit] Đã vá 3 bug (93cc3f91f retro topic, 6b1e3730e incidents index, 2cabd9f0e memcap). Theo dõi: 00:30 25/10 notify_thread_errors.log không còn msg=Retro; sunday_plan_round chạy lần đầu CN 25/10 + selfcheck của nó >7' cần điều tra; context_pack 44.996B sát trần 45KB cần trim; known_red deposit_fallback mục auto đã cũ cần dọn; coord-10-19 còn mở: injector TV1 chưa kẹp biên độ ngày + retro→user options.
- [2026-10-24T02:36:23Z] 24/10 user chốt: Trứng vàng = TIỀN khi lập plan (ngân sách = cash+egg). Cron egg_transfer_alert 08:30-14:30 mỗi 15' T2-T6 đã cài (merge b4bcf3693 + outer b6a6e5c26). Theo dõi: sáng T2 26/10 xem logs/egg_transfer_alert.log + DollarBill plan có còn 'thiếu tiền' không; đã biết: gate 09:05 BLOCK cả plan kể cả lệnh BÁN nếu quên chuyển.
- [2026-10-24T03:52:45Z] 24/10: MSR skeptic REFUTED LAG_HI→khuyến nghị LAG_LO 8% (chờ user ack PROCEED; cần dcf_override_reason, cổ tức đợt 2 thực 5.000đ còn ~3.000đ chưa có ngày chốt, gộp phơi nhiễm Masan MSR+MCH). Taylor_20261024_034455 nghiên cứu DCF-RICH vs triển vọng LN (agents/Taylor/research/dcf_rich_outlook_20261024) — chờ kết quả, relay user. Pack lag_dd_pack cần vá: AR/DSO chuẩn hoá, CFO 2 quý gần nhất, corporate_action thiếu phần 3.000đ.
- [2026-10-24T04:09:56Z] 24/10 11:06 USER: duyệt quant-skeptic (job quant-skeptic_20261024_040741) rồi mới đổi lag_dd_pack; MCH PROCEED LAG_LO 8% (ack ghi, hash 00474f6db9ca8acb gồm ANOMALY_NA — T2 nếu cờ còn DCF_RICH mình hash d3144c184595f6b0 ⇒ ack_stale, ghi lại ack với cùng source); MSR DROP (ack ghi). Taylor_20261024_040927 = nghiên cứu run-up trước công bố vs drift LAG (lag_runup_effect_20261024). Sau skeptic CONFIRMED: vá lag_dd_pack (DCF_RICH chỉ chặn khi sâu & (ROE<25% | hàng hóa)), AR/DSO chuẩn hóa, CFO 2 quý, corporate_action 3.000đ MSR(đã DROP), rating_8l COMMODITY_MAP MSR.
