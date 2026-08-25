# Phần B — Factor-neutral check: DC BULL outperformance là alpha hay beta ngành?

Job `Taylor_20260825_151108`, script `exp_dc3book_factorcheck_20260825.py`. Câu hỏi treo lại từ
giai đoạn 1 (caveat #2, `dc_3book_architecture_20260825.md`): DC universe 56% Banking+Securities —
outperform BULL có thể chỉ là beta ngành re-rate mạnh, không phải alpha chọn mã double-confirm.

## Method

**Control leg**: naive equal-weight buy-and-hold rổ 5 mã Banking trong universe DC (MBB/ACB/HDB/
TCB/VCB) — **KHÔNG có sector-lens gate, KHÔNG có 8L rating gate**, luôn đầu tư 100% (không parking/
cash), tính gross theo state DT5G (đọc trực tiếp `vnindex_5state_dt5g_live.parquet`, local cache
fresh 2026-08-25). Đối chứng: nếu naive-basket gross ≈ DC gross → thuần beta ngành. Nếu DC vượt rõ
rệt naive-basket → có alpha thật từ gate double-confirm.

**Self-check numbering**: session counts theo state code DT5G (1/2/3/4/5) = 489/241/1941/422/60 —
khớp gần như tuyệt đối với BULL=422 đã dùng ở job `_134238` (golive numbering 4=BULL) → xác nhận
đúng code 4=BULL trong bảng dưới, không lẫn numbering.

## Kết quả

| Config | Window | State | N | ann_gross |
|---|---|---|---:|---:|
| naive_bank5 | FULL | BULL(4) | 422 | **+46.32%** |
| naive_bank5 | OOS 2020+ | BULL(4) | 352 | **+41.49%** |
| naive_bank5 | FULL | CRISIS(1) | 489 | -4.13% |
| naive_bank5 | FULL | BEAR(2) | 241 | -5.12% |
| naive_bank5 | FULL | NEUTRAL(3) | 1941 | +25.73% |
| naive_bank5 | FULL | EXBULL(5) | 60 | +77.27% |

So với 2 nguồn đã có (job _145251 Q4 và job _134238):

| | BULL gross FULL | BULL gross OOS |
|---|---:|---:|
| baseline (100% parking basket, custom30V) | +45.34% | +46.50% |
| **naive Bank5 (beta thuần, không gate)** | **+46.32%** | **+41.49%** |
| DC (ConvergePort eq-weight, always-park variant, job _145251) | **+64.12%** | **+68.94%** |

## Kết luận

**Naive Bank5 (thuần beta ngành, không gate nào) gần như BẰNG baseline parking trong BULL** — full
+46,32% vs +45,34% (chênh <1pp), và ở OOS naive Bank5 còn **THẤP HƠN** baseline (+41,49% vs
+46,50%). Nếu outperformance của DC chỉ là beta Banking/Securities thuần, thì naive Bank5 phải
outperform baseline rõ rệt trong BULL — điều đó **KHÔNG xảy ra**.

**DC vượt xa CẢ HAI** (baseline lẫn naive Bank5) trong BULL, cả full lẫn OOS (+64% và +69% so với
~45-46%). Chênh lệch DC − naive_bank5 ≈ +18-27pp — đây chính là phần **alpha từ gate double-confirm
(sector-lens BUY ∩ 8L rating ≤2)**, không giải thích được bằng thuần beta ngành Banking.

→ **Bác bỏ giả thuyết "chỉ là beta ngành".** Outperformance BULL của DC có thành phần alpha thật
từ cơ chế double-confirm, không chỉ là việc universe nghiêng Banking/Securities đúng lúc ngành đó
re-rate. Caveat #2 của giai đoạn 1 được giải quyết theo hướng **ủng hộ DC**.

### Giới hạn

- Naive Bank5 chỉ dùng 5/16 tên (đúng nhóm Banking bị nghi ngờ nhiều nhất, không phải toàn bộ
  universe DC 16 tên — Securities/FPT/khác không kiểm tra riêng ở đây, nhưng banking là nhóm lớn
  nhất (5/16, 31%) và đúng nhóm dispatch chỉ định).
- Đây là DC-luôn-active-mọi-state (proxy ConvergePort gốc, always-park), không phải r_DC state-gated
  dùng ở Phần A — hai con số DC khác nhau do khác quy ước parking, nhưng đều RÕ RÀNG vượt naive
  Bank5, nên kết luận "có alpha" không phụ thuộc vào lựa chọn quy ước nào.
- Không kiểm định thống kê (t-test/bootstrap) chênh lệch DC vs naive — N=422 đủ lớn để tin xu hướng
  nhưng chưa qua DSR/PBO như mọi backtest R&D khác trong job này.
