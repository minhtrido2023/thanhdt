# Nhãn AS-OF cho kết quả pin trong `data/results_registry.md`

**Job:** `Taylor_20260729_155142` (Việc 2) · **Ngày:** 2026-07-29 · **Tác giả:** Taylor

## 1. Vì sao cần

Sự cố 2026-07-29: `vnindex_5state_dt5g_live` bị viết lại 101/3.134 phiên lịch sử (3,22%) mà
không ai biết, do backfill `VNINDEX_PE` 2006+ lan qua cơ chế expanding-window. Baseline R3 pin
ngày 2026-07-22 (27,16%) được đo trên chuỗi state cũ ⇒ lỗi thời trong im lặng.

Vấn đề rộng hơn sự cố này: **không thể quay lại dữ liệu của một ngày trong quá khứ.**
- BQ time-travel đã tắt cho các bảng liên quan.
- `ticker` / `ticker_prune` bị **TRUNCATE + rebuild** mỗi ngày (bq_admin) ⇒ mọi mã "vào bằng
  daily-append" biến mất ở lần rebuild kế; 07-29 vừa mất 58 mã khỏi **toàn bộ** lịch sử.
- Corp-action re-adjust `Close`/`MA` ~2–3%/tuần.

Đo thật hôm nay, **cùng lệnh pin, cùng `AUDIT_END=2026-06-19`, chỉ khác vintage cache**:

| vintage cache | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|
| 2026-07-22 (pin cũ) | 27,16% | 1,81 | −18,1% | 1,50 |
| 2026-07-28 (trước restate) | 27,63% | 1,84 | −18,1% | 1,53 |

**+0,47pp CAGR chỉ vì trôi dữ liệu trong 6 ngày**, chưa tính restate DT5G. Không có nhãn vintage
thì một con số pin là **không kiểm chứng được** — và tệ hơn, chênh lệch do trôi dữ liệu dễ bị
đọc nhầm thành alpha của một thay đổi mô hình.

## 2. Định dạng đề xuất

Mỗi mục pin trong `data/results_registry.md` thêm **một khối `AS-OF DATA VINTAGE`** ngay dưới
bảng số. Bốn phần bắt buộc:

```markdown
### AS-OF DATA VINTAGE
- `run_date`: 2026-07-29T16:4xZ (giờ UTC, giờ chạy thật, không phải giờ soạn ghi chú)
- `cache_dir`: `data/bq_cache` — full re-sync 2026-07-29T15:53Z
- `manifest.verified`: **true** · `verified_at`: 2026-07-29T...Z
- `snapshot`: `data/bq_cache_asof20260729_postrestate/` (ĐÓNG CỨNG, read-only)  ← hoặc "KHÔNG GIỮ"
- `reproducible`: **CHỈ TỪ SNAPSHOT** — BQ time-travel đã tắt, `ticker`/`ticker_prune` bị
  TRUNCATE+rebuild mỗi ngày ⇒ chạy lại trên live BQ ngày khác **KHÔNG** tái lập được con số này.

| bảng | rows | max_time | md5 (16 ký tự đầu) |
|---|---|---|---|
| `vnindex_5state_dt5g_live` | 3.135 | 2026-07-28 | `...` |
| `ticker` | ... | ... | `...` |
| ... | | | |
```

**Sinh khối này bằng lệnh, không gõ tay** (tránh sai/khỏi quên):
```bash
python3 mike/agents/Taylor/bin/cache_vintage_stamp.py data/bq_cache --md
```
Script in đúng bảng md ở trên (7 bảng then chốt: 2 bảng state, `ticker`, `ticker_prune`,
`universe_pit_q`, `ticker_financial`, `fa_ratings_8l`). md5 tính cả cho bảng partitioned
(thư mục) theo thứ tự file đã sort ⇒ ổn định giữa các lần chạy.

### Vì sao có md5 mà vẫn cần snapshot
md5 chỉ **phát hiện** khác vintage, không **khôi phục** được. Chỉ snapshot mới cho phép chạy
lại. Chính sách đề xuất (cân với đĩa — hiện còn ~13 GB trống, mỗi snapshot ~2,0 GB):

| | Giữ gì |
|---|---|
| **Mọi** kết quả pin | Khối `AS-OF DATA VINTAGE` (md5 + rows + max_time) — **luôn luôn**, ~1 KB |
| Chỉ **số pin CHÍNH THỨC hiện hành** (R3) | + 1 snapshot cache đầy đủ, xoay vòng khi re-pin |
| Mốc lịch sử đặc biệt | + snapshot theo quyết định riêng (vd `bq_cache_asof20260728` = mốc **trước** restate, giữ làm bằng chứng attribution vụ 07-29) |

Snapshot cũ khi bỏ: xoá **sau** khi số pin mới đã qua quant-skeptic, không xoá trước.

## 3. Quy tắc kèm theo (đề xuất đưa vào `coding_guidelines.md` §8)

1. **Không có khối AS-OF ⇒ không phải số pin.** Số không có vintage chỉ được trích dẫn kèm chữ
   "không tái lập được".
2. **So sánh 2 con số chỉ hợp lệ khi CÙNG vintage.** Quy tắc này đã có sẵn trong registry mục
   07-22 ("KHÔNG so `pit_v2c` với pin cũ 27,84%"); nhãn as-of biến nó từ ghi nhớ thành thứ
   kiểm tra được bằng md5.
3. **Baseline lỗi thời phải được đánh dấu tại chỗ**, không chỉ thêm mục mới ở cuối file — gạch
   ngang + con trỏ tới mục thay thế (registry đang dài >4.000 dòng, người đọc thường dừng ở
   bảng đầu tiên gặp).
4. **Re-pin định kỳ, không chỉ khi có sự cố.** Trôi +0,47pp/6 ngày nghĩa là số pin có "hạn dùng".
   Đề xuất: R3 re-pin theo tháng, gắn vào cùng nhịp với snapshot BQ hàng tháng mà Winston đang
   dựng (`bin/bq_monthly_pin.py`) — dùng chung snapshot, không tạo cadence mới.

## 4. Áp dụng ngay (Việc 2 của job này)

- Baseline R3 mới (Việc 1) ghi kèm khối AS-OF đầy đủ + snapshot đóng cứng.
- Baseline cũ 27,16% (pin 2026-07-22): đánh dấu **SUPERSEDED / KHÔNG TÁI LẬP ĐƯỢC** — vintage
  cache 07-22 đã bị các lần sync sau ghi đè, không còn tồn tại ở bất kỳ đâu. Đây chính là ca
  mẫu cho quy tắc trên: một con số từng là "CHÍNH THỨC" mà nay **không ai kiểm chứng lại được**.
