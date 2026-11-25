# Dự báo earnings quý ↔ tâm-giá, vòng J3: vá theo quant-skeptic + chu kỳ hàng hoá/ngành (job Taylor_20261125_014736, 25/11/2026)

Chỉ nghiên cứu. Chưa qua quant-skeptic J3, không tự xưng CONFIRMED. Không sửa production, không wire, không merge, không email.
Bản J2 giữ nguyên ở `REPORT_J2.md` (+ `MD5SUMS_J2`). Thiết kế: `PRELOCK.md` (J2) + `PRELOCK_J3_CYCLE.md`. Addendum commit `e7d39ee57`, trước mọi dòng code chu kỳ.
Commit theo bước: vá J2 `1304ad1dd` → PRELOCK chu kỳ `e7d39ee57` → A'/B' `3468caa42` → C' `38fe36954`.
Panel định giá: V3.1 (`in_snapshot_v31/vp2.parquet` md5 `3b89e78d…`, đã vá vốn hoá ảo).

## Kết luận (đọc trước)
1. **KL1 J2 viết lại (đúng hơn và hẹp hơn):** quan hệ "gap tâm-giá ↔ sai số earnings của D0" (B1) **gần như là hằng đẳng thức**.
   Có một null không dùng giá: `nlv = log vb(ROE 5 năm) − log vb(ROE TTM)`, tức "D0 lạc quan bao nhiêu so với earnings hiện tại".
   Null này cho IC với sai số tích luỹ −0,892 (IS) / −0,865 (OOS); gap chỉ cho −0,453 / −0,302.
   Kiểm soát nlv xong, gap chỉ còn +0,013 / +0,049, sai dấu và gần 0. R² hạng của gap: 0,21 (IS) / 0,095 (OOS).
   ⇒ Bỏ chữ "phần lớn". Câu đúng là: *D0 lệch giá chủ yếu vì ROE 5 năm ≠ ROE hiện tại. Điều này đọc được thẳng từ báo cáo tài chính, không cần giá.*
2. **Giá có thêm một phần thông tin, nhưng hẹp:** gap có báo trước sai số TƯƠNG LAI của chính D0 (u4), kể cả sau 4 biến kiểm soát và −ROE_ttm: −0,132 IS / −0,108 OOS, CI loại 0, 6/6 năm âm.
   Gap **không** báo trước surprise thật so với dự báo tốt: với ENS, sau −ROE_ttm còn −0,116 IS / −0,009 OOS (OOS null).
3. **KL3 J2 viết lại:** giá có trôi về phía tâm giữa 2 kỳ công bố ở OOS. Sau E/P và −ROE_ttm còn +0,058 [+0,030; +0,088], 6/7 năm dương.
   Nhưng IS là −0,021, khác dấu ⇒ theo tiêu chí khoá thì chưa phải "thông tin". Quanh ngày công bố (±2 phiên) null ở cả hai era.
   Câu đúng: "không có hội tụ tập trung quanh ngày công bố; trôi giữa kỳ chỉ thấy ở OOS".
4. **Chu kỳ, phần mô tả (A'):** thiên lệch earnings ngầm của D0 **đổi dấu theo pha chu kỳ, rất nhất quán**.
   - Ở đỉnh (ROE TTM > trung vị 8 năm + 0,5 sd): D0 đánh giá THẤP earnings quý kế. Dương ở 5–7/7 năm.
   - Ở đáy: D0 đánh giá CAO. Âm ở **6/6 năm IS và 7/7 năm OOS, ở mọi tercile độ chu kỳ**.
   - Biên độ ở đáy gấp ~2 lần ở đỉnh. Đây chính là nguồn của thiên lệch lạc quan −0,42%/quý ở J2.
   - Nhóm chu kỳ cao (CYC_HI) chiếm 25% sự kiện nhưng **44% tổng |sai số| D0** (OOS).
   - Cùng lúc, ở đỉnh của CYC_HI, các dự báo ngoại suy (ENS, naive) **tệ hơn D0**. MdAE OOS: ENS 3,63%, naive 3,25%, D0 2,62%. ENS lạc quan −2,0%/quý vì đỉnh tự hồi.
   ⇒ Giả thuyết của user đúng về MÔ TẢ. Lưu ý: dấu đổi theo pha phần lớn là cơ học, vì lợi nhuận bám pha hiện tại còn D0 neo vào trung bình quá khứ. Đây không phải thông tin mới.
5. **Chu kỳ, phần mô hình hoá dự báo (B'): NO-GO theo tiêu chí khoá.**
   - ENS có tốc độ hồi quy theo pha (ENSph) so với ENS, h = 1: R 1,004 (IS) / 1,000 (OOS).
   - Yếu tố giá hàng hoá World Bank (COMMF, β fit trên IS) làm dự báo nhóm hàng hoá **tệ hơn naive ở OOS**: R 1,336, chỉ 1/7 năm tốt hơn. Ghép vào ENS (ENScm) thì OOS 1,035.
   - ROE xuyên chu kỳ 8 năm (D0tc8) không tốt hơn ROE 5 năm: 1,041 / 1,041.
   - Giá hàng hoá giải thích được hướng thay đổi lợi nhuận (IC ~0,45, đã có từ `commodity_cycle_te_20261026`). Nhưng nó không cải thiện mức dự báo quý so với ENS.
6. **Chu kỳ, phần tâm định giá (C'):** không biến thể nào đạt tiêu chí khoá. Có một mô tả đáng ghi:
   - Ở mã chu kỳ (COMM + CYC_HI), tâm theo earnings chuẩn hoá (D0) xếp hạng lợi suất 36 tháng **tốt hơn E/P ở 7/10 năm**. IS rất mạnh: IC36 0,220 so với 0,035.
   - Ở mã không chu kỳ thì ngược hẳn: E/P thắng D0 **10/10 năm**.
   - Nhưng ở mã chu kỳ, D0 thua E/P trong 2021–2023. DSR 0,54 < 0,95.
   - C4 (ROE 8 năm) trong nhóm chu kỳ: OOS +0,076 so với D0 (4/4 năm), vượt E/P (0,223 so với 0,169). Nhưng IS −0,045 (1/6 năm), PBO 0,52 ⇒ **trượt, không đọc như cải thiện**.
   ⇒ Hàm ý đáng đem ra skeptic: **chọn neo định giá theo độ chu kỳ** (chu kỳ → earnings chuẩn hoá; không chu kỳ → E/P). Đây là giả thuyết MÔ TẢ, chưa pre-register, chưa có OOS mới.

## Bảng delta J2 → J3
| Mục | J2 | J3 | Nguồn |
|---|---|---|---|
| B1 IC(gap, cu) IS / OOS | −0,453 / −0,302 | không đổi (V3.1 không đổi MC_rel ngày công bố trên mẫu B) | `out_J3/B_results.csv` |
| Null không giá −ROE_ttm → cu | chưa có | −0,436 / −0,507 | như trên |
| Null không giá nlv → cu | chưa có | **−0,892 / −0,865** | như trên |
| Gap tăng thêm trên nlv | chưa có | +0,013 [−0,004; +0,030] / +0,049 [+0,023; +0,074] | như trên |
| Gap tăng thêm trên −ROE_ttm + 4 kiểm soát | chưa có | −0,062 / −0,055 (1/5, 1/7 năm dương) | như trên |
| B1_ctrlEP (J2 có chạy, không báo) | −0,679 / −0,591 | báo lại: kiểm soát E/P làm gap MẠNH hơn, vì gap = log vb + log(E/MC) | như trên |
| R² hạng gap theo cu (TB theo quý) | không báo | 0,211 / 0,095 | cột `R2rank_q_mean` |
| B2 gap → u4, sau 4 kiểm soát + −ROE_ttm | chưa có | −0,132 / −0,108 (CI loại 0) | như trên |
| B3 gap → r_pre, sau E/P + −ROE_ttm | chưa có | −0,021 / **+0,058** [+0,030; +0,088] | như trên |
| Đa kiểm định | CI95 thô | thêm p bootstrap + BH theo era (44 test có p/era); kết luận chính không đổi | cột `q_BH` |
| C2 IC36 OOS (route tĩnh, mc_old) | 0,230 | 0,227 (V3.1 + route PIT); route tĩnh trên V3.1: 0,232 ⇒ route tĩnh làm phồng +0,005 | `out_J3C/`, `out_J3C_static/` |
| C2 − D0 OOS / IS | +0,022 CI99,17 [+0,011; +0,046] / +0,001 | +0,017, **4/4 năm dương** / −0,000, 4/6 năm | `out_J3C/C_diff.csv` |
| C2 − E/P OOS | −0,026 | −0,031, 1/4 năm dương | như trên |
| C2 IC phần dư 5 biến (V3.1) OOS | — | 0,039 (D0 0,086) ⇒ C2 làm GIẢM thông tin riêng | `out_J3C/metrics2_C.csv` |
| PBO {D0, C1, C2, C3} | 0,187 | 0,242 | `out_J3C/C_pbo.json` |

## A. Vá J2: B (gap ↔ sai số), 44 test có p/era, BH
Toàn bảng ở `out_J3/B_results.csv` (cột `IC`, `ci95_*`, `p_boot`, `q_BH`, `R2rank_q_mean`, `n_pos_yr`). Các test then chốt:
| Test | IS | OOS | Đọc |
|---|---|---|---|
| gap → cu | −0,453 | −0,302 | J2 |
| nlv → cu (không giá) | −0,892 | −0,865 | null mạnh hơn gap gần 2 lần |
| gap \| nlv → cu | +0,013 | +0,049 | gap không thêm gì |
| gap \| −ROE_ttm, 4 kiểm soát → cu | −0,062 | −0,055 | phần còn lại nhỏ |
| gap → u4 (sai số D0 4 quý tới) | −0,519 | −0,357 | |
| nlv → u4 | −0,591 | −0,493 | |
| gap \| nlv → u4 | −0,249 | −0,167 | giá biết thêm về việc D0 sẽ còn sai |
| gap \| −ROE_ttm → eps4 (surprise so với ENS) | −0,116 | −0,009 [−0,040; +0,036] | OOS null |
| gap \| E/P, −ROE_ttm → r_pre | −0,021 [−0,043; +0,002] | +0,058 [+0,030; +0,088] | khác dấu giữa 2 era |
- Hạn chế vintage/Q4 (skeptic (6)): `NP_P1(q) = NP_P0(q−1)` ở 99,3% chỉ chứng minh nhất quán **trong 1 vintage**.
  Q4 có K ≈ 30 ngày sau cuối quý, nên số Q4 trong vintage này có thể đã là số kiểm toán, không phải số công bố đầu tiên.
  Không đo được ⇒ sai số A ở quý Q4 có thể bị đánh giá thấp. Áp cho cả J2 và J3.

## B. Chu kỳ (PRELOCK_J3_CYCLE)
**Nguồn:** chỉ World Bank CMO tháng (5 họ: cao su RSS3, dầu thô TB, urê, DAP, đường thế giới; biết sau cuối tháng 35 ngày; 1 vintage 03/11/2026).
Các nguồn bị loại kèm lý do nằm ở PRELOCK §0: TE và sunsirs (không PIT, không phủ IS), BDI và heo (chuỗi ngắn), xút (tổng hợp, không phải số đo).
Thép, thuỷ sản, chăn nuôi, vận tải, KCN, xi măng **không có chuỗi giá PIT phủ IS**. Các ngành này chỉ vào được qua độ chu kỳ tính từ chính LNST.
**Nhóm:**
- COMM: 20 mã của bản đồ đóng băng 2026-10-25. PRELOCK ghi "~19", số đúng là 20; 15 mã có trong mẫu IS, 19 mã trong OOS.
- FIN: route PIT ngân hàng, chứng khoán, bảo hiểm.
- CYC_HI / MID / LO: tercile sd ROE_ttm trong 32 quý (PIT).
- Pha: ROE_ttm so với trung vị 32 quý trước, ±0,5 sd.

### B.1 A' — sai số h = 1 theo nhóm × pha (`out_CY/A2_grp_phase.csv`; e > 0 = thực tế cao hơn dự báo)
| OOS | n | MdAE naive | MdAE ENS | MdAE D0 | thiên lệch ENS | thiên lệch D0 | năm D0 dương / âm |
|---|---|---|---|---|---|---|---|
| CYC_HI đỉnh | 569 | 3,25% | **3,63%** | 2,62% | −2,02% | +1,24% | 7 / 0 |
| CYC_HI giữa | 948 | 1,56% | 1,28% | 1,73% | −0,11% | −0,30% | 1 / 6 |
| CYC_HI đáy | 1.088 | 1,79% | 1,51% | **2,92%** | +0,37% | **−2,24%** | 0 / 7 |
| CYC_MID đỉnh / đáy | 552 / 1.219 | 1,89 / 1,04% | 1,77 / 0,95% | 1,63 / 1,73% | −0,76 / +0,09% | +0,68 / −1,40% | 6/1 · 0/7 |
| CYC_LO đỉnh / đáy | 608 / 838 | 0,96 / 0,68% | 0,87 / 0,55% | 0,82 / 1,09% | −0,22 / 0,00% | +0,24 / −0,87% | 6/1 · 0/7 |
| COMM đỉnh / đáy | 141 / 103 | 1,46 / 0,88% | 1,46 / 0,85% | 1,54 / 0,93% | −0,48 / +0,19% | +1,01 / −0,42% | 5/2 · 1/6 |
| FIN đỉnh / đáy | 555 / 309 | 1,25 / 1,21% | 1,13 / 0,94% | 1,40 / 1,31% | −0,03 / +0,43% | +0,93 / −0,91% | 7/0 · 0/7 |
- IS cùng dạng: CYC_HI đỉnh +1,59%, 5/1 năm; đáy −2,75%, 0/6. COMM IS chỉ có pha đáy và giữa đủ 30 sự kiện; đáy −2,99%, 0/6.
- Tỉ trọng tổng |sai số D0| (OOS): CYC_HI 44,4% trên 24,9% số sự kiện; COMM 2,6% trên 4,2%; CYC_LO 9,7% trên 20,3%.
  IS: CYC_HI 31,7% trên 20,3% (`out_CY/A2_grp.csv`).
- COMM theo pha giá hàng hoá (`A2_comm.csv`): IS pha giá THẤP, D0 −3,13%/quý (161 sự kiện). OOS nhỏ (−0,43%).
  Thiên lệch IS của COMM nặng nhất ở DAP (−3,3%) và dầu (−2,5%). OOS gần 0 ở mọi họ.
- **N thật:** dấu theo pha đồng nhất ở 6–7/7 năm và 3 tercile. Nhưng các pha tương quan chéo theo năm, và mẫu chỉ có ~2–3 chu kỳ lớn ⇒ đây là mô tả, không phải xác suất.

### B.2 B' — 5 dự báo có chu kỳ, h = 1 (`out_CY/B2_pairs.csv`; R = trung bình nhân tỉ lệ MdAE theo quý; "năm tốt" = số năm R < 1)
| So sánh | ALL IS | ALL OOS | CYC_HI OOS | COMM IS | COMM OOS |
|---|---|---|---|---|---|
| ENSph / ENS | 1,004 (1/6) | 1,000 (4/7) | 0,995 (3/7) | 1,027 (0/6) | 1,011 (2/7) |
| MRph / MR | 1,015 | 1,009 (0/7) | 0,997 | 1,044 | 0,993 (5/7) |
| D0tc8 / D0imp | 1,041 | 1,041 | 1,091 | 1,281 | 1,214 |
| COMMF / naive | — | — | — | 0,959 (3/6) | **1,336 (1/7)** |
| ENScm / ENS | 0,998 | 0,998 | 0,995 | 0,995 | 1,035 (2/7) |
- Tiêu chí khoá "R < 1 cả 2 era và ≥ 5/7 năm OOS": **không biến thể nào đạt**. Ở h = 4, ENScm/ENS trong COMM+CYC_HI OOS là 0,968 (4/6), nhưng IS 1,032 ⇒ trượt.
- φ fit trên IS (`out_CY/cycle_fit.json`; 3.851 gốc): HI-đáy 0,385 (hồi nhanh), HI-đỉnh 0,692, ba ô khác chạm trần 1.
  ⇒ ROE ở đáy của mã chu kỳ cao hồi về trung bình nhanh, nhưng nhanh đến mức D0 (giả định hồi tức thì) vẫn đánh giá cao quý kế.
- β COMMF (IS, 17 mã): 0,160 · 0,134 · 0,049 · −0,124 (h = 1..4). Đổi dấu ở h = 4, và độ lớn không chuyển sang OOS.
- COMM dùng ngưỡng ≥ 8 sự kiện/quý (các nhóm khác ≥ 20), vì COMM chỉ có ~15 sự kiện/quý. Ngưỡng chọn khi kết quả COMM đầu tiên bị lọc rỗng, trước khi xem số COMM; không có trong PRELOCK.

### B.3 C' — tâm D0 chu kỳ-hoá (`out_CYC_{ALL,CYC,REST}/`, code đo `d_metrics2.py` V3.1)
| IC36 IS / OOS | D0 | C2 | C4 (ROE 8 năm) | C5 (theo pha) | E/P |
|---|---|---|---|---|---|
| ALL | 0,139 / 0,210 | 0,138 / 0,227 | 0,113 / 0,217 | 0,121 / 0,216 | 0,130 / **0,258** |
| CYC (COMM + CYC_HI, 25,7% dòng) | **0,220** / 0,147 | 0,196 / 0,134 | 0,175 / **0,223** | 0,122 / 0,157 | 0,035 / 0,169 |
| REST | 0,120 / 0,234 | 0,128 / 0,260 | 0,098 / 0,217 | 0,126 / 0,235 | **0,162 / 0,292** |
- CYC và REST: IC và chuẩn EW được tính TRONG tập con, bằng cách che `in_universe`. Selfcheck đã tính lại D0 CYC OOS 0,1474 bằng vòng lặp tự viết và khớp.
- Tiêu chí khoá (≥ 4/6 năm IS ∧ ≥ 3/4 năm OOS ∧ ≥ E/P): C4 trên CYC đạt OOS 4/4 và vượt E/P, nhưng **IS 1/6** ⇒ trượt. C5 trượt. C2 trên REST đạt 4/6 và 4/4 nhưng < E/P (0/4 năm) ⇒ trượt.
- U-hit và cảnh báo đắt (O_right_rel) so với D0: phía TỆ hơn quá 5pp có 2 ca. C2 trên CYC: U-hit IS −6,6pp. C5 trên CYC: cảnh báo đắt IS −5,1pp. Phía tốt hơn: C5 trên CYC có U-hit OOS +22,9pp, nhưng IC trượt.
- DSR (chuỗi Δ theo năm 2014–2023, N thử = 7, `out_CYC_ALL/dsr_cycle.json`):
  - C2−D0: ALL 0,33, REST 0,74.
  - C4−D0 CYC: 0,11.
  - **D0−E/P trong CYC: 0,54, 7/10 năm**. D0−E/P trong REST: 0,00, 0/10 năm.
  - Tất cả < 0,95.
- PBO {D0, C2, C4, C5}: ALL 0,214 · **CYC 0,520** · REST 0,159.

## Selfcheck độc lập (`calc/i_selfcheck_j3.py` → `out_CY/selfcheck_{noTZ,ICT}.txt`)
4/4 PASS. Mỗi số tính lại bằng một đường code khác:
- IC(nlv, cu) OOS: tính bằng scipy spearmanr theo quý, ra −0,8651.
- Thiên lệch D0 ở CYC_HI đỉnh / đáy OOS: tính từ `fc.parquet` của b_forecast thay vì `fc_cy`, ra +0,0124 / −0,0224.
- IC36 D0 trong CYC OOS: vòng lặp tháng quý tự viết, ra 0,1474.
- Ngoài ra, `f_cycle.py` tính lại SRW/ENS/D0imp, lệch tối đa 0,0 so với `b_forecast.py`; `g_cycle_update.py` tái lập D0, lệch tối đa 0,0.
Hai lần chạy (`env -u TZ PYTHONHASHSEED=0` và `TZ=Asia/Ho_Chi_Minh PYTHONHASHSEED=12345`) cho cùng md5 `e2b294d27600fd9e91facde1e5f06492`.

## Hạn chế (cộng dồn J2)
- 1 vintage `ticker_financial` (xem mục A, Q4). Mã huỷ niêm yết vắng ở A/B (survivorship).
- WB CMO chỉ có 1 vintage. Bản đồ COMM theo mô tả kinh doanh HIỆN TẠI: có nguy cơ hindsight nhẹ về mô hình kinh doanh, không phải về kết quả.
- Pha và độ chu kỳ chỉ dựa trên LNST của chính mã. Không có chỉ số ngành độc lập cho thép, thuỷ sản, KCN, xi măng.
- Kiểm soát `nlv` dùng cùng hàm rim_vb với D0. Đó là điểm mấu chốt: tách "phần do cấu trúc mô hình" khỏi "phần do giá".
- OOS của C chỉ có 15 mốc as-of / 4 năm, tức ~1,3 cửa sổ 36 tháng độc lập. Mọi kết luận C là yếu theo cấu trúc.

## Hàm ý (đề xuất, chưa quyết)
- Hiển thị kèm tâm D0 một dòng chẩn đoán: "pha chu kỳ (đỉnh/giữa/đáy) + earnings ngầm so với ENS so với 4 quý thực". Ở đáy của mã chu kỳ, D0 gần như chắc chắn quá lạc quan về quý kế (7/7 năm). Display-only.
- Không wire C2/C4/C5. Không dùng yếu tố giá hàng hoá WB để dự báo mức LNST quý.
- Ứng viên PREREG mới, nếu user muốn đi tiếp: "neo theo độ chu kỳ" (CYC → D0, REST → E/P), khoá trước, kiểm bằng OOS tương lai 2024+. Hiện mới là mô tả, DSR 0,54.

## Tái lập
```
cd agents/Taylor/research/dcf_earnings_forecast_20261125d; PY=/home/trido/thanhdt/wc_venv/bin/python
export SNAP_DIR=$PWD/in_snapshot_v31 OUT_DIR=$PWD/out_J3; (cd calc && $PY a_events.py && $PY b_forecast.py && $PY c_gap.py)
VARIANTS=C1,C2,C3 bash run_j3.sh out_J3C D0,C1,C2,C3,EP; ROUTE_STATIC=1 bash run_j3.sh out_J3C_static D0,C2
(cd calc && $PY f_cycle.py && $PY g_cycle_update.py) && bash run_cyc.sh && (cd calc && $PY h_dsr.py && $PY i_selfcheck_j3.py)
```
Cần `in_snapshot_v31/vp2.parquet` (copy từ `wt-dcf-v3-20261125/.../out_F/`) và `in_cycle/CMO-Historical-Data-Monthly.xlsx` (copy từ `data/_wb_cache/`). Parquet và xlsx bị gitignore; md5 ở `MD5SUMS`.
