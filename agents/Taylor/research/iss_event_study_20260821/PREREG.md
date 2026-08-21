# PREREG — Rights-offering (ISS/Rights) event study

- **Job**: `Taylor_20260821_103727` (dispatch từ Mike, HƯỚNG C)
- **Ngày đăng ký**: 2026-08-21, ICT
- **Trạng thái**: commit TRƯỚC khi đọc bất kỳ outcome nào (chưa tính BHAR lúc file này được commit).
  Những gì ĐÃ khảo sát trước khi viết file này: **chỉ schema + độ phủ field**, không đọc return nào —
  xem §3.1, đây là căn cứ cho 2 deviation phải khai trước.

## 1. Câu hỏi

Cổ phiếu underperform hay outperform benchmark trong **60 phiên** sau khi công ty phát hành thêm
qua quyền mua cho cổ đông hiện hữu (rights offering)? Discount càng sâu thì effect càng mạnh không?

## 2. Giả thuyết (đăng ký trước)

- **H1 (PRIMARY)**: `BHAR_60 < 0` (underperform) với độ lớn `≤ −2pp` và `t ≤ −2,0` (one-sided theo
  hướng đã nêu; báo cáo kèm p two-sided).
  Prior: rights issue = tín hiệu doanh nghiệp CẦN VỐN, và pha loãng cổ đông không thực hiện quyền.
- **H2 (SECONDARY, chỉ báo — KHÔNG quyết GO/NO-GO)**: nhóm discount sâu (giá phát hành ≤ 70% giá thị
  trường tại ex-right, tức discount ≥ 30%) underperform nhiều hơn nhóm discount nông.
- **IS** = `exright_date ≤ 2019-12-31` · **OOS** = `exright_date ≥ 2020-01-01`.

## 3. Dữ liệu (khoá trước)

| Thành phần | Nguồn | Ghi chú |
|---|---|---|
| Sự kiện | `tav2_bq.corporate_action`, `event_code='ISS'` **AND `issue_method_code='Rights'`** AND `event_status='executed'` AND `exright_date IS NOT NULL` | 1.568 dòng, 2002-02-10 → 2026-08-11 |
| Event date | **`exright_date`** (t=0) | KHÔNG dùng `listing_date` — Bẫy 5 data-registry: đó là ngày niêm yết bổ sung, không phải ngày thông báo. KHÔNG làm announcement study — Bẫy 2b: bảng bị UPSERT in-place, `public_date` của sự kiện `executed` đã mất vĩnh viễn. |
| Giá | `tav2_bq.ticker`: `Close` (điều chỉnh) + `Price` (thô) | xem §6 |
| Universe PIT | `tav2_mike.universe_pit` (`in_universe=TRUE` tại `exright_date`) | KHÔNG dùng `ticker_prune` (lệnh dispatch) |
| Benchmark | `tav2_bq.ticker WHERE ticker='VNINDEX'`, `Close` | |
| Regime | `tav2_bq.vnindex_5state_dt5g_live` cột `state` | KHÔNG dùng `vnindex_5state` (v3.4b BASE) |
| Ngành (ghép cặp control) | `corporate_action.icb_code_lv1` | 1.568/1.568 non-null |

### 3.1 HAI DEVIATION khai TRƯỚC (bắt buộc, vì lệnh dispatch giả định khác thực tế bảng)

1. **`event_code='RIGHTS'` KHÔNG TỒN TẠI.** `event_code` chỉ có {DIV, ISS, AIS, NLIS, SUSP, MOVE, MA}.
   Rights offering nằm TRONG `ISS`, phân biệt bằng `issue_method_code='Rights'`
   (`issue_method_name_vi` = "Quyền mua CP cho Cổ đông hiện hữu"). Lấy nguyên `event_code='ISS'` sẽ
   gộp cả cổ tức bằng CP / thưởng / ESOP / riêng lẻ — **khác câu hỏi**. ⇒ PRIMARY = `Rights` thuần.
   Báo cáo kèm một cohort mô tả rộng hơn "huy động vốn" (`Rights` + `PP` + `PUBL`) — **mô tả, không
   quyết GO**.
2. **`value_per_share` NULL 100% trên MỌI dòng `ISS`** (đo: 0/11.719 non-null; nó chỉ populate cho
   `DIV`). ⇒ H2 KHÔNG tính được như lệnh dispatch viết. Proxy thay thế, khai trước:
   `issue_price = total_value / issue_volumn` (1.549/1.568 = 98,8% tính được).
   Sanity filter đăng ký trước: chỉ giữ `issue_price ∈ [1.000 ; 500.000]` VND.
   `discount = 1 − issue_price / Price(exright_date)`; nhóm sâu = `discount ≥ 30%`.
   ⚠️ Mẫu số dùng **`Price`** (giá THÔ tại ex-right) vì `issue_price` là giá danh nghĩa thô — so với
   `Close` (đã điều chỉnh hồi tố) là so hai hệ quy chiếu khác nhau.

## 4. Định nghĩa đo lường

- `BHAR_60` = `Close(t+60 phiên)/Close(t) − 1` − `VNINDEX(t+60 phiên)/VNINDEX(t) − 1`, `t` = phiên
  giao dịch tại/liền sau `exright_date`. Cửa sổ tính từ **t+1..t+60** (giá vào tại `Close(t)` = sau
  khi giá đã điều chỉnh ex-right ⇒ không dính cú rơi kỹ thuật của chính ngày ex-right).
- Ràng buộc mẫu: mã phải `in_universe=TRUE` tại `exright_date`, và có đủ 60 phiên giá sau đó.

## 5. Thống kê & robustness (khoá trước)

- **PRIMARY**: one-sample t-test `BHAR_60` vs 0, N độc lập = số **sự kiện**.
- **Block bootstrap 5.000 vòng, block = tháng lịch của `exright_date`** (ISS có mùa vụ rõ).
- **Control ghép cặp**: với mỗi sự kiện, lấy các mã KHÁC cùng `icb_code_lv1`, cùng tháng `exright_date`,
  `in_universe=TRUE`, **không** có sự kiện `Rights` nào trong ±90 ngày → trung bình `BHAR_60` của nhóm
  đó làm control. Báo `BHAR_60(event) − BHAR_60(control)` = **hiệu ròng ghép cặp**.
- **Robustness regime**: chạy lại sau khi LOẠI sự kiện có `state ∈ {0 CRISIS, 4 EX-BULL}` tại `exright_date`.
- **IS/OOS** theo §2.

## 6. Bẫy PHẢI kiểm soát (đăng ký trước)

Cùng bẫy hệ quy chiếu giá của HƯỚNG A: `Close` là giá **đã điều chỉnh hồi tố cả cổ tức lẫn pha
loãng ex-right**; `Price` là giá **thô**, rơi đúng bằng phần pha loãng tại `exright_date`. Rights
offering pha loãng RẤT mạnh (`exercise_ratio` tới 1,0–2,0 = phát hành thêm 100–200% số CP đang lưu
hành) ⇒ đo BHAR trên `Price` sẽ ra âm khổng lồ **thuần kế toán**, vô nghĩa.
⇒ **PRIMARY đo trên `Close`.** Kết quả trên `Price` chỉ báo cáo như đối chứng cơ học.

## 7. Quy tắc quyết định (khoá trước)

| Verdict | Điều kiện |
|---|---|
| **GO** | H1 đạt trên `Close` **cả IS và OOS**: `BHAR_60 ≤ −2pp` và `t ≤ −2,0` mỗi nhánh, cùng dấu, block-boot CI 95% full-sample không chứa 0 |
| **WEAK_N** | `N < 30` ở bất kỳ nhánh IS hoặc OOS |
| **NO-GO** | hiệu ứng DƯƠNG (outperform), hoặc không significant, hoặc IS/OOS ngược dấu, hoặc hiệu ứng biến mất sau khi trừ control ghép cặp |

H2 báo cáo kèm nhưng **không** lật verdict theo cả hai chiều.

## 8. Deviation log

Ghi nối vào cuối file, có ngày + lý do. Không sửa nội dung phía trên.
