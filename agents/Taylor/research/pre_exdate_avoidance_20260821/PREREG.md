# PREREG — Pre-ex-date buy avoidance (BAL/LAG)

- **Job**: `Taylor_20260821_103727` (dispatch từ Mike)
- **Ngày đăng ký**: 2026-08-21, ICT
- **Trạng thái**: commit TRƯỚC khi đọc bất kỳ outcome nào (BHAR chưa được tính lúc file này được commit)

## 1. Câu hỏi

Buy signal (BAL hoặc LAG) kích hoạt **≤10 ngày lịch trước cash-dividend ex-date** của chính mã đó
có BHAR_20 **tệ hơn** signal kích hoạt **≥30 ngày trước ex-date** không? Nếu có, đó là căn cứ cho
filter production "hoãn entry khi sát ex-date".

## 2. Giả thuyết (đăng ký trước)

- **H1 (PRIMARY)**: `BHAR_20(near_ex) − BHAR_20(far) ≤ −1,5pp` với `|t| ≥ 2,0` (two-sided).
- **H0**: hai cohort không khác nhau.
- **Prior cơ học**: giá ex-date bị điều chỉnh xuống bằng cổ tức tiền mặt. Nếu chuỗi giá đo BHAR
  dùng cột **chưa** điều chỉnh cổ tức thì near_ex sẽ tệ hơn **do kế toán**, không phải do alpha —
  xem §6 (bẫy bắt buộc kiểm soát).

## 3. Dữ liệu (khoá trước)

| Thành phần | Nguồn | Ghi chú |
|---|---|---|
| Buy entries | `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_repin0803_price_univpit.csv` (CSV pin R3 chính thức 2026-08-03, `results_registry.md` §"RE-PIN R3 THEO ĐÚNG MẶC ĐỊNH PRODUCTION `LAG_ADV_BASIS=price`") | `record_type=TX`, `action=buy`. **1 event = 1 `holding_id`**, lấy fill ĐẦU TIÊN làm `entry_date` (ramp 3 phiên ⇒ nhiều fill/1 deal). |
| Ex-dates | `tav2_bq.corporate_action`, `event_code='DIV'`, `event_status='executed'` | dedup key `(ticker, exright_date, dividend_year, dividend_stage_vi)`. Bẫy (3) data-registry: trùng `(ticker,exright_date,event_code)` ⇒ dedup có chủ đích, KHÔNG SUM mù. |
| Giá | `tav2_bq.ticker`: `Close` (đã điều chỉnh hồi tố) và `Price` (thô) | Đo BHAR bằng **CẢ HAI**, xem §6. |
| Benchmark | `tav2_bq.ticker WHERE ticker='VNINDEX'`, cột `Close` | |
| Regime (mô tả, không lọc) | `tav2_bq.vnindex_5state_dt5g_live` — **KHÔNG** dùng `vnindex_5state` (v3.4b BASE, bẫy CLAUDE.md) | |

## 4. Định nghĩa đo lường

- `days_to_ex` = `exright_date − entry_date` (ngày LỊCH), lấy **ex-date tương lai gần nhất** của
  cùng mã trong cửa sổ `(0, 60]` ngày sau `entry_date`.
- `BHAR_20` = `Close(t+20 phiên)/Close(t) − 1` − `VNINDEX_Close(t+20 phiên)/VNINDEX_Close(t) − 1`,
  với `t` = phiên giao dịch của `entry_date`. `t+20` là **phiên**, không phải ngày lịch.
- **Bin**: `near_ex` = `days_to_ex ∈ [0,10]` · `mid` = `[11,29]` · `far` = `[30,60]` ·
  `no_ex` = không có ex-date trong `(0,60]`.
  ⚠️ Lưu ý cách đọc: `far` ở đây nghĩa là "có ex-date nhưng ≥30 ngày nữa", KHÔNG phải "không có
  ex-date" — `no_ex` là cohort riêng, báo cáo kèm nhưng KHÔNG dùng quyết GO.

## 5. Thống kê

- So `near_ex` vs `far` bằng **two-sided Welch t-test** (N độc lập = số **deal**, không phải số dòng).
- **Block bootstrap 5.000 vòng, block = tháng lịch của `entry_date`** (kiểm soát chồng lấn cửa sổ
  20 phiên và cụm mùa chia cổ tức). Báo CI 95% của hiệu số.
- **IS** = `entry_date ≤ 2019-12-31` · **OOS** = `entry_date ≥ 2020-01-01`.

## 6. Bẫy PHẢI kiểm soát (đăng ký trước, không phải hậu kiểm)

**Cột giá quyết định kết quả.** `ticker.Close` là giá **điều chỉnh hồi tố** (đã trừ cổ tức ngược về
quá khứ), `ticker.Price` là giá **thô** (rơi đúng bằng cổ tức tại ex-date). Đo BHAR bằng `Price`
qua một ex-date sẽ tạo ra chênh lệch âm **thuần kế toán** đúng bằng tỷ suất cổ tức — đó KHÔNG phải
alpha và KHÔNG justify filter nào (nhà đầu tư nhận tiền mặt bù lại).
⇒ **Kết quả PRIMARY đo trên `Close`.** Kết quả trên `Price` chỉ báo cáo như **chứng minh cơ học**
(kỳ vọng: hiệu số âm ~bằng div yield). Nếu hiệu số trên `Close` ≈ 0 còn trên `Price` âm mạnh ⇒
kết luận: **hiệu ứng là kế toán, NO-GO**.

(Bài học mang từ job `_024006`: `Low/High` là giá hồi tố còn `Price` là thô — lệch hệ quy chiếu
từng vứt 96% mẫu. Luôn khai hệ quy chiếu trước.)

## 7. Quy tắc quyết định (khoá trước)

| Verdict | Điều kiện |
|---|---|
| **GO** | H1 đạt trên `Close` **cả IS và OOS** (`|t| ≥ 2,0` mỗi nhánh) VÀ **cùng dấu** VÀ hiệu số full-sample `≤ −1,5pp` VÀ block-bootstrap CI 95% không chứa 0 |
| **WEAK_N** | `N(near_ex) < 30` ở bất kỳ nhánh IS hoặc OOS ⇒ báo WEAK_N, **không** GO dù t đẹp |
| **NO-GO** | mọi trường hợp còn lại, gồm: hiệu số dương, không significant, IS/OOS ngược dấu, hoặc hiệu ứng chỉ tồn tại trên `Price` mà biến mất trên `Close` |

## 8. Deviation log

Mọi sai lệch so với file này phải ghi nối vào cuối file, có ngày + lý do, KHÔNG sửa nội dung trên.

