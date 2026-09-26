# PREREG — FiinPro-X H4 + H5 (job Taylor_20260926_164143)

> **Viết TRƯỚC khi chạy bất kỳ phép tính chỉ báo nào.** Timestamp ghi ở git commit đầu tiên của
> thư mục này. Không sửa ngưỡng sau khi nhìn kết quả; nếu phải sửa thì ghi thành mục
> "DEVIATION" ở cuối, kèm lý do, và kết quả sau sửa bị hạ xuống mức thăm dò.

PAPER-ONLY. Không wire. Mọi đề xuất dừng ở finding.

---

## Step 0 — PRE-FLIGHT KHẢ THI (chạy trước, kết quả đã biết)

```
rnd_preflight_power.py --sharpe-ann 0.30 --obs-per-year 252 --n-available 13 \
    --n-trials 4 --n-rule per-episode --max-history-years 12.7
```
→ **NO-GO**. DSR với N=13 episode = 0,1723. Cần 20.370 quan sát = 80,8 năm. Trần dữ liệu
12,7 năm ⇒ DSR tối đa **0,5068**, vẫn dưới 0,95. Sharpe tối thiểu phát hiện được = 13,4 (×44,7).

**Hệ quả BẮT BUỘC mang theo suốt báo cáo:** H4 **không bao giờ** có thể được chứng minh bằng
thống kê trong dữ liệu VN. Mọi kết luận H4 là **chẩn đoán + phán đoán nhân quả**, không phải
bằng chứng thống kê. Cấm tự mình (và cấm người đọc) trích H4 như "đã được xác nhận".
Lý do vẫn chạy: dispatch đặt tiêu chí quyết định là **số lần báo động giả**, không phải p-value;
và đây là CỔNG PHÒNG THỦ (kỳ vọng ΔCAGR ≈ 0 hoặc âm nhẹ), không phải tìm alpha.

H5 chạy pre-flight riêng ở đầu BƯỚC 2 (khác loại: IC cross-sectional, per-day).

---

## BƯỚC 1 — H4: chỉ báo khối ngoại bán ròng KHỚP LỆNH

### 1.1 Nguồn (đã tra `mike/kb/data_registry/` trước)

| Ký hiệu | File | Status | Dùng làm gì |
|---|---|---|---|
| E | `mike/data/fiinprox_vnindex_investor_flow_daily_20260914.csv` | DERIVED (ngoại khớp VNDirect median 1,9 tỷ) | `foreign_matched_net_bn` 2014-01-02→2026-09-14 = TỬ SỐ chính |
| F | `mike/data/fiinprox_foreign_flow_index_daily_20260914.csv` | UNVERIFIED nguồn ngoài | gross 2009-06→2015-12, chỉ cho kiểm tra PHỤ (c) |
| G | `data/bq_cache/ticker/*.parquet` (bảng `ticker` ĐẦY ĐỦ, KHÔNG lọc universe) | — | mẫu số GTGD |
| L | `kb/data_registry/market-state/vn_macro_regime_history_2009_2018_phases.md` | CANONICAL | nhãn episode 2009/2018 — **dùng NGUYÊN, không tự phân loại lại** |
| S | `data/vnindex_5state_dt5g_live.csv` | production DT5G | đếm episode + so cap hiện có |
| P | `data/VNINDEX.csv` cột `time`,`Close` | — | đo drawdown để định nghĩa báo động giả |

**KHÔNG dùng `ticker_prune` làm mẫu số** (§9b: `IN (SELECT DISTINCT ticker FROM ticker_prune)`
không điều kiện `time` là look-ahead universe 1,6-2,6×). Bảng `ticker` đầy đủ không có chọn lọc
universe nên không dính lỗi đó.

**Caveat mẫu số đã biết TRƯỚC:** dòng tiền ngoại là VNINDEX = HOSE; `ticker` gồm cả HNX/UPCOM ⇒
mẫu số lớn hơn HOSE thuần. Đây là hệ số tỷ lệ biến thiên CHẬM, làm ngưỡng tuyệt đối không có ý
nghĩa "phần trăm HOSE" — chỉ dùng như thước đo chuẩn hoá theo quy mô. Ghi lại, không sửa sau.

### 1.2 Hai dạng chỉ báo (khai TRƯỚC, không thêm dạng thứ 3 sau khi nhìn kết quả)

Ký hiệu: `m_t` = `foreign_matched_net_bn` ngày t (âm = bán ròng). `V_t` = GTGD ngày t (tỷ VND).

- **IND-A — ròng khớp lệnh chuẩn hoá theo GTGD**
  - `S20_t = Σ_{i=t-19..t} m_i` ; `S60_t = Σ_{i=t-59..t} m_i`
  - `D_t = median_{i=t-59..t} V_i` (MEDIAN, không mean — bền với ngày thoả thuận/ngày ATC bất thường)
  - `A20_t = S20_t / (20·D_t)` ; `A60_t = S60_t / (60·D_t)`
  - FIRE khi `A20_t ≤ −θ_A` (chính) — hai ngưỡng: **θ_A = 0,02** và **θ_A = 0,03**
  - Biến thể 60 phiên: `A60_t ≤ −0,015`
- **IND-B — z-score tự chuẩn hoá** (không phụ thuộc mẫu số ngoài, kiểm chứng độ bền của A)
  - `z20_t = S20_t / (√20 · SD_{i=t-249..t}(m_i))`
  - FIRE khi `z20_t ≤ −θ_z` — hai ngưỡng: **θ_z = 2,0** và **θ_z = 2,5**

Tổng số cấu hình khai báo: **5** (A20@0,02 · A20@0,03 · A60@0,015 · B@2,0 · B@2,5). Không thêm.

**Vì sao ngưỡng này, chọn TRƯỚC khi nhìn số:** θ_A theo độ lớn kinh tế — khối ngoại bán ròng khớp
lệnh bình quân ≥2% (và ≥3%) tổng GTGD mỗi phiên, duy trì suốt 20 phiên, là mức rút vốn có nghĩa.
θ_z = 2σ/2,5σ là quy ước sự kiện đuôi tiêu chuẩn. KHÔNG chọn ngưỡng bằng phân vị của chính mẫu
sắp test (vòng luẩn quẩn).

### 1.3 Xử lý ngày thoả thuận (khai TRƯỚC)

- Tử số dùng `foreign_matched_net_bn` ⇒ **đã tách thoả thuận theo cấu tạo**, lô Vinhomes
  2018-05-18 (+28.571 tỷ ở cột `foreign_deal_net_bn`) KHÔNG vào tử số.
- Mẫu số: dùng MEDIAN 60 phiên nên ngày thoả thuận khổng lồ không kéo được mẫu số.
- Ngày thiếu dữ liệu (`flags` có `vn_missing`/gap 2018-01-23, 2018-01-24): `m_t` coi là **thiếu**,
  không coi là 0; cửa sổ trượt bỏ qua ô thiếu và chia theo số ô thật (min 15/20 ô mới tính).
- Giai đoạn `provisional` 2026-09-03→09-14: **loại khỏi mọi phép đếm**, chỉ hiển thị.

### 1.4 Quy tắc gộp sự kiện (debounce) — N là SỰ KIỆN, không phải phiên

- Các ngày FIRE liên tiếp hoặc cách nhau < 60 ngày LỊCH thuộc **cùng một sự kiện**.
- Khoảng ≥ 60 ngày lịch không fire ⇒ sự kiện mới.
- Hysteresis khi dùng làm cap: bật khi vượt ngưỡng, **tắt** khi chỉ báo hồi về trên `−θ/2`.
- Tín hiệu tính trên dữ liệu đóng cửa ngày t, cap áp dụng từ **mở cửa t+1** (không nhìn trước).

### 1.5 Định nghĩa BÁO ĐỘNG GIẢ (khai TRƯỚC)

Một sự kiện FIRE là **báo động giả** nếu, tính từ ngày fire đầu tiên của sự kiện đó, VNINDEX
(`Close`) **KHÔNG** giảm ≥ **10%** từ mức đóng cửa ngày fire xuống bất kỳ đáy nào trong **126
phiên (≈6 tháng)** kế tiếp. Ngược lại là báo động đúng.
(10%/6 tháng là ngưỡng thiệt hại tối thiểu biện minh được cho việc hạ trần trạng thái.)

### 1.6 Tiêu chí PASS/FAIL — khai TRƯỚC, không thương lượng lại

**(a) Có bắt được 2018 không** — VN đỉnh 09/04/2018, đáy ≈ 11/07/2018.
- **PASS mạnh**: sự kiện 2018 có ngày fire đầu tiên ≤ **2018-05-31**.
- **PASS yếu**: 2018-06-01 … 2018-07-31 (fire trong lúc rơi, còn kịp giảm thiệt hại).
- **FAIL**: không fire trong 2018, hoặc fire đầu tiên ≥ 2018-08-01 (sau đáy = vô dụng).

**(b) QUYẾT ĐỊNH — báo động giả ngoài 2018** (2014-2017 và 2019-2025, đếm theo SỰ KIỆN):
- **GO-để-quant-skeptic** khi: PASS-(a) ở mức mạnh hoặc yếu **VÀ** số báo động giả ≤ **2**
  trong 11 năm **VÀ** tổng số sự kiện fire ngoài 2018 ≤ **6**.
- **NO-GO** trong mọi trường hợp còn lại.
- Nếu ≥ 2/5 cấu hình cùng đạt GO thì báo cấu hình **trung vị theo độ chặt**, không báo cấu hình
  đẹp nhất (quy chuẩn PBO: chọn robust-trung vị, không IS-best).

**(c) Kiểm tra PHỤ 2009-2013 bằng gross (file F)**: chỉ mô tả, **không** tham gia quyết định —
gross gồm thoả thuận nên không so sánh được trực tiếp. Câu hỏi: chỉ báo có fire bừa trong
rally 2009 (pha 1B theo Bobby) không, và có fire ở pha 1C (điểm gãy 09-12/2009) không.

### 1.7 Overlay NAV (chỉ chạy NẾU (a)+(b) đều PASS)

Vai trò: **CAP tầng 3 của DT5G** — hạ trần trạng thái xuống ≤ NEUTRAL khi fired. Đo ΔCAGR/ΔDD
trên NAV R3 (NEUTRAL-only @50B, universe_pit, pin 2026-08-03: CAGR 28,86% / Sharpe 1,90 /
DD −17,8% / Calmar 1,62 / Final NAV 1.178,01B). Chân control PHẢI tái lập số pin này đến chữ số
thập phân + `self-check 0 VND`, nếu không thì harness sai và kết quả treatment vô nghĩa.
**Kỳ vọng khai trước: ΔCAGR ≈ 0 hoặc âm nhẹ.** ΔCAGR dương lớn ⇒ nghi overfit/leak, phải điều tra
chứ không phải mừng.

### 1.8 So với cap đã có

Cap tầng 3 hiện tại = SBV refi 6m (tiền tệ nội) + VIX/SPX drawdown (hoảng loạn Mỹ) + bypass khi
VN bull xác nhận, cộng guard breadth-decoupling (`BREADTH_SOURCE="pit"`). Câu hỏi bắt buộc trả
lời: các ngày H4 fire có **TRÙNG** ngày cap hiện có đã active không? Nếu trùng phần lớn thì H4
là dư thừa, không phải bổ sung — đó là kết luận NO-GO dù (a)(b) có pass.

---

## BƯỚC 2 — H5: proxy sinh thái retail (AMH G4)

### 2.1 Nguồn
E (như trên), cột `local_individual_net_bn`, `proprietary_net_bn`, `local_institutional_net_bn`,
`foreign_matched_net_bn`, `foreign_deal_net_bn`. **Chỉ từ 2016-04** (trước đó thiếu 2/5 nhóm).
Loại giai đoạn `provisional` 2026-09-03→09-14. Loại đoạn tự doanh trống 2022-03-03→2022-05-16
khỏi series `retail_net_share` (thiếu 1 trong 5 nhóm ⇒ mẫu số sai).
Trục breadth PIT: `tav2_mike.universe_pit` theo quy ước 08-22 (tercile).

### 2.2 Hai series (khai TRƯỚC)
- `retail_net_share_m` = trung bình THÁNG của `|local_individual_net_bn| / Σ|5 nhóm|` theo ngày.
- `retail_capitulation_t` = z-score 20 phiên của `local_individual_net_bn`
  (`(S20 − mean(S20 rolling 250)) / SD(S20 rolling 250)`), âm = cá nhân bán ròng cực đoan.

**Loại ngày thoả thuận lớn** khỏi CẢ HAI series: bỏ ngày có `|foreign_deal_net_bn| ≥ 1.000` tỷ
(bẫy #3 registry: phía bán lô thoả thuận bị gán cho cá nhân, vd 2018-05-18 cá nhân −30.767 tỷ).
Ngưỡng 1.000 tỷ khai TRƯỚC.

**Bẫy mang theo:** 5 nhóm không cộng về 0 (|tổng| median 64→300 tỷ) ⇒ mẫu số `Σ|5 nhóm|` là
thước đo QUY MÔ hoạt động, KHÔNG phải tổng đại số; cấm suy nhóm thứ 5 bằng phần dư. Tổ chức
trong nước có thể đã gồm tự doanh ⇒ cấm cộng 2 cột đó.

### 2.3 Test — CHỈ như BIẾN ĐIỀU KIỆN
Hướng (ecology làm tín hiệu mua/bán) đã **REFUTED 2026-07-13** ⇒ **KHÔNG test lại hướng**.
- IC (Spearman) của `mom_200` và của value (`1/PE`) với forward return, tính theo tercile của
  `retail_net_share_m`, đặt CẠNH trục mặc định breadth-tercile PIT.
- Tách IS **2016-04→2019-12** / OOS **2020-01→2026-08**.
- N khai theo quy tắc: IC cross-sectional per-day (số phiên), NHƯNG số **tercile-tháng độc lập**
  mới là N của kết luận điều kiện hoá — báo cả hai, và block-bootstrap theo THÁNG (B≥1000).
- Tiêu chí PASS khai trước: chênh IC giữa tercile cao và thấp phải (i) cùng DẤU ở IS và OOS,
  (ii) CI 95% bootstrap không chứa 0 ở OOS, (iii) có dạng đơn điệu qua 3 tercile. Thiếu 1 trong
  3 ⇒ "không đủ bằng chứng", không phải "có hiệu ứng yếu".

### 2.4 `retail_capitulation` làm ứng viên điều kiện 3 của margin Loại-2
- Kiểm: có cực trị (z ≤ −2) tại **2020-03** và **2022-10/11** không.
- Đếm **cực trị giả** = sự kiện z ≤ −2 (debounce 60 ngày lịch như §1.4) KHÔNG nằm trong vòng
  ±1 tháng của một đáy thị trường (VNINDEX giảm ≥20% từ đỉnh 1 năm trước đó).
- PASS khai trước: bắt được CẢ 2020-03 VÀ 2022-10/11, và ≤ 2 cực trị giả trên toàn 2016-2026.

### 2.5 Ràng buộc kết luận
Nguồn **KHÔNG có nối tiếp sau 28/09/2026**. Nếu H5 có giá trị ⇒ đó là bằng chứng để **mở lại câu
hỏi mua gói rẻ nhất**, KHÔNG phải để wire. Nói thẳng câu này trong finding.

---

## Cấu hình môi trường
- Interpreter: `/home/trido/thanhdt/wc_venv/bin/python` (`$DNA_PYEXE`, pandas 3.0.2, numpy 2.4.4,
  duckdb 1.5.4). KHÔNG dùng `python3` hệ thống.
- Snapshot BQ local: `data/bq_cache/` (ticker parquet theo năm).
- Không sửa bất kỳ file production nào; `git status` phải sạch trên file production.
