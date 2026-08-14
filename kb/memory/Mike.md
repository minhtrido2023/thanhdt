# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-13 (cuối ngày, sau daily retro bước 3/3)

## Daily retro 08-13 — XONG
4 sự cố, 2 pattern. Wags verify GAPS FOUND → đã sửa (draft gốc grep sai đường dẫn
dnse_raw_2026-08-13.jsonl, kết luận sai "TV1 0cp cả ngày" — thực tế SpaceX 1.100/1.800cp,
ZaloPay 600/1.200cp đã khớp sau khi bot tự phục hồi từ sự cố DNS-block 09:21 ICT). File:
`kb/incidents/retro/retro-2026-08-13.md`, commit `d299d5ac`.

**Pattern-B (ngày thứ 4 liên tiếp, 08-10→08-13)** — hệ thống tin BIỂU DIỄN của sự thật thay vì
xác nhận sự thật. Hôm nay 3 hình dạng: (1) `append_event.sh` word-split nuốt payload có dấu `'`
— ĐÃ VÁ HOÀN CHỈNH commit `94b01dbb`; (2) checker tin "bus không có `answer`" = "chưa quyết" dù
quyết định đã hành động qua code+injector (ceiling TV1 20.497); (3) chính draft retro hôm nay
grep sai đường dẫn → Wags bắt lại. Prevention đề xuất (coding_guidelines: chuẩn hoá giá trị
trước khi so 2 nguồn) VẪN CHƯA được user duyệt — câu hỏi
`retro-pattern-recurring-patternB-checker-wrong-representation` mở 08-12, nay Day 2 chưa đóng.

**Pattern backlog (KHÔNG MỚI, treo sang NGÀY THỨ 5, mở 08-09)** — `Mike/retro-pattern-recurring-2-days`
chưa có `answer`/`decision` 5 ngày liên tục dù đã triage GENUINE từ 08-10.

**Escalation mới sẽ post lên bus ngay sau bước này** — cả 2 pattern trên, mức nghiêm trọng tăng
(2+ retro liên tiếp không ai đóng).

## Việc treo sang 08-14 (ưu tiên)
1. User cần quyết 3 việc: (a) prevention Pattern-B (coding_guidelines mới), (b) hướng xử lý
   `retro-pattern-recurring-2-days` (khuyến nghị Wags có sẵn từ 08-10), (c) ceiling TV1 — tuy đã
   hành động (20.497), câu hỏi bus gốc `zalopay-tv1-ceiling-vs-t1-band` vẫn cần 1 event `answer`
   đóng chính thức.
2. Ghi file `kb/incidents/2026-08/` cho 3 sự cố còn thiếu: TV1 DNS-block đầu phiên (#2), SMTP
   DNS-block email P0 (#3), ceiling decision-via-action (#4).
3. TV1 mới đạt 61%(SpaceX)/50%(ZaloPay) kế hoạch 08-13 — quyết mua nốt 08-14 hay coi đã đóng
   phiên (ADV mỏng, tương tự §27 fill-reconciliation).
4. Điều tra root cause DNS-block hạ tầng job `_codex_` headless (09:14-09:21 ICT hôm 08-13) —
   chưa rõ có tái diễn không, chưa có cơ chế retry/backoff riêng cho lớp job này.

## Bối cảnh còn hiệu lực (không đổi từ trước)
- Cron `compute_active_nav_all.sh` (20:15 ICT T2-T6) + permission Edit/Write `data/trade_plans/**`
  đã XONG (08-13 sáng).
- `tav2_bq.corporate_action` (DIV/ISS/AIS event-level) đã research xong, ghi
  `kb/data_registry/price-volume/corporate_action_bq.md` (status TRAP, chưa có writer/cron) —
  CHƯA wire vào pipeline nào.
- Chuỗi corporate_action/paper-report (Việc A-E) khép lại 08-13; còn Việc B (Oshares) chờ user
  chọn consumer đầu tiên. Crontab `corp_action_daily.py` (07:30 ICT T2-T6) đã cài, alert-only.

- [2026-08-13T18:29:45Z] 2026-08-13 tối: Chuỗi Oshares/corp-action HOÀN TẤT (12 vòng quant-skeptic tổng cộng cả ngày, 3 lần REFUTED thật đều đã vá). Việc A/B đã wire an toàn. 1 quyết định chính sách còn treo cho user: mở SANITY_FACTOR cho corp_action_daily.py không (ẩn số 34 mã lịch sử gồm VHM/VND đang giữ). 08-14 07:30 ICT sẽ có 1 cảnh báo THẬT (EVF/SHB, do mô hình siết chặt) — đã biết trước, không phải sự cố.
- [2026-08-14T01:31:16Z] [2026-08-14T01:26Z] SANITY_FACTOR ĐÓNG: user chọn C (WARN, không ẩn số), Taylor wire (mike@1ea8c4ee), quant-skeptic CONFIRMED cao (tái lập BQ thật khớp tuyệt đối). Còn 1 gap coverage kỹ thuật nhẹ (0 test run()-level) — không khẩn, không phải policy. Đã báo user + đóng kb/projects/corporate-action-bq-integration-0813.md.
