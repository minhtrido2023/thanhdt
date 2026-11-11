**KẾT LUẬN: KHÔNG ĐẠT — chưa đủ bằng chứng; giữ nguyên V_dài, chưa thêm nền mới vào DD.** Theo tiêu chí khoá trước
(T1–T5, chân trời 3/6/12 tháng), **0/9 ứng viên** đạt mức "hiển thị được", 0/9 đạt mức "thay V_dài".
- Gần nhất là **D2 = CFO3 − (capex/doanh thu trung vị ngành) × doanh thu**: đạt T1–T4, trượt T5 (BH-FDR chỉ sống ở N12).
- **Giả thuyết của user đúng một nửa.**
  - Đúng: thị trường định giá chủ yếu theo LN. FCFE giải thích bội số kém hơn hẳn: R² chéo mã 0,12–0,21, so với 0,32–0,42 của LN.
  - Sai: thị trường KHÔNG thưởng chất lượng dòng tiền trong bội số. 2020–25, nhóm CFO/LN cao có P/E thấp hơn nhóm thấp
    khoảng 12% (log −0,127, CI [−0,27; +0,004]).
- Nền "LN kiểm định bằng CFO" (A1/A2) không hơn V_ngắn: IC IS âm ở 3/3 chân trời.
- Nền lai theo điểm chất lượng (E) KÉM hơn chính bản trộn hằng số của nó, nên điểm chất lượng không mang thông tin.

Job Taylor_20261111_095819 · 2026-11-11 · Taylor · CHỈ NGHIÊN CỨU (không sửa engine, skill, dd_price_zones, sổ pin).
PRELOCK.md md5 `ed2cea3fc1d584ae7febce619e6f463c`, khoá 17:05:03 ICT, trước mọi lần tính IC và hồi quy định giá (`out/prelock_md5.txt`).
Panel: dd_blend `1de5145f…` + ext (decay) + `out/ext2.parquet` `8dcb552f…`. Phạm vi: universe_pit, phi tài chính, as-of
cuối quý 2016Q1–2025Q4. MC0 dùng bản đã sửa share-basis.

## 1. Bảng ứng viên × tiêu chí (khoá trước; chân trời chính N = 3/6/12 tháng)
Mẫu: M0 ∩ {X>0} (rating≤3, V_dài>0, V_ngắn>0), so cùng dòng với baseline. IC = rank IC log(V/MC0) theo quý, lấy
trung bình. K = chân co-về-giá (0,5·V_ngắn + 0,5·V_dài, không có thông tin mới). Số quý: IS 16; OOS 24/24/23.

| Ứng viên | IC IS 3/6/12 | IC OOS 3/6/12 | PIC\|K toàn kỳ 3/6/12 | ΔIC vs V_dài OOS 3/6/12 | T1 | T2 | T3 | T4 | T5 | T6 |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 LN×clip(CFO/LN,0,1) | −0,028/−0,024/−0,022 | +0,087/+0,113/+0,136 | +0,015/+0,008/+0,027 | +0,013/+0,017/+0,057 | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| A2 min(LN, CFO) | −0,034/−0,028/−0,018 | +0,078/+0,097/+0,126 | −0,002/−0,014/+0,020 | +0,004/+0,002/+0,047 | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| B3 CFO trung vị 3 năm, g/ROIC | −0,061/−0,070/−0,080 | +0,086/+0,115/+0,142 | +0,002/−0,012/−0,000 | +0,011/+0,016/+0,050 | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| B5 CFO trung vị 5 năm | −0,065/−0,068/−0,099 | +0,088/+0,097/+0,124 | +0,018/−0,009/−0,007 | +0,007/−0,003/+0,049 | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| C1 owner earnings | −0,064/−0,028/+0,007 | +0,078/+0,097/+0,119 | −0,012/−0,017/+0,022 | +0,003/−0,000/+0,039 | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| C2 C1 − ΔNWC | −0,036/−0,004/−0,023 | +0,074/+0,095/+0,085 | −0,009/−0,012/+0,001 | −0,000/+0,001/+0,008 | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| D1 CFO3 − capex 5 năm | +0,008/+0,020/+0,053 | +0,069/+0,083/+0,075 | +0,028/−0,003/−0,037 | −0,007/−0,015/−0,013 | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ |
| **D2 CFO3 − capex chuẩn ngành** | +0,000/+0,026/+0,082 | +0,093/+0,128/+0,150 | **+0,042/+0,064/+0,102** | +0,019/+0,032/**+0,062** | ✓ | ✓ | ✓ | ✓ | **✗** | ✗ |
| E lai theo điểm chất lượng | −0,040/−0,008/+0,035 | +0,087/+0,113/+0,134 | +0,000/+0,020/+0,056 | +0,009/+0,014/+0,045 | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| *Tham chiếu: V_dài (FCFE3y)* | −0,039…+0,012 / +0,003…+0,040 / −0,004…+0,090 | +0,074…+0,082 / +0,094…+0,100 / +0,075…+0,092 | | | | | | | | |
| *V_ngắn (LN)* | −0,055…−0,004 / −0,042…−0,005 / −0,048…−0,003 | +0,055…+0,078 / +0,079…+0,101 / +0,109…+0,125 | | | | | | | | |
| *C4 (decay)* | −0,003/+0,024/+0,082 | +0,090/+0,116/+0,125 | +0,052/+0,061/+0,094 | +0,013/+0,017/+0,036 | | | | | | |

Tham chiếu V_dài/V_ngắn khác chút theo mẫu của từng ứng viên, nên ghi dải. Chi tiết: `out/summary.json` → `res.<X>.none.<N>`.

**D2 trượt ở đâu:**
- **T5 BH-FDR (q=0,10, họ 9):** p một phía của PIC|K là 0,056 (N3), 0,025 (N6), 0,004 (N12). Chỉ N12 sống; luật cần ≥2/3.
- **T6:** ΔIC so với V_dài trên OOS có CI cụm mã loại 0 chỉ ở N12, [+0,021; +0,105]. t khối năm ở N6 = 2,59, vượt
  E[max Z] của 9 trial (1,52) nhưng chưa vượt mức của 434 trial cộng dồn (3,01; mức này chỉ để thông tin).
- PBO (CSCV, IC theo năm, N6, 12 cấu hình) = 0,35 < 0,5.
- Không nới luật sau khi thấy số.

**Chân co-về-giá:**
- K_shrink: IC(X^c) = IC(X) đúng tuyệt đối (lệch 0,0, assert) với c ∈ {0,25; 0,5; 0,75} cho cả 9 ứng viên. Rank IC
  không thưởng việc co về giá.
- K_blend: chỉ D2 có PIC|K dương ở cả IS lẫn OOS. A/B/C/E đều âm trên IS, tức phần "thêm" của chúng đến từ đúng giai
  đoạn 2020+ mà V_ngắn đã có.
- E so với E_const (cùng hai nền, w cố định w̄ = 0,632): ΔIC toàn kỳ −0,012/−0,016/−0,018. Điểm chất lượng LÀM XẤU.

## 2. Kiểm trực tiếp luận điểm "thị trường chú trọng chất lượng lợi nhuận" (Q4, mô tả)
**(i) Biến nào giải thích định giá chéo mã** (as-of Q4 hằng năm, mọi rating, phi tài chính). R² trung bình 2016–19 → 2020–25:

| Mô hình | log–log (chủ yếu là quy mô) | log(MC/TS) ~ ·/TS | thêm FE ngành |
|---|---|---|---|
| LN | 0,793 → 0,810 | 0,422 → 0,320 | 0,468 → 0,364 |
| LN + CFO (hoặc CFO/LN) | 0,795 → 0,824 | 0,433 → 0,328 | 0,478 → 0,373 |
| CFO một mình | 0,706 → 0,732 | 0,240 → 0,147 | 0,316 → 0,212 |
| **FCFE một mình** | **0,521 → 0,538** | **0,211 → 0,124** | **0,303 → 0,193** |
| LN + FCFE | 0,803 → 0,827 | 0,436 → 0,324 | 0,480 → 0,369 |

- Thị trường định giá chủ yếu theo LN. CFO chỉ thêm khoảng +0,01 R²; FCFE thêm gần 0.
- Hệ số CFO/TS (kiểm soát LN, FE ngành) dương ở 9/10 năm, nhưng nhỏ: ~1,0 so với ~7 của LN. Năm 2021 ≈ 0.
- Hệ số capex/TS đổi dấu theo năm (−2,3 … +2,2). Thị trường không trừ capex như chi phí một cách nhất quán.

**(ii) Có thưởng P/E cho CFO/LN cao không?** Tercile CFO3/LN3 trong năm; FE ngành×năm; kiểm soát log(1+g), ROE.
- 2016–19: chênh log P/E (cao − thấp) = **+0,003**, CI cụm mã [−0,18; +0,19]. Không thưởng.
- 2020–25: **−0,127**, CI [−0,27; +0,004]. Nhóm chất lượng THẤP được định giá CAO hơn. P/E trung vị thấp/giữa/cao = 20,9 / 13,2 / 15,0.
- Theo năm: âm ở 2021–25 (−0,11 … −0,25), dương ở 2016, 2018, 2020.

**Đọc:**
- Thị trường nhìn LN, nhưng KHÔNG dùng CFO để thẩm định LN. Sau 2020 nó còn trả giá cao hơn cho LN có chất lượng dòng tiền thấp.
- Kết hợp với dd_fcfe3y_decay (accrual cao ⇒ lợi suất sau đó THẤP hơn): chất lượng LN có giá trị như một **nguồn sai
  định giá**, không phải như một mô tả cách thị trường đang định giá.
- Vì vậy một nền "bám cách nhìn của thị trường" (A1/A2/E) không phải là nền dự báo tốt hơn. Dữ liệu nghiêng về phía
  giữ CFO trong nền và chỉ khử phần capex mang tính chu kỳ riêng của từng mã. Đó chính là cấu trúc của D2 và C4.

## 3. Đòn tấn công tự kiểm (mô tả; không đổi kết luận)
- **Bỏ BĐS / bỏ tercile ADV60 thấp mỗi quý / chỉ dòng có MC0 fiinprox (share-basis):** D2 giữ dấu và độ lớn. OOS IC N12
  là +0,177 / +0,140 / +0,145; PIC|K N12 CI loại 0 ở cả 3 biến thể. A1, E, D1 không ứng viên nào đổi từ trượt thành đạt.
  B=200 cho phần này.
- **Sống sót:** 0 dòng thiếu nhãn trong mẫu D2 ở N3/N6, và ở N12 với các as-of ≤ 2024Q3. Không có mất nhãn do huỷ niêm yết trong mẫu.
- **Ngân hàng/tài chính:** đã loại ở panel (D.is_financial). BĐS đã kiểm ở trên.
- **One-off:** A1 (trung vị LN) và A2 (trung bình, min với CFO) cho kết quả gần nhau. Không có cột khoản bất thường để kiểm trực tiếp.
- **Chân trời dài (mô tả, ngoài tiêu chí):**
  - D2 ở N24: IC IS/OOS +0,182/+0,140; ΔIC vs V_dài trên OOS +0,080 [+0,022; +0,128].
  - D2 ở N36: +0,230/+0,169; ΔIC +0,102 [+0,039; +0,172]; ΔIC IS ≥ 0.
  - A1/E ở N24–36 có OOS mạnh nhưng IS yếu (giống V_ngắn).
  - Mọi nền định giá, kể cả V_dài, đều gần 0 trên IS ở 3–6 tháng. Chân trời ngắn là nơi khó nhất để một mỏ neo định giá thể hiện.
- **Năm gánh:** D2 IC theo năm ở N6: 2016 −0,115; 2017–19 +0,04…+0,12; 2020 +0,322; 2021–24 +0,08…+0,12; 2025 +0,017.
  Bỏ 2 năm cao nhất (2020, 2021) vẫn +0,053. LOYO nhỏ nhất +0,061.

## 4. Câu trả lời thực dụng cho skill DD
1. **Không có nền nào đủ vững để HIỂN THỊ chính thức cạnh V_dài theo luật khoá.** Không có nền nào thay V_dài. Giữ nguyên.
2. Nếu Mike/user muốn một dòng nhạy display-only như đề xuất C4 của decay, ứng viên hợp lý nhất là **D2**. Phải gắn
   nhãn "chưa qua tiêu chí khoá, theo dõi". Đây là ĐỀ XUẤT, không phải kết quả đạt. D2 có hai giới hạn cấu trúc phải in kèm:
   - Nền không định nghĩa (≤ 0 hoặc thiếu dữ liệu) ở 30,5% dòng rating≤3, chủ yếu khi CFO thấp so với doanh thu × capex chuẩn ngành.
   - Phạt sai các mã doanh thu lớn, capex/doanh thu thấp hơn hẳn trung vị nhóm ngành của chính nó. Ví dụ PNJ 2023Q4 ra nền âm: doanh thu 32,0
     nghìn tỷ × 3,3% trung vị nhóm tiêu dùng/bán lẻ ≈ 1.059 tỷ, so với CFO3/3 ≈ 292 tỷ (đo trong job này).
   - Cần một nhóm so sánh mịn hơn trước khi dùng.
3. **Không dùng điểm chất lượng CFO/LN để trộn nền (E).** Nó làm xấu so với trộn hằng số.
   Nên dùng CFO/LN như **cờ rủi ro** trong DD (accrual cao ⇒ thị trường đang trả cao cho LN chưa thành tiền), không như hệ số nền.
4. **Theo dõi:**
   - Khi có thêm 4–8 quý OOS, chạy lại `calc/analyze.py` không đổi luật. D2 chỉ cần T5 sống thêm 1 chân trời.
   - Chân trời 24–36 tháng (nơi D2 mạnh nhất) nên được khoá làm chân trời chính trong prelock kế tiếp nếu Mike đồng ý.
     Đây là quyết định thiết kế, không suy từ số này.

**Độ tin cậy:**
- Kết luận âm (A/B/C/E không đạt; E kém hơn chân điều khiển; thị trường không thưởng CFO/LN): **khá cao**. Số dòng
  3,0–3,8 nghìn, 300+ mã, nhất quán qua các đòn tấn công.
- Kết luận về D2: **chưa đủ bằng chứng.** Mẫu có 16 quý IS và 23–24 quý OOS, nên lực thống kê ở 3–6 tháng thấp.

## 5. Giới hạn
- LN3 trong A1/A2/C1 là tổng 3 TTM cuốn (theo engine `_annual_series`), còn CFO3 là trường 3 năm tài chính (đổi ở Q4).
  Hai bên lệch thời điểm tới 9 tháng. Đây là định nghĩa engine; chưa kiểm bản đồng bộ.
- Khấu hao là proxy EBITDA − EBITM × doanh thu (≤ 0 ở 10,5% dòng ⇒ C1, C2, E không định nghĩa ở đó). ROIC3Y, ROE3Y là
  số vendor, có thể bị restate. ICB lấy theo snapshot hiện tại.
- Q4 đo trên as-of Q4 (1 dòng/mã/năm), không có EV (thiếu nợ ròng chuẩn) ⇒ chỉ P/E.
- Rank IC đo xếp hạng, không đo mức tâm. Các khẳng định về mức V/P không có trong báo cáo này.
- Prelock không ghi rõ các cổng cơ học sau; tôi khai ở đây:
  - b cần ROE > 0 (ROIC > 0 cho B).
  - D1 cần CF_OA_5Y có giá trị.
  - Nhóm ngành < 5 mã thì dùng trung vị cả quý (D2).
  - E không định nghĩa khi V_cash ≤ 0.

## 6. Kỷ luật & tái lập
- **Trial lựa chọn: 9.** Cộng dồn chuỗi DD: 425 + 9 = **434**. Q4 và đòn tấn công là mô tả. PBO 0,35. DSR-analog: t D2
  2,59 so với E[max] 1,52 (9 trial) / 3,01 (434 trial).
- **PIT:**
  - fin_time ≤ as-of (assert ở build_panel). Lịch sử quý chỉ lấy bản phát hành ≤ fin_time.
  - Trung vị ngành D2 dùng chéo mã cùng as-of, không nhãn.
  - Không dùng profit_*, không dùng ticker_prune.
- **Chạy 2 lần cho cùng md5:** `summary.json` `cf939423613bad6c6f023cf380ffa39c` (`out/md5_run1.txt`, `md5_run2.txt`).
- **Tái tính độc lập** (`calc/recompute_hand.py`; đọc thẳng ticker_financial, không import bases/common):
  - Phạm vi: FPT, HPG, PNJ, DGC, REE @2023Q4 × A1, B3, C1, D1, D2, E.
  - Kết quả: lệch tương đối tối đa **0,0** ở mọi ô có định nghĩa (`out/recompute_hand.csv`). D2 dựng lại trung vị ngành từ dữ liệu gốc.
  - Lần chạy đầu, ô REE·E lệch vì script tay thiếu cổng "nền ≤ 0". Đã thêm cổng; pipeline không đổi.
- md5 output: `out/outputs_md5.txt`.

```
cd agents/Taylor/research/dd_cfo_anchor_20261112/calc ; PY=/home/trido/thanhdt/wc_venv/bin/python
$PY -W ignore build_ext2.py      # -> out/ext2.parquet (~2,5 phút)
$PY -W ignore analyze.py         # -> out/summary.json, cands_table.csv (~4 phút, B=1000, 6 tiến trình)
$PY -W ignore q4_market.py       # -> out/q4_market.json
$PY -W ignore recompute_hand.py  # -> out/recompute_hand.csv
```
