# REPORT — Model kỹ thuật định lượng "deal ±5%, bán từ chiều T+2" bổ trợ Livermore (PAPER-ONLY)
Job `Taylor_20261105_171103` · 2026-11-06 · PREREG: `PREREG.md` (viết trước khi chạy) · code: `engine.py`,
`analyze.py`, `selfcheck.py` · số: `results.csv` (216 dòng = 72 cấu hình × 3 mức slippage), `table_h20.md`,
`byyear.csv`, `summary.json`, `deals.parquet` · dữ liệu: `data/bq_cache` tới 2026-11-05.
Không wire production. Chưa qua quant-skeptic.

## 1. Kết luận thẳng: NO-GO, không có edge sau phí
- **Ở slippage chính 0,2%/chiều: 0/72 cấu hình có lợi suất ròng trung bình > 0** (tốt nhất BRK/L50/H20/C:
  −0,04%/deal). Ở 0,3%: 0/72. Chỉ ở slippage 0,1% có 11/72 dương, cao nhất +0,16%/deal (BRK/L50/H20/C), p=0,19,
  không có ý nghĩa thống kê.
- **Win-rate hoà vốn** của deal ±5% đối xứng sau phí 0,097% + slippage s:
  **53,9% (s=0,1%) · 56,0% (s=0,2%) · 58,0% (s=0,3%)**. P(+5% trước −5%) cao nhất đo được ở bất kỳ cấu hình nào
  là **51,9%** (PB20/L20/H20/HL). Bản C (bảo thủ, theo close) cao nhất là 48,5%. **Không pattern nào chạm ngưỡng hoà vốn.**
- **Vào ngẫu nhiên cùng ngày, cùng bộ lọc thanh khoản** (L20, H20, bản C): P(TP) = **43,2% IS / 45,9% OOS**,
  R ròng −0,33%/deal. Ván cờ ±5% bán từ T+2 có xác suất nền DƯỚI 50%: thua phí trước khi tính tới tín hiệu.
- **So với vào ngẫu nhiên:** họ xu hướng (BRK breakout+vol, PB20 pullback MA20) hơn ngẫu nhiên +1–3pp P(TP), nhưng
  exR OOS chỉ ~0…+0,17pp/deal, CI95 luôn chứa 0 (p_OOS ≥ 0,17). PB50, SQZ, OSB, FTD **thua** ngẫu nhiên
  (exR −0,2…−0,9pp, p_OOS ≥ 0,84 tức âm có ý nghĩa ở SQZ/OSB/FTD). Khớp với tiền lệ `ta-schools-vn-20261025`.
- **DSR = 0,00 cho cả 72 trial** (SR tốt nhất trên chuỗi exR cấp ngày 0,040 so với ngưỡng max-kỳ-vọng SR0 = 0,171).
  **PBO = 0,086**: thứ hạng giữa các pattern ổn định (BRK/PB20 luôn ở nhóm đầu, SQZ/OSB/FTD luôn ở nhóm cuối), nhưng
  nhóm đầu cũng chỉ ≈ 0. PBO thấp ở đây nghĩa là "chọn đúng cái đỡ tệ nhất", không phải "có edge".
- **Calibration (đầu vào Livermore):** logistic học trên IS, chấm OOS: Brier **0,2501** so với climatology (tần suất
  nền IS) 0,2490 và đồng xu 0,2500 ⇒ **BSS = −0,5%**. Mô hình không phân biệt được: dải dự báo 0,35–0,51 nhưng tỉ lệ
  thực mỗi decile chỉ trong 0,42–0,50 (bảng §5). Không có điểm số nào đáng đưa cho Livermore ngoài **tần suất nền**.
- **Phân bố theo năm:** P(TP) của mọi pattern đi theo năm thị trường (2020: 54–64%, 2021: 52–57%, 2022: 32–46%,
  2026 YTD: 28–50%), cùng chiều với rổ ngẫu nhiên ⇒ phần "thắng" là beta/thời điểm thị trường, không phải pattern.
- **Hậu FTSE (T0 ≥ 2026-09-21):** 11–27 deal/pattern, ≤ ~10 ngày tín hiệu độc lập ⇒ **không đủ mẫu**, không kết luận.

## 2. Model + quy tắc kích hoạt (đủ để tái lập)
**Dữ liệu (PIT):** `tav2_bq.ticker` (cache local, OHLC điều chỉnh, `Price` thô), `tav2_mike.universe_pit`
(`in_universe` tại T0 — không dùng `ticker_prune`). Không dùng cột forward (`profit_*`, `*_center_*`, `PC1W..PC2M`,
`Open_1D`, `O1W..O2Y`). Chỉ báo tự tính từ OHLCV ≤ T0 (MA tự tính khớp cột BQ MA20/50/200 ở 98,3/96,9/93,0% số
dòng với ngưỡng |Δ|/Close < 0,1%; phần lệch không ảnh hưởng vì engine dùng MA tự tính).
**Thanh khoản:** MDV60 thực = trung vị 60 phiên của `Price×Volume`/`Inflation_7` (VND 2026). Bậc lồng nhau
L20 ≥ 20 tỷ · L50 ≥ 50 tỷ · L100 ≥ 100 tỷ. Giai đoạn T0 2014-01-02 → 2026-10; IS 2014–2019, OOS 2020+.

**Pattern (tham số sách giáo khoa, không tune; hồi chiêu 10 phiên/mã/pattern):**
| Mã | Quy tắc tại close T0 | Số tín hiệu L20 |
|---|---|---|
| BRK | Close > max High 60 phiên trước ∧ Vol ≥ 1,5×TB Vol20 trước ∧ Close > MA50 | 3.421 |
| PB20 | MA50>MA200 ∧ MA50 dốc lên (vs 20 phiên trước) ∧ Close>MA50 ∧ Low ≤ MA20×1,01 ∧ Close ≥ MA20 ∧ đỉnh 20 phiên trước ≥ MA20×1,05 | 5.282 |
| PB50 | MA50>MA200 ∧ MA200 dốc lên ∧ Low ≤ MA50×1,01 ∧ Close ≥ MA50 | 5.571 |
| SQZ | Bề rộng Bollinger(20,2)/MA20 tại T0−1 ≤ phân vị 20% của 120 phiên ∧ Close > dải trên ∧ Vol > TB Vol20 | 3.163 |
| OSB | RSI14 Wilder (T0−1) < 30 ∧ Close > High T0−1 | 1.838 |
| FTD | Đáy (min Close 20 phiên) thấp hơn đỉnh 80 phiên ≥ 15% ∧ T0 là phiên thứ 4–10 kể từ đáy ∧ +3% close-close ∧ Vol > Vol hôm trước và > TB Vol20 ∧ Close > đáy | 2.375 |

**Mô hình deal:**
- Tín hiệu chốt close T0 → lệnh LO mua phiên B = T0+1, **trần giá = Close_T0 × 1,03**. Open_B ≤ trần → khớp Open_B;
  Open_B > trần mà Low_B ≤ trần → khớp tại trần; còn lại hoặc B "trần trắng" (High=Low, Open > Close_T0) → **không khớp**
  (tỉ lệ 0,3–2,7% tuỳ pattern, cao nhất OSB/FTD; loại khỏi thống kê và báo trong `unfilled`).
- TP = giá khớp × 1,05, SL = giá khớp × 0,95. **Không thoát trước chiều B+2.**
  - **Bản C (bảo thủ):** xét close từng phiên B+2..B+H; Close ≥ TP hoặc ≤ SL → bán tại chính close đó (ghi return thật, kể cả vượt mức).
  - **Bản HL (lạc quan):** B+2 chỉ xét close; từ B+3: gap Open ≥ TP → bán Open; gap Open ≤ SL → bán Open (xấu hơn mức);
    Low ≤ SL → bán tại SL (ưu tiên SL nếu cùng phiên chạm cả hai); High ≥ TP → bán tại TP.
  - Phiên phải bán mà sàn trắng (High=Low, giảm) → bán Open phiên kế tiếp.
  - Hết hạn H ∈ {10, 20} phiên (tính từ B) → bán close B+H.
- Chi phí 0,097%/chiều + slippage s/chiều; R ròng = P_ra(1−f−s) / (P_vào(1+f+s)) − 1. "Thành công" = thoát do TP.
- Deal thiếu dữ liệu tương lai (đình chỉ/huỷ niêm yết/cuối mẫu) bị loại: 805 / ~300k (0,27%) ở C20.

## 3. Bảng chính (H=20, s=0,2%) — xem đầy đủ H=10, s=0,1/0,3 trong `results.csv`
P(TP) ngẫu nhiên = rổ mọi mã đủ điều kiện cùng ngày (trung bình cấp ngày, theo đúng các ngày có tín hiệu).
exR = R_tín hiệu − R_ngẫu nhiên cùng ngày, gộp theo NGÀY (N độc lập = số ngày), CI/p bootstrap khối tháng (2000 lần).
p = P(exR ≤ 0). DSR tính trên họ 72 trial.

| pattern | bậc | bản | N dòng / ngày / tháng | không khớp | P(TP) IS / OOS | P(TP) ngẫu nhiên OOS | R ròng TB IS / OOS (%) | exR vs ngẫu nhiên OOS (pp) [CI95] p | DSR | LOYO đổi dấu | năm exR>0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BRK | L20 | C | 3377 / 1497 / 152 | 1.2% | 47.9 / 47.7 | 47.3 | -0.03 / -0.09 | -0.00 [-0.40; +0.39] p=0.52 | 0.00 | 0 | 8/13 |
| PB20 | L20 | C | 5257 / 1853 / 154 | 0.4% | 47.3 / 48.8 | 45.9 | -0.13 / -0.10 | +0.06 [-0.21; +0.33] p=0.36 | 0.00 | 0 | 7/13 |
| PB50 | L20 | C | 5545 / 2027 / 154 | 0.4% | 41.8 / 44.0 | 45.0 | -0.66 / -0.62 | -0.30 [-0.53; -0.07] p=0.99 | 0.00 | 0 | 3/13 |
| SQZ | L20 | C | 3138 / 1398 / 149 | 0.7% | 39.2 / 42.4 | 46.0 | -0.72 / -0.61 | -0.67 [-1.02; -0.31] p=1.00 | 0.00 | 0 | 3/13 |
| OSB | L20 | C | 1779 / 642 / 145 | 2.6% | 43.6 / 46.8 | 45.1 | -0.33 / -0.49 | -0.65 [-1.23; -0.06] p=0.98 | 0.00 | 0 | 5/13 |
| FTD | L20 | C | 2333 / 942 / 151 | 1.6% | 42.1 / 47.2 | 46.1 | -0.72 / -0.37 | -0.62 [-1.06; -0.17] p=1.00 | 0.00 | 0 | 3/13 |
| BRK | L20 | HL | 3379 / 1499 / 152 | 1.2% | 49.9 / 50.3 | 50.8 | -0.25 / -0.21 | +0.10 [-0.28; +0.48] p=0.30 | 0.00 | 0 | 9/13 |
| PB20 | L20 | HL | 5259 / 1855 / 154 | 0.4% | 50.9 / 52.2 | 49.4 | -0.18 / -0.19 | +0.01 [-0.24; +0.27] p=0.48 | 0.00 | 0 | 7/13 |
| PB50 | L20 | HL | 5547 / 2029 / 154 | 0.4% | 45.5 / 47.3 | 48.5 | -0.67 / -0.68 | -0.27 [-0.51; -0.05] p=0.99 | 0.00 | 0 | 3/13 |
| SQZ | L20 | HL | 3139 / 1398 / 149 | 0.7% | 44.1 / 44.5 | 49.6 | -0.67 / -0.88 | -0.77 [-1.12; -0.42] p=1.00 | 0.00 | 0 | 2/13 |
| OSB | L20 | HL | 1780 / 642 / 145 | 2.6% | 45.5 / 47.0 | 47.6 | -0.52 / -0.69 | -0.58 [-1.14; -0.04] p=0.98 | 0.00 | 0 | 4/13 |
| FTD | L20 | HL | 2336 / 942 / 151 | 1.6% | 46.4 / 49.1 | 48.9 | -0.67 / -0.57 | -0.45 [-0.77; -0.14] p=1.00 | 0.00 | 0 | 3/13 |
| BRK | L50 | C | 1920 / 1047 / 143 | 1.0% | 46.7 / 47.9 | 47.3 | -0.11 / -0.02 | +0.11 [-0.28; +0.53] p=0.29 | 0.00 | 0 | 11/13 |
| PB20 | L50 | C | 3149 / 1356 / 152 | 0.3% | 45.9 / 47.2 | 45.0 | -0.43 / -0.35 | +0.01 [-0.31; +0.33] p=0.48 | 0.00 | 1 | 7/13 |
| PB50 | L50 | C | 3441 / 1517 / 152 | 0.3% | 39.9 / 43.4 | 43.9 | -0.99 / -0.69 | -0.13 [-0.37; +0.13] p=0.84 | 0.00 | 0 | 3/13 |
| SQZ | L50 | C | 1719 / 927 / 138 | 0.3% | 36.4 / 41.5 | 45.5 | -0.73 / -0.73 | -0.67 [-1.02; -0.33] p=1.00 | 0.00 | 0 | 3/13 |
| OSB | L50 | C | 988 / 404 / 122 | 2.7% | 40.3 / 46.5 | 45.2 | -0.74 / -0.46 | -0.67 [-1.36; +0.01] p=0.97 | 0.00 | 0 | 2/13 |
| FTD | L50 | C | 1317 / 596 / 132 | 1.4% | 40.6 / 46.4 | 46.1 | -1.03 / -0.50 | -0.62 [-1.09; -0.15] p=0.99 | 0.00 | 0 | 3/13 |
| BRK | L50 | HL | 1922 / 1049 / 143 | 1.0% | 48.8 / 50.9 | 51.1 | -0.34 / -0.10 | +0.17 [-0.20; +0.53] p=0.19 | 0.00 | 0 | 9/13 |
| PB20 | L50 | HL | 3150 / 1357 / 152 | 0.3% | 49.4 / 51.7 | 48.8 | -0.42 / -0.24 | +0.06 [-0.22; +0.37] p=0.34 | 0.00 | 0 | 7/13 |
| PB50 | L50 | HL | 3442 / 1518 / 152 | 0.3% | 44.2 / 47.3 | 47.8 | -0.87 / -0.68 | -0.16 [-0.39; +0.07] p=0.92 | 0.00 | 0 | 5/13 |
| SQZ | L50 | HL | 1719 / 927 / 138 | 0.3% | 41.1 / 44.1 | 49.5 | -0.76 / -0.91 | -0.73 [-1.05; -0.41] p=1.00 | 0.00 | 0 | 3/13 |
| OSB | L50 | HL | 988 / 404 / 122 | 2.7% | 42.4 / 47.2 | 47.8 | -0.88 / -0.69 | -0.55 [-1.09; +0.03] p=0.96 | 0.00 | 0 | 2/13 |
| FTD | L50 | HL | 1318 / 596 / 132 | 1.4% | 45.4 / 47.9 | 49.3 | -0.93 / -0.73 | -0.70 [-1.13; -0.29] p=1.00 | 0.00 | 0 | 3/13 |
| BRK | L100 | C | 1054 / 669 / 126 | 0.9% | 43.1 / 47.4 | 48.3 | -0.38 / -0.11 | +0.02 [-0.48; +0.48] p=0.47 | 0.00 | 1 | 6/13 |
| PB20 | L100 | C | 1852 / 931 / 133 | 0.4% | 47.9 / 46.5 | 44.5 | -0.27 / -0.42 | -0.01 [-0.36; +0.35] p=0.51 | 0.00 | 1 | 5/13 |
| PB50 | L100 | C | 2056 / 1043 / 138 | 0.5% | 38.0 / 43.1 | 42.9 | -1.48 / -0.75 | -0.23 [-0.48; +0.02] p=0.96 | 0.00 | 0 | 4/13 |
| SQZ | L100 | C | 936 / 586 / 115 | 0.4% | 34.6 / 42.2 | 45.3 | -0.61 / -0.61 | -0.57 [-0.90; -0.21] p=1.00 | 0.00 | 0 | 4/12 |
| OSB | L100 | C | 527 / 250 / 97 | 1.9% | 42.7 / 46.1 | 45.4 | -0.15 / -0.59 | -0.66 [-1.49; +0.19] p=0.94 | 0.00 | 0 | 3/13 |
| FTD | L100 | C | 744 / 390 / 101 | 1.2% | 46.0 / 44.9 | 45.2 | -0.48 / -0.76 | -0.40 [-0.96; +0.16] p=0.92 | 0.00 | 0 | 6/13 |
| BRK | L100 | HL | 1054 / 669 / 126 | 0.9% | 45.4 / 51.0 | 52.5 | -0.59 / -0.10 | +0.11 [-0.32; +0.59] p=0.33 | 0.00 | 7 | 7/13 |
| PB20 | L100 | HL | 1853 / 932 / 133 | 0.4% | 52.5 / 51.4 | 48.6 | -0.18 / -0.23 | +0.05 [-0.29; +0.45] p=0.39 | 0.00 | 7 | 6/13 |
| PB50 | L100 | HL | 2057 / 1044 / 138 | 0.5% | 42.7 / 46.8 | 47.1 | -1.25 / -0.74 | -0.26 [-0.48; -0.03] p=0.99 | 0.00 | 0 | 3/13 |
| SQZ | L100 | HL | 936 / 586 / 115 | 0.4% | 40.4 / 45.3 | 49.5 | -0.69 / -0.82 | -0.66 [-0.99; -0.32] p=1.00 | 0.00 | 0 | 4/12 |
| OSB | L100 | HL | 527 / 250 / 97 | 1.9% | 43.8 / 48.2 | 48.2 | -0.51 / -0.71 | -0.41 [-1.08; +0.30] p=0.87 | 0.00 | 0 | 2/13 |
| FTD | L100 | HL | 744 / 390 / 101 | 1.2% | 47.1 / 46.7 | 48.5 | -0.80 / -0.91 | -0.64 [-1.10; -0.19] p=1.00 | 0.00 | 0 | 3/13 |

Đọc: (i) cột R ròng toàn âm; (ii) exR của BRK/PB20 dương nhưng CI chứa 0; (iii) SQZ/OSB/FTD/PB50 thua rổ ngẫu nhiên
ở mọi bậc thanh khoản; (iv) bậc thanh khoản cao hơn KHÔNG cải thiện (L100 còn kém hơn L20 ở BRK/PB20).

## 4. Capacity
Size 5% NAV ≈ 40–45 triệu/lệnh/account. MDV60 trung vị của mã có tín hiệu: L20 59 tỷ · L50 112 tỷ · L100 188 tỷ ⇒
lệnh 45 triệu = 0,08% / 0,04% / 0,02% MDV60; ở đúng sàn 20 tỷ là 0,23%. **Không phải ràng buộc ở quy mô hiện tại.**
Bắt đầu thành ràng buộc khi lệnh vượt ~1% MDV (tác động giá đáng kể với cổ VN) ⇒ ở sàn 20 tỷ: lệnh > 200 triệu,
tức NAV account > ~4 tỷ với size 5%; trần %ADV 10% của fleet chỉ chạm khi NAV > ~40 tỷ. (Không mô hình hoá impact;
slippage cố định 0,1–0,3% chỉ hợp lý ở quy mô hiện tại.) Capacity không cứu được kết luận: edge đã ≤ 0 ở size nhỏ nhất.

## 5. Calibration (đầu ra cho Livermore)
Mục tiêu: P(TP) bản C, H=20, L20. Logistic (6 dummy pattern, log MDV60, VNINDEX>MA50, Close/MA50−1), fit IS 2014–19, chấm OOS.
| Tập | n test (ngày) | Nền IS → OOS | Brier model | Brier nền IS | Brier 0,5 | BSS vs nền |
|---|---|---|---|---|---|---|
| Chỉ dòng có tín hiệu | 14.173 (1.617) | 44,3% → 46,3% | 0,2501 | 0,2490 | 0,2500 | −0,5% |
| Mọi dòng đủ điều kiện | 215.686 (1.704) | 43,0% → 46,2% | 0,2498 | 0,2496 | 0,2500 | −0,1% |

Reliability (tín hiệu, decile dự báo → thực): 0,35→0,42 · 0,38→0,46 · 0,40→0,45 · 0,41→0,45 · 0,42→0,44 · 0,44→0,47 ·
0,45→0,50 · 0,47→0,45 · 0,49→0,49 · 0,51→0,49. Gần như phẳng ⇒ không phân biệt được. Hệ số duy nhất có dấu nhất quán:
VNINDEX>MA50 (+0,16 log-odds) — tức lại là trạng thái thị trường, không phải pattern.
**Hàm ý cho bài thử Livermore:** với biến mục tiêu này, mốc đúng phải vượt là **Brier climatology (~0,249)**, không phải
đồng xu (0,250); Brier 0,2507 của Livermore kém cả hai. Model này cũng chỉ đạt ≈ climatology — tức không model kỹ thuật
nào ở đây có thông tin để "bổ trợ".

## 6. Đề xuất ghép với Livermore (giữ MÙ, DISPLAY-ONLY, không sizing/gate)
Vì NO-GO, **không đưa "điểm model" theo pattern** (nó chỉ là nhiễu quanh tần suất nền và có thể neo Livermore vào tín hiệu
vô giá trị). Đề xuất tối giản, nếu user vẫn muốn một tầng định lượng:
1. Livermore khoá dự báo (P(+5% trước −5%) trong H=20, kèm lý do) vào registry, có hash + timestamp, **trước** khi xem gì thêm.
2. Sau khoá mới hiện "thẻ tham chiếu": tần suất nền rổ ngẫu nhiên cùng bậc thanh khoản (IS/OOS ~43–46%, theo năm), ngưỡng
   hoà vốn 56% (s=0,2%), pattern nào đang bật + P(TP) lịch sử kèm CI. Thẻ ghi rõ "model không hơn tần suất nền (BSS −0,5%)".
3. Chấm cả Livermore lẫn climatology bằng Brier trên cùng mục tiêu; Livermore chỉ được coi là có kỹ năng khi BSS vs
   climatology > 0 với CI không chứa 0 trên ≥ ~100 dự báo độc lập theo ngày.
Không viết code tích hợp ở job này (chưa có quyết định của user).

## 7. Self-check & kiểm toán
- `selfcheck.py`: tái hiện ĐỘC LẬP 400 deal ngẫu nhiên × 4 bản (C10/HL10/C20/HL20) bằng vòng lặp thuần Python trên OHLC
  thô ⇒ **0 lệch lý do/giá; tổng |Δ P&L| trên 1 tỷ/deal = 0,000000 VND** (rc=0).
- Chân control = mọi mã đủ điều kiện cùng ngày (chính là baseline ngẫu nhiên), dùng cùng engine.
- Số trial khai báo 72 (6 pattern × 3 bậc × 2 H × 2 bản); slippage 0,1/0,3 là độ nhạy.
- Không pin `data/results_registry.md`: NO-GO, không có ledger pin (đúng chỉ thị "chỉ khi có ledger").

## 8. Lệch PREREG / giới hạn
- FTD: "đỉnh 60 phiên trước đáy" cài đặt là max Close 80 phiên (đáy nằm trong 20 phiên gần) — xấp xỉ tương đương.
- Tiêu chí (e) LOYO tính trên exR toàn mẫu; 0 lần đổi dấu ở hầu hết ô; ngoại lệ PB20/L50/C (1) và BRK/PB20 ở L100 (1–7 ⇒ không ổn định).
- Giá điều chỉnh (Close/Open/High/Low) đã gộp cổ tức tiền ⇒ chạm TP trên chuỗi điều chỉnh hơi lạc quan ở ca có GDKHQ trong cửa sổ.
- Không mô hình hoá: biên độ trần/sàn theo sàn (chỉ xử lý trần/sàn trắng High=Low), lô lẻ, impact theo size, thuế bán 0,1%
  (**thêm thuế làm kết luận xấu hơn**: hoà vốn tăng thêm ~1pp (ước lượng theo độ nhạy p*: +0,1%/chiều ≈ +1pp)).
- Universe_pit có ngày trống (in_universe=0 cả phiên) ⇒ các ngày đó không có deal.
- Bản HL giả định stop khớp đúng giá SL khi không gap — lạc quan; bản C là bản đáng tin.
