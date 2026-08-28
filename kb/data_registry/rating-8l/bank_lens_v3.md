---
kind: script-output
status: BLOCKED-STALE
source: data/bank_lens_v3.csv
group: rating-8l
note: CHƯA refresh được — vnstock library deprecated 31/08/2025, mọi mã trả KeyError('lengthReport'); vẫn stale từ 2026-05-31 (job Taylor_20260828_081256)
writer: bank_lens_v3.py (repo root) — pull vnstock finance.ratio per ticker, ad-hoc chạy tay
---

# data/bank_lens_v3.csv (+ bank_lens_v3.md — cùng builder, cùng lần chạy)

**Status: BLOCKED-STALE (data 2026-05-31, không refresh được ngay bây giờ)**

## Là gì
Sector lens 18 mã bank (VCB BID CTG TCB MBB ACB VPB VIB HDB STB SHB TPB MSB OCB LPB EIB NAB SSB) —
gate asset-quality cứng (AVOID/WATCH/CLEAN theo NPL, coverage, CAR, ROE, NPL-trend) + rank CLEAN
banks theo quality+value. Feed vào `rating_8l.py` route BANK (dòng ~528) — nhưng route BANK vẫn
hoạt động không có file này (fallback `ICB_Code==8355`, xem Bẫy).

## Ai ghi / cadence
`bank_lens_v3.py` (repo root, executable) — kéo `finance.ratio(period="quarter")` từ **vnstock/VCI**
qua `Vnstock().stock(...).finance.ratio(...)`. Ad-hoc, không cron.

## Vì sao BLOCKED-STALE (xác nhận thật 2026-08-28)
Chạy `python3 bank_lens_v3.py` → **100% mã bị skip**, lỗi `parse KeyError('lengthReport')` — thư
viện `vnstock` in cảnh báo "VNSTOCK DEPRECATION NOTICE (31/08/2025)": class `Vnstock()` cũ (kể cả
`.stock(...).finance.ratio(...)`) đã ngừng hỗ trợ, schema trả về không còn cột `lengthReport` mà
code cũ kỳ vọng. Đây KHÔNG phải lỗi rate-limit tạm thời (dù script cũng ăn rate-limit guest 20
req/phút song song) — là breaking change upstream cần **sửa code sang `vnstock.api.quote.Quote`**
trước khi refresh lại được. Việc sửa migration nằm NGOÀI phạm vi job đăng ký registry này.

## Bẫy
- **Đọc số trong `data/bank_lens_v3.csv`/`.md` hiện tại = đọc dữ liệu tháng 5/2026** — NPL/coverage/
  CAR/ROE có thể đã đổi 1 quý (Q2 2026 đã có trên `tav2_bq.ticker_financial` từ lâu). Đừng dùng cho
  quyết định BANK sector gần đây mà không tự kiểm lại bằng nguồn khác (vd BQ `ticker_financial`
  trực tiếp cho 18 mã này) hoặc chờ ai đó sửa migration.
- `rating_8l.py` fail-safe khi thiếu/lỗi file (route vẫn chạy qua `ICB_Code==8355`, chỉ mất phần
  gate asset-quality CLEAN/WATCH/AVOID riêng của lens này) — KHÔNG crash, nên staleness/broken
  không tự lộ qua lỗi chạy.
- **CÙNG lỗi sẽ xảy ra với BẤT KỲ script nào khác trong repo còn dùng `Vnstock().stock(...)` kiểu
  cũ** — nếu thấy lỗi `KeyError('lengthReport')` ở script khác, đây là cùng nguyên nhân gốc, không
  phải bug riêng của từng script.
- Refresh lại: cần sửa `bank_lens_v3.py` sang API mới trước (không tự động dùng data_registry_audit
  Section E hay B để phát hiện — 2 section đó chỉ kiểm tra "có đăng ký chưa"/"còn mới không",
  không kiểm tra được builder có CHẠY ĐƯỢC không).
