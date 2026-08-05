# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-04 (dọn cuối ngày, sau daily retro bước 3/3)

## Trạng thái cuối ngày 08-04
- Daily retro 08-04 XONG: 2 sự cố (cả 2 đã ghi file trước khi retro chạy) + 1 mục theo dõi
  liên-ngày (dt5g-live-writer-la), 1 pattern MỚI quan trọng (Pattern 1: sửa monitoring để dập
  false-positive có thể tự tạo ra đúng loại lỗi-im-lặng nó được xây để chặn — case
  paper_main_early_check.sh 08-03 khiến netting production giết evidence account `main` 8 ngày
  liên tiếp không ai biết). Wags verify GAPS FOUND → đã sửa (số liệu bus sweep sai: finding-
  topic 81→32 thật; job Taylor_20260804_094514 thực ra đã DONE + selfcheck 6/6 PASS, không phải
  "chưa xác nhận" như draft). Entry: kb/incidents/retro/retro-2026-08-04.md.
- Wakeup compliance ĐÓNG (về 0%, 19/19 lượt --bg đúng, chuỗi 33.3→9.5→18.2→0.0%).

## Việc treo sang 08-05 (ưu tiên)
1. **`dt5g-live-writer-la`**: writer lạ (`OTHER`) ghi vnindex_5state_dt5g_live ~16:21-16:26 ICT,
   2/2 ngày liên tiếp, không khớp cron nào trên host — cần dispatch Winston xác định danh tính.
   Nếu tái xuất lần 3 mai mà chưa ai điều tra → cân nhắc escalate.
2. **Paper-main netting fix** (job Taylor_20260804_094514): code DONE + selfcheck PASS, còn chờ
   xác nhận LIVE end-to-end ngày mai (basket sau netting còn ≥1 lệnh thật) để đóng hẳn.
3. **Mafee live-lever-order test** (`test-lenh-that-goi-1840-BI-CHAN-chua-ket-luan`): vẫn
   CHUA_KET_LUAN, cần user cấp quyền chạy Bash đặt lệnh thật ở phiên interactive.
4. **Pattern 1**: cân nhắc thêm mục mới vào kb/coding_guidelines.md nếu tái diễn lần nữa ở agent
   khác (checklist "đã kiểm tra hành vi mới trên MỌI đối tượng monitor chưa" khi sửa false-positive).
5. `retro-pattern-recurring-silent-cron-spof-2` — cần xác nhận số chu kỳ cron_health_check sạch
   liên tục đã đủ 3-5 ngày chưa.

## Kế thừa lâu hơn (theo dõi định kỳ, không cần hành động ngay)
- funding_required residual risk; PNJ TTL anomaly_flags (~08-23 review);
  coding_guidelines.md ~40KB gần ngưỡng; bin/crontab_add_line.sh wrapper (khuyến nghị chưa làm).

- [2026-08-04T09:34:02Z] PENDING DECISION user: 2 câu hỏi từ Taylor (bus question
  vol-scale-chase-cap-gate4-can-user-quyet-huong) — (1) netting production đang giết evidence
  paper của vol_scale_chase_cap + fill_timing (đã có fix job trên, chờ verify); (2)
  vol_scale_chase_cap gate 4 (real-fill vs proxy) không thể đóng bằng paper — 3 lựa chọn
  A(re-scope+đóng)/B(live pilot nhỏ ZaloPay)/C(park). Chưa quyết, production không đổi.

- [2026-08-05T01:24:27Z] 2026-08-04: Chuỗi 4 việc deterministic-plan-decisions (A1-A4, audit Taylor_20260804_125048) ĐÃ XONG hết + LIVE production. A1 funding gate (bb8583c), A2 TV1 cash-race + A3 CAPIT topup-warn (mike 9dc4c53a), A4 LAG governance IVS/TMG exclude (WorkingClaude c8edc92). Cả 4 quant-skeptic CONFIRMED. Policy A2: V2.4 ưu tiên mặc định, TV1 nhường (user chốt 08-04). Bonus fix: verify_finding.sh log-collision + max-turns 30→50 (d206034f).
