**KẾT LUẬN:** (1) Sụt giảm theo tiêu chí khoá trước = **ARTIFACT** — hiệu PIC(IS)−PIC(OOS) của V_dài KHÔNG tách khỏi nhiễu ở 3/4 chân trời (chỉ N24 biên), nên CHƯA chứng minh được là thật; mô tả cho thấy suy yếu DẦN từ as-of 2021+, không phải bước nhảy 2020. (2) **Cơ chế chính: trừ capex thực.** CFO yield vẫn giữ thông tin OOS (PIC +0,15…+0,20, CI loại 0), còn capex/CFO đổi từ ≈0 (IS) sang dự báo DƯƠNG (OOS +0,11…+0,26) ⇒ FCFE = CFO − capex trừ đi đúng phần đang mang tin; lợi thế IS chủ yếu đến từ xếp hạng giữa ngành và cũng biến mất. (3) **Chưa có cách sửa đạt tiêu chí khoá**: 0/8 biến thể đạt; gần nhất C4 (CFO3 − min(capex, khấu hao)) Δ OOS dương ở cả 4 N nhưng CI cụm mã chỉ loại 0 ở 2/4 N (cần 3/4).

Job Taylor_20261111_051016 · 2026-11-11 · Taylor · CHỈ NGHIÊN CỨU (không sửa dcf_valuation.py, skill, dd_price_zones.json, moat_tags.csv).
PRELOCK.md md5 `267caa2bb505669770e1d837e852ea8d`, khoá 12:14:09 ICT, trước mọi lần tính IC (`out/prelock_md5.txt`).
Panel dd_blend md5 `1de5145f42281f9b3bf5e940064e473c` + `out/ext.parquet` (thành phần dòng tiền, ghép theo (mã, fin_time), vintage CF_OA_3Y lệch 0).

Thước đo: rank IC theo quý → trung bình quý; **PIC** = hệ số chuẩn hoá của x trong hồi quy hạng (x, V_ngắn v0) mỗi quý (= PIC_l của dd_fwd_prelock, tái lập tới 1e-9 — assert). CI95: cụm MÃ (B=1000) và **khối NĂM** (rút năm có hoàn lại; thay cụm quý vì nhãn N>3 tháng chồng lấp). Mẫu M0 = rating≤3 ∧ V_dài>0 ∧ V_ngắn>0 (2016Q1–2025Q4).

## Q1 — thật hay artifact?

**(b) Hiệu IS 2016–19 − OOS 2020+ (PIC V_dài):**

| N | PIC IS | PIC OOS | Δ | CI cụm mã | CI khối năm |
|---|---|---|---|---|---|
| 12 | +0,068 | +0,061 | +0,007 | [−0,097; +0,118] | [−0,140; +0,125] |
| 24 | +0,182 | +0,039 | **+0,143** | **[+0,011; +0,271]** | [−0,000; +0,290] |
| 36 | +0,162 | +0,038 | +0,124 | [−0,011; +0,249] | [−0,034; +0,256] |
| 60 | +0,142 | +0,032 | +0,110 | [−0,047; +0,281] | [−0,018; +0,251] |

Luật khoá: "thật" cần CI mã loại 0 ở ≥3/4 N và CI năm ở ≥2/4 N → đạt 1/4 và 0/4. "Artifact" = cả hai CI chứa 0 ở ≥3/4 N → **đạt (N12/36/60) ⇒ nhãn ARTIFACT.** Đọc đúng: nhãn này nghĩa là *không đủ bằng chứng thống kê là thật* với 16 quý IS / 7–23 quý OOS, KHÔNG phải bằng chứng rằng V_dài vẫn tốt. Δ điểm ở N24–60 vẫn lớn (+0,11…+0,14).

**(a) Điểm cắt khác / cửa sổ trượt (PIC V_dài, điểm):**
- IS16–18 / OOS19+: N24 +0,130 → +0,091; N36 +0,125 → +0,087; N12 và N60 OOS còn cao hơn IS. Dời điểm cắt sớm 1 năm thì "sụt" gần như mất, vì as-of 2019–20 mạnh.
- IS16–21 / OOS22+: N24 +0,153 → −0,001, Δ +0,154 với CI mã [+0,027; +0,287] VÀ CI năm [+0,022; +0,292] loại 0; N12 +0,095 → +0,013; N36 +0,127 → +0,016.
- Cửa sổ 4 năm as-of, N24: 2016–19 +0,18 · 2017–20 +0,21 · 2018–21 +0,18 · 2019–22 +0,12 · 2020–23 +0,06 · 2021–24 −0,01 · 2022–25 −0,00. N36 cùng hình dạng (0,16 → −0,01). N12 đỉnh 2017–20 +0,16, xuống +0,01 ở 2022–25.
- Hồi quy PIC theo quý: độ dốc N24 −0,025/năm, CI khối năm [−0,071; −0,000]; bước nhảy 2020 −0,143, CI [−0,296; +0,018]. Trong riêng IS độ dốc DƯƠNG (+0,05…+0,08/năm). ⇒ **Đỉnh quanh as-of 2017–20 rồi suy yếu dần từ as-of 2021**, không phải gãy ở 1/1/2020.

**(c)** Bỏ 2022: PIC OOS +0,066/+0,061/+0,064/+0,032 (N12/24/36/60) — vẫn thấp hơn IS ở N24–60. Bỏ 2020–21 (chỉ còn 2022+): +0,013/−0,001/+0,016/– — còn yếu hơn. ⇒ Không phải do riêng 2022 hay riêng Covid-bull; as-of 2020–21 thật ra là đoạn V_dài còn tốt.

**(d) Mẫu đồng nhất.** Mã có mặt ở cả IS và OOS (135–147 mã): N24 +0,222 → +0,044, Δ +0,178 CI mã [+0,019; +0,317]; N36 +0,206 → +0,015, Δ +0,190 [+0,024; +0,343]. Vậy sụt giảm KHÔNG do universe nở từ ~80 lên ~145 dòng/quý (2021). Bản chặt (≥8 quý mỗi bên, chỉ 41–49 mã): N24 +0,103 → +0,138, không sụt; N36 +0,121 → +0,063. Mẫu quá nhỏ, CI rộng ±0,2, không kết luận được.

## Q2 — cơ chế

Trong frame domestic_v2, r = 12,25% và g_T = 5,5% là hằng số chéo-mã (kiểm trong code) ⇒ log(V_dài/MC0) = log(FCFE3/MC0) + log k(g_exp) (assert khớp 1e-9). PIC (kiểm soát V_ngắn), CI cụm mã; IS → OOS:

| Thành phần | N24 | N36 | N60 |
|---|---|---|---|
| V_dài | +0,182 → +0,039 | +0,162 → +0,038 | +0,142 → +0,032 |
| (i) FCFE3/MC0 | +0,175 → +0,042 | +0,152 → +0,039 | +0,146 → +0,044 |
| (ii) **CFO3/MC0** | +0,212 → **+0,148** [+0,06; +0,23] | +0,262 → **+0,170** [+0,07; +0,27] | +0,322 → **+0,204** [+0,05; +0,36] |
| (iii) capex3/MC0 | +0,090 → **+0,181** | +0,162 → **+0,248** | +0,247 → **+0,347** |
| (iii) **capex/CFO** | −0,026 → **+0,107** [+0,02; +0,18] | +0,029 → **+0,168** [+0,07; +0,26] | +0,092 → **+0,264** [+0,15; +0,37] |
| (iii) capex/doanh thu | +0,051 → +0,139 | +0,082 → +0,185 | +0,148 → +0,236 |
| (iii) capex/tài sản | −0,077 → +0,146 | −0,025 → +0,222 | +0,077 → +0,321 |
| (iv) ΔNWC/tài sản | −0,028 → −0,073 | −0,053 → −0,071 | −0,051 → −0,138 |
| (iv) accrual (NI−CFO)/TS | −0,021 → −0,115 | −0,078 → −0,170 | −0,144 → −0,224 |
| (vi) g_exp | +0,058 → −0,009 | +0,090 → −0,008 | +0,014 → −0,070 |
| (v) V_dài trung hoà ngành | +0,078 → +0,037 | +0,046 → +0,030 | +0,038 → +0,050 |
| tham chiếu E/P TTM | +0,191 → +0,072 | +0,187 → +0,102 | +0,208 → +0,091 |

N12 cùng hướng (`out/summary.json` → `Q2.12`).

**Đọc:**
1. **Phần CFO còn thông tin; phần trừ capex làm mất nó.** FCFE yield = CFO yield × (1 − capex/CFO). OOS, capex/CFO dự báo DƯƠNG lợi suất (CI loại 0 ở N24/36/60), tức (1 − capex/CFO) dự báo ÂM, nên nhân vào triệt tiêu tin của CFO. Trên IS, capex/CFO ≈ 0 nên thiệt hại nhỏ. Đây là thay đổi về *thông tin chứa trong capex*, KHÔNG phải về *mức* capex: trung vị capex/CFO theo năm 0,29–0,36 (2016–19) và 0,21–0,32 (2020–25) — **giả thuyết "capex mở rộng sau 2020 tăng mạnh" KHÔNG được dữ liệu ủng hộ.**
2. **Lợi thế IS chủ yếu là xếp hạng GIỮA ngành.** Trung hoà ngành, PIC IS chỉ +0,04…+0,08 (CI chứa 0) so với +0,14…+0,18 thô; OOS hai bản gần nhau (+0,03…+0,05). Phần giữa-ngành biến mất OOS. IC trong nhóm (điểm, N24 IS→OOS): BĐS +0,18 → −0,12; công nghiệp +0,43 → +0,04; tiêu dùng/bán lẻ −0,03 → +0,35; XD/VLXD −0,01 → +0,10. Tỉ trọng dòng của nhóm capex-nặng ổn định 0,52–0,60 ⇒ không phải do mix số mã đổi.
3. **g_exp không phải thủ phạm chính.** PIC của k(g) kiểm soát FCFE yield: IS +0,08/+0,11 (N24/36) → OOS +0,01/+0,01. Mất phần nhỏ, nhưng FCFE yield một mình đã mất gần hết.
4. **Độ cũ trường 3Y (chỉ đổi ở dòng Q4, cũ 0–9 tháng) không giải thích.** Mẫu tươi (0–3 tháng) và cũ (6–9 tháng) cùng sụt (N24 tươi +0,170 → +0,059, cũ +0,193 → +0,017). Biến thể C8 (FCFE 12 quý cuốn) cũng không tốt hơn.
5. **Vốn lưu động/accrual: tín hiệu ÂM mạnh lên OOS** (accrual cao → lợi suất thấp; Sloan). CFO không bị nhiễu bởi WC theo hướng xấu — ngược lại, CFO thắng NI một phần nhờ đó.

## Q3 — 8 biến thể khoá trước (so trên giao hỗ trợ với baseline)

| Biến thể | Độ phủ M0 | Δ OOS N12/24/36/60 | (i) CI mã loại 0 | (ii) | (iii) |
|---|---|---|---|---|---|
| C1 FCFE 5 năm | 0,91 | −0,026/−0,003/+0,026/+0,030 | 0/4 | ✓ | ✗ |
| C2 CFO3 − khấu hao | 0,85 | +0,020/+0,017/+0,041/+0,044 | 0/4 | ✓ | ✓ |
| C3 CFO3 − KH − g·TSCĐ | 0,76 | −0,010/−0,025/−0,045/+0,020 | 0/4 | ✓ | ✗ |
| **C4 CFO3 − min(capex, KH)** | 0,89 | **+0,034/+0,041/+0,051/+0,064** | **2/4** | ✓ | ✓ |
| C5 NI3 + KH − capex | 0,81 | +0,017/−0,018/−0,024/−0,094 | 0/4 | ✓ | ✗ |
| C6 CFO5 − KH | 0,82 | +0,006/+0,057/+0,085/+0,080 | 0/4 | ✓ | ✗ |
| C7 nhóm nặng dùng C2 | 0,91 | +0,013/+0,007/+0,005/−0,007 | 0/4 | ✓ | ✗ |
| C8 FCFE 12 quý cuốn | 0,78 | +0,000/−0,032/−0,020/−0,028 | 0/4 | ✓ | ✗ |

(iv) PBO (CSCV, 8 khối năm 2016–23, 9 cấu hình) = 0,29 (N24) / 0,43 (N36) < 0,5 ✓. **Không biến thể nào đạt (i) ⇒ 0/8 phục hồi.**

**C4** (capex vượt khấu hao coi là đầu tư tăng trưởng NPV≈0, không trừ khỏi dòng tiền): Δ OOS CI cụm mã N12 [+0,003; +0,068] · N24 [−0,004; +0,087] · N36 [+0,003; +0,100] · N60 [−0,000; +0,125]. CI khối năm loại 0 ở cả 4 N. IS còn TĂNG (PIC +0,10/+0,22/+0,22/+0,22 so với baseline cùng hỗ trợ +0,08/+0,18/+0,14/+0,14). Dấu giữ khi bỏ 2020–21 và khi bỏ 2022. Nó nhất quán với cơ chế Q2, nhưng **trượt (i) theo luật khoá (2/4, cần 3/4) ⇒ không tuyên bố là đã sửa được.** Hai ô trượt là biên (−0,004 và −0,000); không nới luật sau khi thấy số.
C2 và C6 (trừ khấu hao thay vì capex) cùng hướng nhưng yếu hơn. Biến thể dùng LN (C5) hay dữ liệu tươi (C8) không giúp ⇒ khớp với chẩn đoán "vấn đề nằm ở trừ capex thực".

Không kiểm được: cộng thu nhập tài chính / loại khoản một-lần (cache không có cột). Khấu hao là proxy EBITDA − EBITM × doanh thu TTM (≤0 ở 11% dòng engine-ok → loại khỏi C2–C7).

## Q4 — hệ quả cho DD (ĐỀ XUẤT, không sửa skill)

1. **Giảm trọng tâm V_dài như thước đo rẻ/đắt chéo-mã**, nhất là so giữa các ngành (phần giữa-ngành là phần đã mất; BĐS đảo dấu). Vẫn trình bày V_dài như "giá trị dòng tiền tự do sau toàn bộ đầu tư hiện tại" (nền thận trọng), không như ước lượng tâm.
2. **Cờ phân kỳ (HAI NỀN, display-only): thêm ngữ cảnh capex.** Khi V_dài < giá < V_ngắn VÀ capex/CFO cao (capex > khấu hao), phân kỳ nhiều khả năng do *capex tăng trưởng đang bị trừ như chi phí*. Dữ liệu OOS cho thấy nhóm này KHÔNG kém hơn (capex/CFO dự báo dương). Cờ nên ghi "phân kỳ do capex tăng trưởng (FCFE thấp vì đầu tư)" thay vì ngụ ý V_dài cảnh báo đắt.
3. **Dòng nhạy (tuỳ chọn, display-only):** in thêm V theo C4 (CFO3 − min(capex, khấu hao)) cạnh V_dài, gắn nhãn "chưa qua tiêu chí khoá, theo dõi". Không đổi tâm vùng giá.
4. Không có cơ sở để chuyển trọng số sang V_ngắn: dd_fwd_prelock đã kết luận V_ngắn trượt IS. Cả hai nền đều không ổn định qua hai giai đoạn.
5. **Theo dõi:** chạy lại `calc/analyze.py` khi có thêm 4 quý nhãn N24 (≈ Q4/2027). Nếu C4 đạt (i) trên OOS mở rộng mà không đổi luật ⇒ đề xuất đưa C4 vào engine qua quy trình quant-skeptic. Forward thật: `dd_fwd_prelock/calc/score_dd_zones_forward.py` (mốc 12 tháng 2027-10/11).

## Hạn chế / không kiểm được
- IS 16 quý; OOS N60 7 quý. Khối năm chỉ có 4 năm IS ⇒ CI năm thô. Nhãn ARTIFACT ở Q1 phản ánh lực thống kê thấp; mô tả (cửa sổ trượt, IS16–21/OOS22+) nghiêng về suy yếu thật từ as-of 2021+.
- "Capex dự báo dương OOS" là quan hệ thống kê 2020–25 (giai đoạn đầu tư công/KCN/năng lượng). Có thể là đặc trưng chế độ, không phải quy luật. Đây là lý do không nới luật cho C4.
- Lớp phán đoán DD, moat/NPV=0, fiinprox UNVERIFIED-PIT, ROE3Y/CF có thể bị restate theo vendor: không kiểm được (kế thừa dd-blend). ICB lấy từ snapshot hiện tại.
- Rank IC đo xếp hạng, không đo mức tâm.

## Kỷ luật & tái lập
- **N trials lựa chọn = 8** (Q3); Q1/Q2 là mô tả/kiểm định cơ chế. Cộng dồn chuỗi DD: 417 + 8 = **425**. PBO 0,29/0,43. DSR không áp dụng (metric không phải lợi suất).
- PIT: fin.time ≤ as-of (assert ở build_panel), lịch sử quý trong ext chỉ lấy dòng time ≤ fin_time. Giá chỉ là nhãn/thước đo. Không dùng profit_*, không ticker_prune; universe_pit.
- Hai lần chạy `analyze.py` cho cùng md5 `c341fb94e694b3979d448eb8c0ccc9f4` (`out/md5_run1.txt`, `md5_run2.txt`).
- Tính lại độc lập (`calc/recompute.py`, scipy rankdata + lstsq theo quý): PIC V_dài, CFO yield, FCFE yield, C4 ở N24/N36 IS/OOS — lệch tối đa 8e-17 (`out/recompute.csv`).
- Assert trong code: baseline = PIC_l dd_fwd_prelock (1e-9); V_dài = FCFE3·k(g) (1e-9); V_dài khớp engine (kế thừa common.load).

```
cd agents/Taylor/research/dd_fcfe3y_decay_20261111 ; PY=/home/trido/thanhdt/wc_venv/bin/python
$PY -W ignore calc/build_ext.py   # -> out/ext.parquet (~40s)
$PY -W ignore calc/analyze.py     # -> out/summary.json (~8 phút, B=1000)
$PY -W ignore calc/recompute.py   # -> out/recompute.csv
```
