# aria-K — executor chờ kết quả ATC sau CLOSED (job Taylor_20260913_091014)

- `executor_atc_postclose.patch` — bản vá + selfcheck. Header ghi lệnh apply, selfcheck, commit.
  Land T2 14/09 ≥15:00, SAU v2 → remove_v23 → aria_H.
- `backfill_vhc_0710.py` — backfill 1 lần fill ATC ZaloPay 07-10 (oid 502431, 600cp @57.500).
  **KHUYẾN NGHỊ: chưa `--apply`** (lý do bên dưới).

## Backfill 07-10: xử lý đếm 2 lần

Hiện có 3 nơi ghi fill này:

| Nguồn | Có 600cp? | Ai đọc |
|---|---|---|
| `dnse_raw_2026-07-10.jsonl` (bản ghi API broker) | KHÔNG (poll cuối 14:45:05 còn New) | `verify_account_snapshot` (vế raw), `reconcile_equity` |
| `exec_ZaloPay_2026-07-10_journal.csv` | KHÔNG | `verify_account_snapshot` (vế journal), `park_holdings`, `daily_nav_snapshot` |
| `data/account_seed_capital.json` → `missing_fills_broker_confirmed` (aria-F2) | CÓ | chỉ `reconcile_equity` |

Đo trong sandbox (bản sao `execution_logs` bằng symlink, chỉ copy thật file journal 07-10; journal
thật không đổi, mtime vẫn 2026-07-10), ZaloPay asof 09-11, 20 ngày `dates_included` của aria-F2:

| | verify_account_snapshot | reconcile_equity |
|---|---|---|
| trước backfill | rc=0, verified | +1.575.955đ (0,1607%) ✅ KHỚP |
| sau backfill | **rc=1**, `WARN qty mismatch VHC: dnse_raw=-1200 journal=-1800` ⇒ "KHÔNG dùng số liệu này để viết báo cáo" | +1.575.955đ ✅ KHỚP (không đổi) |

Kết luận:
1. **Không đếm 2 lần ở reconcile**: `reconcile_equity` không đọc journal, nên phần 600cp vẫn chỉ
   đi vào qua `missing_fills_broker_confirmed`. Giữ nguyên mục seed đó.
   **Tuyệt đối không** nạp 600cp vào dnse_raw: khi đó raw + seed sẽ đếm 2 lần. Hơn nữa dnse_raw là
   bản ghi API broker, không được tự bịa record.
2. **Nếu chỉ backfill journal thì hỏng verify**: vế journal 1.800 ≠ vế raw 1.200. Mọi lần chạy
   verify cho ZaloPay có ngày 07-10 trong `--dates` sẽ ra rc=1. Lệch này tồn tại vĩnh viễn vì raw
   là lịch sử. Không nên dùng `known_position_discrepancies.json` ở đây, vì file đó bắt buộc
   `expires_at`: hết hạn là cảnh báo quay lại.
3. **Đề xuất (việc riêng, chưa làm, cần owner pipeline §6 duyệt)**: cho vế raw của
   `verify_account_snapshot` đọc `missing_fills_broker_confirmed`, giống `reconcile_equity.py:259`.
   Sau đó chạy backfill: raw 1.800 = journal 1.800, và mọi reader thấy cùng một con số. Trước khi
   việc đó xong, cứ để journal như cũ; mục seed đã đủ cho kế toán.
   ⚠ **BẪY (arch-review vòng 1)**: phải cộng seed ở **tầng SO SÁNH của verify** (chỗ dựng
   `raw_agg`), **KHÔNG được** sửa bên trong `dnse_fill_events()`. Lý do: `reconcile_equity.py:246`
   import chính hàm này, rồi tự cộng `missing_fills_broker_confirmed` ở `:259`. Nếu cộng seed trong
   `dnse_fill_events`, reconcile sẽ đếm 600cp 2 lần.

## Ngoài phạm vi patch, cần owner biết
- `mike/bin/session_announce.sh close` (14:50) vẫn báo "bot sẽ tự hủy và dừng trong ít phút tới".
  Những ngày có child mở, bot giờ chờ tới tối đa 14:55. Câu báo chưa sai, nhưng không nhắc bước
  chờ kết quả ATC.

Script đã kiểm bằng chứng thật (dry-run trên dữ liệu live, rc=0): email 1.800cp (600 @57.500),
dnse_raw 1.200cp, journal 1.200cp. Chạy lại lần 2 thì không làm gì (idempotent). Trước khi ghi,
script sao lưu `<journal>.pre_aria_K` và ghi theo kiểu atomic.
