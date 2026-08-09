# `entry_anchor_price` — vá lỗ hổng KỸ THUẬT của luật entry-window V2.4

**Job**: `Taylor_20260809_082212` · **Ngày**: 2026-08-09 · **Trace gốc**: `DollarBill_20260809_075604`

## 1. Vấn đề

User duyệt CHÍNH SÁCH (2026-08-09, nguyên văn): *"Tôi đồng ý duyệt luật mới và làm lại plan mua
DRI như một lệnh bình thường của book lagged."* Luật V2.4 mở cửa sổ entry LAG = phiên chuẩn + 2
phiên kế tiếp.

Nhưng điều kiện an toàn CỐT LÕI của chính luật đó — *"giá live không vượt `entry_anchor_price` đã
lưu ở phiên chuẩn"* — **không có nguồn dữ liệu nào sinh ra**. Bản vá uncommitted chỉ đặt cờ
`requires_anchor_price=True` rồi thả mã vào `due_today`: **cửa sổ mở ra nhưng cái chốt cửa không
tồn tại**. Chạy thẳng như vậy ⇒ plan sinh candidate ngày 2/3 mà không ai kiểm được điều kiện
chống mua-đuổi.

## 2. Nguồn anchor — quyết định và LÝ DO BÁC bỏ đề xuất ban đầu

Đề xuất ban đầu (Mike) là dùng **`Close`**. **BÁC** — dùng `Price` (giá THÔ).

| | `Price` | `Close` |
|---|---|---|
| Nội dung | giá thật khớp trên sàn phiên đó | **đã điều chỉnh** cổ tức/chia tách, hồi tố từ vintage HÔM NAY |

Anchor được đem so với **giá live trên bảng (DNSE) = giá thô**. Lấy `Close` là trộn hai hệ quy
chiếu — đúng **"Bẫy (2)"** trong `kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md`
(đã gây 2 lỗi thật trong 3 báo cáo client-facing T7/2026). Nếu mã chốt quyền giữa phiên chuẩn và
phiên 2/3, `Close` phiên chuẩn bị kéo XUỐNG so với giá thật ⇒ anchor thấp giả tạo ⇒ **chặn oan một
entry hợp lệ**.

Với DRI hai cột tình cờ bằng nhau (13.000) — sự trùng khớp đó **không** phải lý do để dùng `Close`;
nó chỉ có nghĩa DRI chưa có ex-date trong cửa sổ này.

**Không dùng cột giá trong CSV khuyến nghị**: cột đó tên là
`close_bq_stale_DO_NOT_USE_AS_REFPRICE` — hàng rào cơ học dựng sau sự cố 2026-07-09 (lệch +5,7%).
**Không dùng `ref_price` trong plan file**: SpaceX có, ZaloPay KHÔNG ⇒ phá tính account-agnostic
của script (bất biến "2 account cùng CSV ⇒ cùng `due_today`").

**BQ hợp lệ ở đây** vì là giá LỊCH SỬ của phiên đã đóng. §6 (dữ liệu cùng ngày phải lấy DNSE)
KHÔNG bị nới: `_reject_non_historical()` **raise** nếu ai đó tra anchor cho ngày `>= plan_date`.

## 3. Cài đặt

| File | Vai trò |
|---|---|
| `mike/bin/lag_entry_anchor.py` | **MỚI** — tra giá thô phiên chuẩn từ `tav2_bq.ticker`, 1 truy vấn batch, guard §6 |
| `mike/bin/filter_lag_entry_window.py` | `_apply_anchor_gate()` + rổ mới `anchor_unavailable`; `filter_window(..., anchor_fetcher=)` |

Tách module có chủ đích: `filter_window()` **vẫn thuần offline** (selfcheck tiêm fetcher giả,
không đụng mạng), BQ chỉ nằm ở đường CLI.

**Fail-safe (fail-closed ở MỌI nhánh hỏng)** — thiếu nguồn tra · BQ lỗi · mã không có dữ liệu ngày
đó · giá ≤ 0 ⇒ mã bị **chuyển sang `anchor_unavailable`** kèm `drop_reason`, **không đoán giá thay
thế**, không im lặng thả vào `orders[]`. Phiên 1 không cần anchor — chính nó đặt ra anchor.

## 4. Verify DRI (câu hỏi #1 CRITICAL)

| Mục | Giá trị | Nguồn |
|---|---|---|
| Entry chuẩn | **2026-08-06** | CSV: `T+3`(08-03) → `T+2`(08-04) → `T+1`(08-05) → `WINDOW_PASSED 2026-08-06`(08-06, 08-07) |
| Cửa sổ | 08-06 (T5, ngày 1) → 08-07 (T6, ngày 2) → **08-10 (T2, ngày 3 — NGÀY CUỐI)** | `next_trading_day` |
| **anchor** | **13.000** | `tav2_bq.ticker.Price` @ 2026-08-06 |
| Giá quan sát mới nhất | **13.200** (close 08-07) | `Price` @ 2026-08-07 |
| Chênh | **+1,54% TRÊN anchor** | |

**Kết luận DRI**: **CÒN TRONG cửa sổ** (ngày 3/3) ⇒ được vào `due_today` như entry LAG bình thường,
đúng ý user. **NHƯNG cổng anchor đang FAIL trên giá quan sát gần nhất.** Quyết định cuối phải so
với **giá LIVE ngày 08-10 lấy từ DNSE** (§6): chỉ đặt lệnh khi **live ≤ 13.000**; live > 13.000 ⇒
**KHÔNG mua** (mua đuổi, luật cấm). 08-10 là ngày cuối — hết phiên là `WINDOW_PASSED`, không catch-up.

Đây chính là điều kiện đã bị bỏ qua âm thầm nếu chạy bản uncommitted.

## 5. Kết quả chạy thật — plan 2026-08-10 (signal 2026-08-07)

12 ứng viên có anchor thật: BSR 25.050 · DRI 13.000 · GVR 27.850 · NVB 11.200 · PHR 58.600 ·
POW 13.400 · SCL 24.200 · SSI 24.450 · TVN 9.200 · VGS 17.900 · VNF 12.800 · VSI 19.600.

**2 mã BỊ LOẠI fail-closed** (đã xác minh là thiếu dữ liệu THẬT, không phải lỗi truy vấn):
- **HMH** — không có dòng nào trong `tav2_bq.ticker` 08-05→08-07 (thu hẹp universe, xem
  `ticker_ohlcv_tables.md`).
- **PGS** — có 08-05 và 08-06 nhưng **không có 08-07**, đúng ngày entry chuẩn của nó.

Cả 2 vốn đã mang cờ đỏ `THANH_KHOAN_CHET,NGOAI_UNIVERSE`.

## 6. Selfcheck

**52/52 PASS** dưới `env -u TZ` (§16). Thêm 6 test fail-closed mới: không có fetcher → loại; BQ nổ
→ loại + ghi lỗi vào `drop_reason`; không có dữ liệu → loại; anchor là SỐ thật không phải cờ;
ngày 1 không bị gate chặn oan. Guard §6 test riêng: tra anchor cho ngày `>= plan_date` → raise.

## 7. Hạn chế / rủi ro tồn dư (disclose)

1. **`_sessions_after()` dùng `next_trading_day`** ⇒ đường quyết định NAY phụ thuộc bảng ngày nghỉ,
   trong khi `_VARIABLE_HOLIDAYS` (Tết ÂL) hiện RỖNG — đây là điều docstring gốc cố ý tránh. Quanh
   kỳ nghỉ chưa khai báo, cửa sổ **hết hạn SỚM hơn** thực tế (fail-closed, không phải mở rộng oan),
   nhưng cần khai báo lịch nghỉ trước Tết.
2. **Anchor = giá đóng cửa phiên chuẩn**, không phải giá khớp thật lẽ ra đã trả (không ai biết vì
   không khớp). Đây là một quy ước, chọn vì auditable + account-agnostic; nó KHÔNG được hiệu chuẩn
   bằng dữ liệu fill thật.
3. Luật mở cửa sổ 3 phiên **chưa qua backtest** — đây là quyết định CHÍNH SÁCH của user, không phải
   edge đã đo. Bản vá này chỉ làm cho điều kiện an toàn của luật **kiểm được**, không chứng minh
   luật sinh lời.
4. Số ứng viên nhảy từ ~0 lên 12 trong phiên đầu áp luật (tồn từ 08-06/08-07). Sizing/%ADV/8L/DD
   giữ nguyên nên vẫn bị các cổng cũ chặn, nhưng DollarBill cần lưu ý khối lượng này khi lập plan.
