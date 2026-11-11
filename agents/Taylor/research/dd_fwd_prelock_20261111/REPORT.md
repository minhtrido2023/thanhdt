**KẾT LUẬN (theo tiêu chí D khoá trước):** V_ngắn (nền lợi nhuận) **KHÔNG có thông tin bổ sung ổn định** so với V_dài. Lý do: trượt điều kiện (ii). Partial rank IC của V_ngắn trên IS 2016–19 chỉ dương ở 2/4 chân trời, và cả 4 chân trời đều sát 0 (−0,033 … +0,037). Điều kiện (i) OOS đạt ở 3/4 chân trời, (iii) đạt khi bỏ as-of 2020–21. ⇒ **DD giữ V_ngắn ở chế độ hiển thị-chỉ (phương án (a)). Không đề xuất blend.** Chọn w trên IS theo rank IC ra w* = 0.

Job Taylor_20261111_043843 · 2026-11-11 · Taylor · CHỈ NGHIÊN CỨU (không sửa dcf_valuation.py, skill, dd_price_zones.json, moat_tags.csv).
PRELOCK.md md5 `2b0763704928fae449389c2bbea0b9ae`, khoá 11:40:56 ICT, trước mọi lần chạy IC (`out/prelock_md5.txt`).
Panel tái dùng từ dd_blend (md5 `1de5145f…`, `out/inputs_md5.txt`).

## 1. Kết quả chính: biến thể khoá trước v0 (NI trung vị TTM 3 năm · ROE3Y vendor · g/ROE cắt [0,1])
Rank IC tính theo quý rồi lấy trung bình các quý. CI95 bootstrap cụm theo MÃ (B=1000). PIC là hệ số chuẩn hoá của hồi quy hạng hai biến trong từng quý.

| N | Split | Số quý / số dòng | IC V_ngắn | IC V_dài | **PIC V_ngắn** [CI mã] | CI cụm quý | PIC V_dài [CI mã] |
|---|---|---|---|---|---|---|---|
| 12 | IS | 16 / 1.314 | −0,016 | +0,058 | **−0,033** [−0,121; +0,054] | [−0,098; +0,038] | +0,068 [−0,018; +0,154] |
| 12 | OOS | 23 / 2.704 | +0,117 | +0,088 | **+0,102** [+0,041; +0,161] | [+0,044; +0,169] | +0,061 [−0,002; +0,120] |
| 12 | OOS bỏ 20–21 | 15 / 1.757 | +0,134 | +0,048 | **+0,129** [+0,058; +0,193] | | +0,013 |
| 24 | IS | 16 / 1.314 | +0,016 | +0,173 | **−0,026** [−0,128; +0,073] | [−0,081; +0,029] | +0,182 [+0,086; +0,284] |
| 24 | OOS | 19 / 2.254 | +0,141 | +0,074 | **+0,133** [+0,041; +0,211] | [+0,086; +0,180] | +0,039 [−0,043; +0,122] |
| 24 | OOS bỏ 20–21 | 11 / 1.307 | +0,139 | +0,038 | **+0,140** [+0,034; +0,243] | | −0,001 |
| 36 | IS | 16 / 1.314 | +0,041 | +0,162 | **+0,005** [−0,097; +0,121] | [−0,054; +0,068] | +0,162 [+0,053; +0,261] |
| 36 | OOS | 15 / 1.819 | +0,139 | +0,071 | **+0,131** [+0,023; +0,233] | [+0,081; +0,184] | +0,038 [−0,056; +0,134] |
| 36 | OOS bỏ 20–21 | 7 / 872 | +0,171 | +0,059 | **+0,165** [+0,038; +0,288] | | +0,016 |
| 60 | IS | 16 / 1.314 | +0,069 | +0,152 | **+0,037** [−0,101; +0,170] | [−0,030; +0,106] | +0,142 [+0,025; +0,259] |
| 60 | OOS | 7 / 777 | +0,073 | +0,047 | **+0,066** [−0,085; +0,219] | [+0,029; +0,115] | +0,032 [−0,111; +0,168] |

Tương quan hạng giữa V_ngắn và V_dài trong cùng quý là 0,22–0,31: hai nền khá độc lập với nhau.

**Chấm từng điều kiện D:**
- (i) OOS, PIC_s > 0 và CI cụm mã loại 0: ĐẠT ở N 12/24/36, trượt ở N 60 ⇒ **ĐẠT** (3/4).
- (ii) IS, PIC_s điểm > 0: chỉ dương ở N36 (+0,005) và N60 (+0,037), âm ở N12 và N24 ⇒ **TRƯỢT** (2/4).
- (iii) OOS bỏ as-of 2020–21: dương ở N 12/24/36 (15, 11 và 7 quý); N60 không kiểm được ⇒ **ĐẠT**.
- ⇒ **KHÔNG ĐẠT.**

**Đọc ý nghĩa:** dữ liệu cho thấy một sự **đảo chiều theo thời gian**, không phải thông tin bổ sung ổn định.
- Trên IS, V_dài mang thông tin (PIC_l +0,14…+0,18 ở N 24–60, CI loại 0), còn V_ngắn gần bằng 0.
- Trên OOS thì ngược lại: V_ngắn mang thông tin, còn V_dài tụt về +0,03…+0,06 (CI chứa 0).
- Hiệu IC (V_ngắn − V_dài) trên IS ở N24 là −0,157 [−0,287; −0,030]. Trên OOS bỏ 2020–21 ở N12 là +0,086 [+0,011; +0,157].
- Không nền nào thắng ổn định qua cả hai giai đoạn.

## 2. Chân kiểm soát co-về-giá (B): chốt chặn ĐẠT
- Định nghĩa: V_dài^c = MC0·(V_dài/MC0)^c. Hệ số c khớp độ phân tán với V_hh(w) trên IS: c(0,5) = 0,683, c(0,8) = 0,583. Thêm lưới c ∈ {0,25; 0,5; 0,65; 0,75}.
- **IC(V_dài^c) = IC(V_dài) chính xác**, |Δ| < 1e-12, cả ở số điểm lẫn trên 1000 mẫu bootstrap, với 6 giá trị c và 4 N (assert trong code). Như vậy rank IC không thưởng cho việc co V về phía giá. Mọi lợi thế của blend phải đến từ thông tin, không từ việc co thang đo.
- Mô tả lại phát hiện của skeptic (không dùng để kết luận). AEdm của chân co c=0,683 so với V_hh(0,5):
  - IS: 0,505/0,501/0,545/0,608 so với 0,530/0,524/0,567/0,591.
  - OOS: 0,491/0,508/0,505/0,566 so với 0,494/0,526/0,526/0,613.
  - Chân co (không dùng chút thông tin nào từ V_ngắn) thắng ở 7/8 ô; ô duy nhất thua là IS N60.
  - "V = giá" có AEdm 0,18–0,42 và thắng tất cả ⇒ xác nhận AEdm không phải thước đo tâm giá trị.
- **Blend theo rank IC.** Trung bình IC trên IS theo w (4 N): w=0: 0,136 · 0,3: 0,136 · 0,5: 0,124 · 0,8: 0,083 · 1: 0,028.
  - ⇒ w* = 0, tức V_hh(w*) ≡ V_dài, nên Δ so với V_dài = 0.
  - So với V_ngắn trên OOS: Δ âm ở cả 4 N, CI chứa 0 (ví dụ N24 −0,067 [−0,156; +0,031]).
  - Không thắng cả hai nền thuần ⇒ **không có đề xuất blend hợp lệ.**
  - Trên OOS, IC tăng dần theo w (N24: 0,074 → 0,106 ở w=0,5 → 0,141 ở w=1). Đây là cùng một sự đảo chiều như §1, chọn trên IS không bắt được nó.

## 3. Ổn định theo năm as-of và theo DT5G (C) — `out/ic_by_year.csv`
PIC_s (V_ngắn) theo năm, kèm CI cụm mã. Ô **in đậm** là ô có CI loại 0:

| Năm | N12 | N24 | N36 | N60 |
|---|---|---|---|---|
| 2016 | −0,144 | −0,102 | −0,099 | −0,075 |
| 2017 | +0,045 | +0,027 | +0,128 | +0,195 |
| 2018 | −0,129 | −0,104 | −0,076 | −0,042 |
| 2019 | +0,094 | +0,075 | +0,068 | +0,070 |
| 2020 | +0,025 | +0,104 | +0,110 | +0,034 |
| 2021 | +0,078 | +0,143 | +0,091 | +0,110 |
| 2022 | **+0,255** | **+0,245** | **+0,228** | – |
| 2023 | **+0,210** | +0,092 | +0,083 | – |
| 2024 | +0,026 | +0,063 | – | – |
| 2025 | −0,009 | – | – | – |

- **2020–21 (Covid-bull) KHÔNG phải nguồn thông tin của V_ngắn.** PIC_s của 2020–21 dương nhưng nhỏ, CI chứa 0. Bỏ hai năm này, OOS còn mạnh hơn (§1).
- Thông tin tập trung ở **as-of 2022 (và 2023 với N12)**, giai đoạn thị trường sập 2022.
  - Theo DT5G tại as-of: các quý **BEAR** có PIC_s +0,251 [+0,146; +0,345] (N12), +0,217 (N24) và +0,202 (N36), CI đều loại 0.
  - Quý **NEUTRAL** có PIC_s −0,002 / +0,006 / +0,021, tức ≈ 0. CRISIS và BULL dương nhỏ, CI chứa 0.
  - Ngược lại, PIC V_dài mạnh nhất ở NEUTRAL (+0,145 [+0,064; +0,228] ở N24).
- Hậu kiểm mô tả (ngoài prelock, chỉ số điểm, không có CI):
  - Bỏ as-of 2022, PIC_s của OOS còn +0,070 / +0,103 / +0,095 / +0,066 (N 12/24/36/60).
  - Bỏ cả 2022–23, còn +0,032 / +0,107 / +0,100 / +0,066.
  - Toàn kỳ: +0,046 / +0,060 / +0,066 / +0,046.
  - ⇒ Phần dương OOS không chỉ do một năm. Nhưng IS 2016–19 dao động dấu theo năm: âm 2016, 2018; dương 2017, 2019.

## 4. Biến thể V_ngắn (E): 12 = NI {trung vị 3 năm · TTM · TB 5 năm} × ROE {vendor · tự tính} × cắt {[0,1] · [0,0,8]}
- ROE tự tính = NI / (BVPS × OShares) của dòng fin cuối, ghép PIT. Trung vị tỉ số so với ROE3Y vendor là 0,83 (kiểm đơn vị đạt).
- Trên IS, PIC_s của **mọi** biến thể nằm trong [−0,053; +0,053]. Trên OOS, mọi biến thể đều dương: +0,036 … +0,183.
- **Biến thể chọn trên IS** (cực đại PIC_s trung bình 4 N) là v* = TTM · ROE tự tính · cắt 1, với IS +0,019. Nó **trượt (i)**: CI OOS chỉ loại 0 ở N36.
  - PBO (CSCV, 70 cách chia, 8 khối năm 2016–23) = **0,69 ở N12** và 0,31 ở N36: chọn biến thể theo IS ở N12 là overfit.
  - Theo luật khoá trước, kết luận đi theo v0.
- **Chỉ 1/12 biến thể đạt cả (i)–(iii): TTM · ROE vendor · cắt 0,8.** Biến thể này **không** phải lựa chọn của IS.
  - PIC_s IS của nó là −0,012 / +0,012 / +0,026 / +0,040, CI chứa 0 ở cả 4 N.
  - 1 lần đạt trong 12 lần thử, không qua lựa chọn IS ⇒ không đủ làm bằng chứng. Ghi nhận, không đề xuất.
- **Cắt [0, 0,8] (mô tả):** so với [0,1], nó tăng PIC_s OOS ở mọi cặp NI×ROE (ví dụ v0 N24: 0,133 → 0,171) và tăng độ phủ OOS N12 (2.704 → 2.890 dòng), vì tránh được việc V_ngắn sụp về 0 khi ROE ≤ g.
  - Trên IS nó không tạo khác biệt có ý nghĩa.
  - Nếu DD vẫn hiển thị V_ngắn, cắt 0,8 là lựa chọn hợp lý về **cơ chế**: không cho V_ngắn = 0 chỉ vì ROE ≤ g. Đây không phải lý do thống kê.
- Kiểm bền trên giao các biến thể (cùng dòng: N12 3.521 · N24 3.121 · N36 2.724 · N60 1.788) cho cùng hình ảnh: PIC_s IS ≤ 0,054 ở mọi biến thể, OOS +0,029…+0,143 (`ic_summary.json` → `common_support_PIC_s_point`).

## 5. Theo dõi forward thật (G): `calc/score_dd_zones_forward.py`
- **Đầu vào:** sổ `kb/dd_price_zones.json`, lấy bản rev cao nhất cho mỗi (mã, dd_date). Hiện có 28 cặp, 27 cặp chấm được (1 cặp center null). dd_date từ 2026-10-26 đến 2026-11-10.
- **Giá:** Close điều chỉnh từ `data/bq_cache/ticker`, bản sao của `tav2_bq.ticker` (sync 23:45 ICT).
- **Đầu ra:** x0 = log(P/center), AE_N, tỉ lệ khoảng cách đã đóng, nằm trong vùng hay không, có chạm tâm hay không, rank IC theo tháng dd_date (cần ≥ 8 mã), cờ `insufficient_N`.
- **Kiểm tra:** `calc/selfcheck_forward.sh` dùng sổ giả 2025-01-15 với 10 mã. Nó kiểm luật chọn rev cao nhất, TR_12 khớp với tra độc lập tới 1e-12, và cờ N24. **PASS** ở cả 3 môi trường: TZ mặc định, `env -u TZ`, TZ=America/New_York.
- Chạy trên sổ thật hôm nay: n_full = 0 ở mọi N (đúng như dự kiến).
- **Mốc chấm đầu tiên:**

| N | Mốc đầu → mốc đủ | Ghi chú |
|---|---|---|
| 3 tháng | 2027-01-29 → 2027-02-10 | chỉ MÔ TẢ |
| 6 tháng | 2027-04-29 → 2027-05-10 | mô tả |
| **12 tháng** | **2027-10-29 → 2027-11-10** | mốc chấm đầu tiên có nghĩa |
| 24 tháng | 2028-10 → 2028-11 | |

- Với ~27 mã chia theo 11 ngày DD, rank IC theo từng tháng sẽ rất nhiễu. Nên gộp toàn sổ khi chấm.

## 6. Hạn chế
- IS chỉ có 16 quý, OOS N60 chỉ 7 quý. CI cụm quý lạc quan vì nhãn N > 3 tháng chồng lấp giữa các quý.
- 2022 là một năm có trọng số lớn. Hậu kiểm bỏ 2022 vẫn dương ở OOS, nhưng đó là số ngoài prelock và không có CI.
- PIC V_dài OOS gần 0 là một phát hiện riêng: nền FCFE3y production mất thông tin xếp hạng sau 2020. Cần theo dõi, nhưng ngoài phạm vi job này.
- Vẫn kế thừa các hạn chế của dd-blend: lớp moat/NPV=0 không kiểm định được (không có PIT), fiinprox UNVERIFIED-PIT, ROE3Y vendor có thể bị restate. ICB lấy từ snapshot hiện tại (chỉ dùng để loại ngành tài chính).
- Rank IC đo khả năng **xếp hạng** giữa các mã, không đo mức tâm. Một V có IC tốt vẫn có thể lệch mức.

## 7. Kỷ luật & tái lập
- **N trials lựa chọn = 23** (12 biến thể + 11 w). Phân theo năm, DT5G, c và hậu kiểm bỏ 2022 là mô tả, không dùng để chọn. Cộng dồn với dd-blend: 394 + 23 = 417.
- PBO: 0,69 (N12) / 0,31 (N36) trên 12 biến thể. DSR không áp dụng vì metric không phải lợi suất.
- Chạy `ic_analysis.py` hai lần cho cùng md5:
  - `ic_summary.json` `b24bc63e0499e77d1c3a7433295cf68c`
  - `ic_by_year.csv` `f2a5daa944b401630b6c0f05013731c8`
  - `ic_variants.csv` `17fecdc1ecacbd7fec6f76342d2dfd33`
  - (`out/md5_ic_run1.txt`, `run2.txt`)
- **Tính lại độc lập** (scipy spearmanr + lstsq theo từng quý, không dùng hàm lõi): IC_s, IC_l, PIC_s, PIC_l ở N12 và N36, cho IS / OOS / OOS22, khớp tới 3 chữ số thập phân.
- Các assert trong code: v0 ≡ V_s của dd-blend (lệch 0); V_dài khớp engine (6,7e-16); PIT ghép vốn chủ (eq.time ≤ fin_time); đơn vị ROE; chốt chặn chân co.
- Không dùng profit_*, không ticker_prune. Giá chỉ là nhãn. quant-skeptic chưa chạy (Mike sẽ chạy).

```
cd agents/Taylor/research/dd_fwd_prelock_20261111/calc ; PY=/home/trido/thanhdt/wc_venv/bin/python
$PY -W ignore ic_analysis.py           # -> out/ic_summary.json, ic_by_year.csv, ic_variants.csv (~2 phút)
$PY -W ignore score_dd_zones_forward.py # -> out/fwd/ (chấm forward; --asof để cắt ngày)
./selfcheck_forward.sh
```
