# Dòng nghiên cứu dự báo earnings quý ↔ tâm DCF-VN: kết luận cuối J1→J4 (+ J3.1 sửa chữ, chạy lại C trên V3.2)

Job J3.1 `Taylor_20261125_022916`, 25/11/2026. Chỉ nghiên cứu. **Không khuyến nghị wire.** Không merge, không email.
J3.1 chưa qua quant-skeptic. J4 cũng chưa qua quant-skeptic.
Nhánh `session/Taylor_20261125_011012`. Thư mục của từng vòng (`d/e/f` = `dcf_earnings_forecast_20261125{d,e,f}`):
- J1 = PRELOCK + A, `bc94665f1`;
- J2 = B + C, `cec37fa11` (`d/REPORT_J2.md`);
- J3 = `1d74c6474` (`d/REPORT.md`);
- J4 = `8e467efab` (`e/REPORT.md`);
- J3.1 = thư mục này.

## Trang 1: kết luận cuối dòng nghiên cứu

### Đã làm gì
- **J1:** dự báo LNST quý bằng 8 họ mô hình, có ngày công bố thật (PIT), so với naive mùa vụ.
- **J2:**
  - B: hỏi gap (tâm D0 so với vốn hoá) có phải là sai số earnings hay không.
  - C: vòng cập nhật tâm D0 (C1–C3).
- **J3:** vá J2 theo skeptic, thêm null không dùng giá (nroe, nlv); phân tích chu kỳ (World Bank CMO + độ chu kỳ tính từ LNST).
- **J4 (hướng C):** chu kỳ ngành từ BCTC, trung vị ICB4 loại chính mã (LOO); vá mc ảo, ra panel V3.2.
- **J3.1:** sửa chữ KL2/KL4/KL6 theo skeptic J3; chạy lại phần C của J2/J3 trên V3.2.

### Cái gì ĐÚNG (đứng được qua skeptic, hoặc tái lập khớp)
1. **D0 lạc quan có hệ thống về earnings quý kế.**
   - Earnings ngầm của D0 (`roe_tc5·E/4`) dự báo kém naive mùa vụ. R = 1,27 ở IS và 1,18 ở OOS.
   - Thiên lệch trung vị OOS là −0,42%/quý (J1).
   - Phần A tái lập khớp (skeptic J2).
2. **Một ensemble đơn giản (ENS) hơn naive khoảng 10–12% ở quý kế, cả hai era** (R 0,903 IS / 0,876 OOS).
   - Từ h = 3 trở đi không hơn nữa.
   - ENS là công cụ dự báo h = 1–2, không phải nguồn alpha.
3. **Gap của D0 chủ yếu là "ROE 5 năm ≠ ROE hiện tại"** (KL1 đã viết lại ở J3).
   - Null không dùng giá `nlv` cho IC với sai số tích luỹ −0,892 / −0,865.
   - Gap kiểm soát theo nlv chỉ còn +0,013 / +0,049.
   - Caveat skeptic J3: `nlv` dùng cùng `rim_vb` với D0, nên nó **không phải null độc lập**. Nó tách phần do cấu trúc mô hình, không chứng minh "giá không có thông tin".
4. **Giá có thêm một phần thông tin về việc D0 sẽ còn sai, nhưng nhỏ** (KL2 sửa ở J3.1, đã đo lại).
   - Độ lớn đúng sau khi kiểm soát đủ (ep, size, roe_tc5, mom, nroe, nlv) là **−0,055 (IS) / −0,054 (OOS)**, CI loại 0. Không phải −0,132 / −0,108.
   - Con số cũ −0,132 / −0,108 chỉ kiểm soát nroe; thêm nlv thì độ lớn giảm hơn một nửa (`out_delta/kl2_u4_ctrl.csv`).
   - Với surprise thật so với ENS, OOS là null.
5. **Không có hội tụ giá về tâm tập trung quanh ngày công bố** (±2 phiên, null cả hai era). Trôi giữa kỳ chỉ thấy ở OOS, IS khác dấu.

### Cái gì BỊ BÁC (skeptic REFUTED, đã sửa chữ)
- **J2 KL1 "gap phần lớn là sai số earnings":** gần như là hằng đẳng thức kế toán (gap = log vb + log E/MC), không phải phát hiện. Đã thay bằng KL1 ở mục ĐÚNG.
- **J2 KL3 "không hội tụ":** viết quá rộng. B3 OOS tồn tại; chỉ null trong ±2 phiên.
- **J3 KL4, chu kỳ "D0 lạc quan ở đáy / bi quan ở đỉnh" (sửa ở J3.1):**
  - Đây chỉ là **đại số persistence** của ROE_ttm − ROE5y. Lợi nhuận bám pha hiện tại, còn D0 neo vào trung bình quá khứ, nên dấu đổi theo pha là cơ học.
  - Skeptic J3: kiểm soát persistence xong thì phần dư hết đổi dấu. Chưa đo lại trong J3.1.
  - Câu "CYC_HI = 25% sự kiện nhưng 44% |sai số D0|" đúng **theo định nghĩa**: độ chu kỳ chính là SD của ROE. Không phải bằng chứng riêng về chu kỳ.
  - ⇒ A' chỉ là mô tả cơ chế đã biết. Đừng trích như "phát hiện về chu kỳ".
- **J3 KL6, "neo theo độ chu kỳ" (chu kỳ → D0, không chu kỳ → E/P) (sửa ở J3.1):**
  - Chỉ đúng ở IS: D0 > E/P 6/6 năm.
  - Ở OOS, trong nhóm chu kỳ, **E/P ≥ D0**: IC36 0,1665 so với 0,1468 (V3.2), D0 > E/P chỉ 1/4 năm. Trong nhóm còn lại, E/P thắng 10/10 năm.
  - Giả thuyết lập **sau khi thấy số**. N hiệu dụng khoảng 3–4 (2–3 chu kỳ lớn, khoảng 1,3 cửa sổ 36 tháng OOS độc lập).
  - ⇒ **Không phải ứng viên PREREG.** Rút lại khỏi phần "hàm ý" của J3.

### Cái gì NO-GO (theo tiêu chí khoá trước)
- **Vòng cập nhật tâm D0, C1–C5 (J2/J3; J3.1 chạy lại trên V3.2):** không biến thể nào ≥ E/P.
  C2 OOS 0,226 so với E/P 0,257, chỉ 1/4 năm. C2 cũng không làm tăng IC phần dư.
- **Dự báo có chu kỳ (J3 B'):**
  - ENS theo pha so với ENS: 1,004 / 1,000.
  - Yếu tố giá hàng hoá WB so với naive, OOS: 1,336.
  - ROE 8 năm thay ROE 5 năm: 1,041.
- **Chu kỳ ngành LOO, M1–M5 (J4):**
  - Tất cả thua E/P khoảng −0,036 đến −0,039 IC36 OOS.
  - M4 hơn null P1 +0,0019, 3/4 năm, DSR 0,765. Độ lớn khoảng 1% IC36, không dùng được.
  - **Caveat J4, phải đọc kèm:**
    - Bug chỉ số LOO được sửa **sau khi đã thấy số**. Bản lỗi cho NO_NEW = true; bản sửa cho NO_NEW = false, nghĩa là tiêu chí dừng bị lật.
    - Bản sửa là sửa lỗi cơ học (0/300 dòng lệch). Nhưng thứ tự "thấy số rồi mới sửa" làm trạng thái tiêu chí không còn sạch.
    - Có **3 lựa chọn chưa ghi trong PRELOCK_J4**: mẫu fit chỉ lấy `in_universe`; S1 dùng mức trong M1, dùng hạng ở M2–M5; capex lấy `|capex_ttm|`.
  - Kết luận thực dụng giữ nguyên dù tiêu chí lật: **không có gì mới đủ dùng.**
- **Null persistence P1 (J4):** dự báo ROE tốt hơn D0 (R² OOS 0,305 so với 0,217), nhưng **xoá phần thông tin xếp hạng riêng của D0** (IC phần dư −0,002 so với +0,089). Không thay tâm D0 bằng P1.

### Dùng được gì cho DCF-VN (thực dụng, display-only, không wire)
- **Panel V3.2 (vá mc ảo)** thay V3.1 cho mọi lần chạy lại nhánh DCF-VN, md5 `a24678ff…`. Đây là sửa dữ liệu, độc lập với các kết quả trên.
  Ảnh hưởng đo được: |ΔIC36| ≤ 0,006, số năm dương không đổi (bảng dưới).
- **Một dòng chẩn đoán cạnh tâm D0:** "ROE TTM so với ROE 5 năm" (nlv). Đó chính là phần lớn lý do D0 lệch giá, đọc thẳng từ BCTC.
  Khi ROE TTM < ROE 5 năm, D0 gần như chắc chắn quá lạc quan về quý kế. Đây là đại số persistence (KL4 đã sửa), không phải alpha.
- **ENS h = 1** nếu cần một con số "LNST quý kế" để hiển thị: hơn naive khoảng 10–12%, sai số trung vị vẫn khoảng 1,06% vốn chủ/quý.
- **E/P vẫn là thước so sánh phải vượt**, ở mọi tập con OOS kể cả mã chu kỳ. Mô hình hoá earnings thêm không vượt được E/P trên dữ liệu PIT hiện có.
- Muốn đi tiếp về chu kỳ thì phải có chuỗi giá/tồn kho ngành PIT phủ từ 2014 (việc thu thập dữ liệu của Winston), không phải thêm biến thể mô hình.

---

## J3.1 bước 2: chạy lại C (J2) và C' (J3) trên panel V3.2
- Đầu vào: `in/vp2.parquet` = `e/out_panel/vp2.parquet` (md5 `a24678ff0a8b2166ac3328624cc0cd13`).
- Code đo: `d/in_snapshot_v31/d_metrics2.py` nguyên văn. `calc/{d_update,e_cdiff,g_cycle_update,h_dsr}.py` chép từ `d/calc`, chỉ đổi đường dẫn (xem `diff`).
- Tái dùng events và đặc trưng chu kỳ từ J3 (`d/out_J3/events.parquet`, `d/out_CY/cyc_features.parquet`). Chúng tính từ earnings/ROE, không phụ thuộc mc (`V_D0` = exp(lv_D0)·mc là bất biến theo mc).
- `D0_recompute_maxabs` = 3,8e−15, tức lv_D0 của V3.2 tái lập đúng.

Nguồn: IC36 (scope ALL) ở `out_delta/delta_ic36.csv`; cặp so sánh ở `out_delta/delta_pairs.csv`; PBO/DSR ở `out_delta/delta_pbo_dsr.json`.

| IC36 | J3 (V3.1) IS / OOS | J3.1 (V3.2) IS / OOS |
|---|---|---|
| ALL D0 | 0,1388 / 0,2102 | 0,1373 / 0,2090 |
| ALL C2 | 0,1385 / 0,2274 | 0,1360 / 0,2260 |
| ALL C3 (ENS 4 quý) | 0,1225 / 0,2042 | 0,1217 / 0,2029 |
| ALL C4 / C5 | 0,1129 / 0,2168 · 0,1211 / 0,2157 | 0,1107 / 0,2156 · 0,1192 / 0,2144 |
| ALL E/P | 0,1303 / 0,2582 | 0,1285 / 0,2566 |
| CYC D0 | 0,2196 / 0,1474 | 0,2174 / 0,1468 |
| CYC C4 | 0,1748 / 0,2229 | 0,1702 / 0,2202 |
| CYC E/P | 0,0353 / 0,1687 | 0,0343 / 0,1665 |
| REST D0 / E/P | 0,1198 / 0,2338 · 0,1623 / 0,2923 | 0,1184 / 0,2324 · 0,1603 / 0,2909 |

| Cặp so sánh (ΔIC36, số năm dương) | J3 | J3.1 |
|---|---|---|
| ALL C2 − D0, OOS | +0,0172 (4/4) | +0,0169 (4/4) |
| ALL C2 − E/P, OOS | −0,0308 (1/4) | −0,0307 (1/4) |
| CYC C4 − D0, IS / OOS | −0,0448 (1/6) / +0,0755 (4/4) | −0,0473 (1/6) / +0,0734 (4/4) |
| CYC D0 − E/P theo năm (DSR) | +0,0947, 7/10, DSR 0,535 | +0,0945, 7/10, DSR 0,538 |
| REST C2 − D0, OOS | +0,0262 (4/4) | +0,0258 (4/4) |
| PBO ALL / CYC / REST | 0,214 / 0,520 / 0,159 | 0,238 / 0,504 / 0,163 |
| PBO {D0, C1, C2, C3} | 0,242 | 0,258 |

- **Mọi ΔIC36 nằm trong [−0,006; 0]. Không cặp nào đổi số năm dương. Không kết luận nào của J3 đổi** (tiêu chí khoá vẫn trượt như cũ).
- D0 − E/P trong CYC theo năm: 2014–2019 đều dương; 2020 +0,251; 2021 −0,051; 2022 −0,041; 2023 −0,319. OOS chỉ 1/4 năm, là cơ sở của KL6 đã sửa.
- Thay đổi lớn nhất là IC phần dư 5 biến của **E/P**: ALL OOS −0,149 → −0,093; REST OOS −0,015 → −0,066.
  Lý do: biến kiểm soát quy mô dùng `log mc`, và mc vừa được vá. Các mô hình D0/C* gần như không đổi (lệch ≤ 0,006).

## Selfcheck (`calc/l_selfcheck_j31.py` → `out_delta/selfcheck_{noTZ,ICT}.txt`)
9/9 PASS. md5 `89c26dd6563b08a1de27f8c0f743e0ad` giống nhau dưới `env -u TZ PYTHONHASHSEED=0` và `TZ=Asia/Ho_Chi_Minh PYTHONHASHSEED=12345`. Các kiểm tra:
- md5 panel đúng V3.2. ACG 2022-03 mc = 9.018 tỷ trong panel đo (V3.1 là 13.978).
- IC36 OOS trong CYC của D0 / C4 / E/P tính lại bằng vòng lặp tháng quý + scipy: 0,1468 / 0,2202 / 0,1665, khớp artifact.
- KL6: E/P ≥ D0 trong CYC OOS. D0 > E/P: IS 6/6, OOS 1/4.
- KL2: phần dư hạng tính bằng phương trình chuẩn (khác đường lstsq của `k_kl2_check.py`), ra −0,0551 / −0,0541.
- Ngoài selfcheck: chạy lại toàn bộ `run_j31.sh` dưới TZ=ICT; 10/10 file kết quả (metrics2, C_diff, PBO, DSR) có md5 khớp bản chạy `env -u TZ`.

## Hạn chế (cộng dồn J1–J4)
- 1 vintage `ticker_financial`, nên số Q4 có thể đã là số kiểm toán. Mã huỷ niêm yết vắng ở A/B (survivorship).
- WB CMO 1 vintage. Bản đồ COMM và ICB theo phân loại hiện tại (hindsight nhẹ về mô hình kinh doanh).
- OOS của C: 15 mốc as-of / 4 năm, khoảng 1,3 cửa sổ 36 tháng độc lập ⇒ mọi kết luận về C là yếu theo cấu trúc.
- KL4 phần "residual hết đổi dấu" dựa trên đo của skeptic J3, chưa đo lại trong J3.1.

## Tái lập
```
cd agents/Taylor/research/dcf_earnings_forecast_20261125f
cp ../dcf_earnings_forecast_20261125e/out_panel/vp2.parquet in/   # parquet bị gitignore; md5 ở MD5SUMS
env -u TZ PYTHONHASHSEED=0 bash run_j31.sh
(cd calc && $PY j_delta_j31.py && $PY k_kl2_check.py && $PY l_selfcheck_j31.py)   # PY=/home/trido/thanhdt/wc_venv/bin/python
```
Cần `d/out_J3/{events,gapev}.parquet`, `d/out_CY/cyc_features.parquet` và `d/in_snapshot_v31/d_metrics2.py` (md5 ở `d/MD5SUMS`).
