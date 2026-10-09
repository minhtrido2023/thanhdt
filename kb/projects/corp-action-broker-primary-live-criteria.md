# Corp-action broker-primary — tiêu chí bật live

> Chuyển nguyên văn từ `kb/current_ops.md` 2026-10-09 (kb-hot-size-gate). Lịch sử vòng r1–r10: `agents/Taylor/research/broker-primary-20261004.md`.

## Corp-action broker-primary SHADOW — tiêu chí bật live (user chốt 2026-10-09 22:11 ICT, `decided_by: user`)
- `bin/corp_action_auto_confirm.py` nhánh broker, cron 19:25 T2-T6, `MIKE_CA_BROKER_SOURCE` mặc định `shadow` (merge r10 `bacf6e99`). Bật `live` CHỈ khi đủ CẢ:
  1. ≥3 sự kiện **điều chỉnh giá** thật trên mã đang giữ đi qua shadow; mỗi ca broker MATCH record người ký, hoặc không ghi + hỏi đúng chỗ (AIS/niêm yết bổ sung KHÔNG tính).
  2. 0 ca broker `CONFIRMABLE` sai.
  3. Đã xác minh 1 lần DNSE `quote_only` trả `marketId` sau 19:00.
  4. 0 crash / kẹt khoá trong cửa sổ shadow.
  5. Ngay trước khi bật: 1 vòng test-only (Sonnet medium) cho 5 đột biến tương đương/nhẹ còn sống từ arch-review r9 (ask_key chỉ theo mã; không chuẩn hoá mã ở khoá vendor; xday chỉ áp mục gửi bù; so ex thô không `_iso`; write-incomplete thiếu `xday_note`).
- **Mốc xem lại 2026-12-15**: chưa đủ 3 sự kiện ⇒ Mike trình user số liệu đã có để quyết bật/chờ tiếp. Nguồn đếm: `data/corp_action_broker_ledger.jsonl` + bus finding `corp-action-broker-shadow-<D>` + `logs/corp_action_auto_confirm.log`. Tới 09/10: 5 phiên shadow, 0 mục.

