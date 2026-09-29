# VÒNG 2 BAL — cơ chế EXIT/TÁI NHẬP adaptive theo market state
job `Taylor_20260909_112201` · 2026-09-09 · **PAPER-ONLY** · **VERDICT = NO-GO cả 4 chân**

Tiền đăng ký viết TRƯỚC khi chạy chân treatment nào: `PREREG.md` (N_trials = 4, 7 tiêu chí GO,
0 tham số tự do — mọi hằng số lấy từ quy ước production sẵn có). Không có chân nào khác trên trục
này trong job. Bus finding PREREG đã ghi trước khi có số.

## 1. Kết quả một dòng

**Cơ chế hoạt động ĐÚNG như thiết kế và vẫn LỖ.** Cả 4 luật thoát adaptive đều cho CAGR **thấp
hơn** cấu hình pin. Tiêu chí đầu tiên (C1: ΔCAGR > +0,385pp) trượt ngay ở mọi chân, nên 6 tiêu
chí còn lại chỉ mang tính tư liệu.

| chân | luật | CAGR % | **ΔCAGR pp** | ΔIS(14-19) | ΔOOS(20+) | Calmar | MaxDD % | Final NAV B |
|---|---|---|---|---|---|---|---|---|
| ctrl | pin R3 | 28,8627 | — | — | — | 1,6229 | −17,785 | 1.178,01 |
| **A** | state-exit tại commit | 27,6863 | **−1,176** | −0,758 | −1,499 | 1,6702 | −16,577 | 1.050,81 |
| **B** | trailing −20% thay hold 45 phiên | 27,8261 | **−1,037** | +1,116 | −3,103 | 1,3228 | −21,036 | 1.065,24 |
| **C** | thoát theo candidate clock k≥10 | 27,2549 | **−1,608** | −0,026 | −3,022 | 1,6538 | −16,480 | 1.007,42 |
| **D** | A + B | 27,1905 | **−1,672** | −1,856 | −1,422 | 1,3418 | −20,264 | 1.001,09 |

Chân control tái lập pin R3 **BYTE-IDENTICAL**: CAGR 28,8627% / Final NAV 1.178,0099B /
Calmar 1,6229 / MaxDD −17,785% · CSV md5 **`7d053e6201c9d107685ff4d1dd9d2d2a`** = trùng byte
artifact pin 2026-08-03. Self-check **0 VND** (cash-flow identity + final-NAV identity, cả sổ BAL
lẫn LAG) trên **cả 5 chân**.

## 2. Chấm theo 7 tiêu chí tiền đăng ký

| # | Tiêu chí | Ngưỡng | A | B | C | D |
|---|---|---|---|---|---|---|
| C1 | ΔCAGR full | > +0,385pp | ❌ −1,18 | ❌ −1,04 | ❌ −1,61 | ❌ −1,67 |
| C2 | Calmar ≥ 1,6229 | — | ✅ 1,670 | ❌ 1,323 | ✅ 1,654 | ❌ 1,342 |
| C3 | IS và OOS cùng dấu dương | — | ❌ cả 2 âm | ❌ IS+ / OOS− | ❌ cả 2 âm | ❌ cả 2 âm |
| C4a | LOYO ≤ 50% Σ\|delta\| theo năm | — | 2021 = 42,0% | 2020 = 21,5% | 2021 = 32,0% | 2021 = 23,0% |
| C4b | **LOWO (10 cửa sổ)** ≤ 50% \|delta\| | — | max 28,9% (W7-2024) | ❌ **102,1%** (W6-2021/10) | ❌ **56,1%** (W7-2024) | max 38,0% (W3); nhưng đoạn TRƯỚC cửa sổ đầu chiếm 56,5% |
| C5a | DSR vs **SR_ctrl**, N=4 | > 0,95 | **0,430** (chân tốt nhất B) ❌ | | | |
| C5b | PBO (CSCV S=16, 5 cấu hình) | < 0,5 | **0,611** ❌ | | | |
| C6 | Block bootstrap CI95 loại trừ 0 | — | ❌ [−2,66; +0,85] | ❌ [−3,34; +1,79] | ❌ [−3,43; +0,79] | ❌ [−3,57; +0,93] |
| C7 | Self-check 0 VND + ctrl md5 | — | ✅ | ✅ | ✅ | ✅ |

C4a/C4b chấm trên delta ÂM nên **không có ý nghĩa "concentration của edge"** — ghi lại để đủ 7
tiêu chí, không dùng để biện hộ. Cái đọc được: với B, **một cửa sổ duy nhất (2021-10 → 2024-01)
giải thích 102% tổng delta**; với C là W7-2024 (56,1%).

Điểm ước lượng bootstrap (pp/năm): A **−0,917** · B **−0,808** · C **−1,255** · D **−1,306**;
P(Δ>0) lần lượt 0,157 / 0,286 / 0,120 / 0,124.

⚠️ **Đọc DSR cho đúng.** `DSR vs 0 = 1,000000` là số VÔ NGHĨA ở đây — nó đúng với cả chân control.
Null trung thực là "có đánh bại chính cấu hình pin không" ⇒ **`DSR vs SR_ctrl = 0,430`**.

## 3. Cơ chế ĐÃ chạy đúng — bằng chứng, không phải giả định

Kiểm chứng trên sổ lệnh (`mech_2026.py`), sổ BAL, loại tier `CAPIT_*`:

| | ctrl | A | B |
|---|---|---|---|
| exit `TIME` (đồng hồ 45 phiên), toàn kỳ | **234** | 106 | 0 |
| exit `MODE_FLIP` (thoát theo state), toàn kỳ | 0 | **131** | 0 |
| exit `TRAIL` / `STOP`, toàn kỳ | 0 / — | — | **65 / 36** |
| 2026: ngày thoát các vị thế mở tháng 1-2 | **10-21/04** (12 `TIME`) | **23-27/02** (15 `MODE_FLIP`) | rải theo giá |

Chân A đã làm **chính xác** điều Phần 1 chỉ ra là thủ phạm: thay vì bị đồng hồ 45 phiên ép bán
ngày 10-21/04/2026 đúng đáy, nó thoát ngày 23-27/02 ngay sau khi DT5G commit về NEUTRAL. Luật
chạy đúng. **Nó vẫn không cứu được năm 2026.**

## 4. Vì sao sửa đúng thủ phạm mà vẫn không có lợi — hai cơ chế đối kháng

### (a) Thoát sớm trong NEUTRAL KHÔNG phải là giảm rủi ro — chỉ là ĐỔI rổ cổ phiếu

Thành phần sổ BAL cuối tháng, 2026 (`mech_exposure.py`), % NAV sổ:

| | ctrl stocks / park / cash | A stocks / park / cash |
|---|---|---|
| 31/01 | 30,5 / 0,0 / 69,5 | 32,9 / 0,0 / 67,1 |
| **28/02** | **97,2 / 2,0 / 0,8** | **9,2 / 63,5 / 27,2** |
| 31/03 | 80,6 / 13,6 / 5,8 | 11,5 / 62,0 / 26,6 |
| 30/04 | 10,6 / 69,2 / 20,2 | 24,9 / 59,5 / 15,6 |

Tiền A giải phóng **không thành tiền mặt** — `PARK_STATES="3:0.7"` đẩy 70% vào rổ custom30V, cũng
là cổ phiếu VN. Lợi suất sổ BAL theo tháng 2026:

| | 01 | 02 | 03 | 04 | 05 | 06 | **cả kỳ** |
|---|---|---|---|---|---|---|---|
| ctrl | +4,96 | **+3,97** | **−9,05** | **−0,76** | +1,02 | −1,87 | −0,91 |
| A | +6,34 | **−0,98** | **−6,86** | **+1,33** | +0,62 | −1,95 | −0,70 |

A tiết kiệm được **+2,19pp** tháng 3 và **+2,09pp** tháng 4 — đúng như chẩn đoán hứa. Nhưng nó
**trả lại −4,95pp ngay trong tháng 2**, vì lệnh bán rơi vào lúc sổ đang còn tăng và rổ parking
chạy chậm hơn nhóm đang giữ. **Ròng cả năm: +0,21pp.** Con số cứu được nhỏ hơn một bậc so với
"11,5pp chi phí của nhịp bỏ lỡ tháng 4" mà Phần 1 ước lượng — vì ước lượng đó so BAL với VNINDEX,
còn phương án thay thế thực tế không phải VNINDEX mà là **custom30V, thứ cũng rơi trong tháng 3**.

*(Ghi chú: stocks% của A hồi lên 24,9% cuối tháng 4 là do `RE_BACKLOG_BUY` — tier duy nhất có cổng
vào {3,4,5} nên vẫn mua được trong NEUTRAL. Đường "tái nhập trong NEUTRAL" đã tồn tại sẵn trong
production, chỉ hẹp.)*

### (b) Cùng luật đó phá các năm mà GIỮ QUA downgrade mới là đúng

Lợi suất sổ BAL theo quý 2021 — năm đóng góp lớn nhất toàn kỳ:

| | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| ctrl | 17,55 | 13,59 | **20,58** | **33,62** |
| A | 17,05 | 18,83 | **7,43** | **22,71** |
| C | 16,82 | 15,78 | 13,78 | **14,25** |

2021 DT5G ra-vào BULL bốn lần (4 trong 10 cửa sổ của Phần 1 nằm trong năm này). Mỗi lần commit
xuống, A bán; giá đi tiếp lên. Δ per-year 2021: **A −12,40pp, C −15,44pp, D −8,17pp**. 2024 lặp
lại nhẹ hơn (A −4,12; C −10,53).

**Đây là chi phí cấu trúc, không phải xui:** DT gate commit **sau giá 10 phiên**. Thoát tại commit
= bán sau khi cú giảm đã xảy ra, rồi đứng ngoài cú hồi. Nó biến một cược "giữ 45 phiên" thành một
cược **market-timing trên tín hiệu trễ 10 phiên** — đúng thứ mà DT5G được thiết kế để KHÔNG làm
(CLAUDE.md: *"DT5G là CHỐT RỦI RO FAIL-SAFE, không phải công cụ tăng lợi nhuận"*; hành động phòng
thủ duy nhất là CAP trần trạng thái, **re-risk thuần theo GIÁ**).

### (c) Chân C (candidate clock) tệ hơn chân A — hành động sớm hơn làm hại thêm

Clock candidate chỉ khác commit ở **3 đợt / 45 phiên** toàn bộ 12,5 năm (2018, 2021, 2024 — đều là
candidate CRISIS `need=25`, C thoát ở k=10 nên sớm hơn A 15 phiên). Ba đợt đó đủ để kéo ΔCAGR từ
−1,18 xuống **−1,61pp**, phần lớn từ 2024 (−10,53pp per-year). Kết luận khớp với chính báo cáo
hazard của DT gate (job `Taylor_20260710_122230`): **độ dài streak là thông tin YẾU**; front-run
cổng không được trả công.

### (d) Chân B (trailing) — đổi hình dạng rủi ro theo hướng xấu

Bỏ đồng hồ thời gian ⇒ vị thế thắng nằm lâu, chiếm slot (trần 12) và **chặn** lệnh mới ở cửa sổ
BULL kế: số lệnh mua BAL toàn kỳ rơi từ **1.480 → 831**. MaxDD xấu đi rõ (−17,8% → **−21,0%**),
Calmar 1,62 → **1,32**. Đặc biệt 2020: **−10,84pp** — vị thế cũ khoá vốn đúng lúc thị trường hồi.

## 5. Kiểm tra tính nhân quả của candidate clock (điều kiện chặn của chân C)

`dt_candidate_clock.py` phát chuỗi `(date, committed, cand, k, need)` bằng đúng vòng lặp tiến của
`macro_state_live._dt_4gate`. Hai self-check chạy thật, in ra log:
- `committed` == output cổng production trên toàn chuỗi: **0 mismatch** / 3.136 phiên.
- **PIT / no look-ahead**: cắt chuỗi tại 4 mốc (500 / 1.200 / 2.000 / 3.131 phiên), clock tính
  trên tiền tố phải trùng khớp clock chuỗi đầy đủ ⇒ **0 diff** ở cả 4 mốc.

Nguồn = bản copy của `vnindex_5state_tam_quan_v34b_clean` **nằm trong chính snapshot pin**
`bq_cache_asof20260729_postrestate` ⇒ **không có lệch vintage** (khác nợ kỹ thuật `bal_open_pcf.csv`
của vòng 1).

## 6. Sự cố harness đã bắt được và vá (ghi lại vì nó suýt tạo kết quả giả)

Lần chạy đầu, chân B và D **crash** `TypeError: simulate() got an unexpected keyword argument
'trailing_tiers'`, còn A/C chạy "thành công". Nguyên nhân: `pt_v23_audit_2014.py` tự
`sys.path.insert(0, WORKDIR)` **trước** khi import ⇒ bản copy nghiên cứu của
`simulate_holistic_nav.py` bị che, mọi chân âm thầm dùng file production. A/C không dùng tham số
mới nên **không có lỗi nào để thấy** — nếu B/D không tồn tại, kết quả A/C vẫn "chạy được" và vẫn
sai về mặt xuất xứ code. Đã vá bằng một dòng re-insert thư mục nghiên cứu lên đầu `sys.path`, rồi
**chạy lại CẢ 5 chân** (kể cả control) trên cùng code path. Control sau khi vá vẫn md5 trùng pin ⇒
bản copy trung thực.

## 7. Kết luận & khuyến nghị

1. **NO-GO cả 4 chân.** Không wire gì. `filter.json`, `macro_state_live.py`, production V2.4
   không bị đụng; toàn bộ output mang `AUDIT_EXP_TAG=baladapt*`.
2. **Chẩn đoán vòng 1 vẫn đúng, nhưng "sửa được thủ phạm" ≠ "có lợi".** Đồng hồ 45 phiên thật sự
   ép bán đúng đáy tháng 4/2026; thoát sớm đúng như mong muốn chỉ đổi được **+0,21pp** cho cả năm
   2026 và mất **−1,18pp/năm** trên toàn kỳ. Nguyên nhân là §4(a): trong NEUTRAL, "thoát" chỉ là
   đổi từ rổ momentum sang rổ custom30V — **không phải giảm rủi ro**.
3. **Hàm ý cho mandate của user.** Yêu cầu *"state đổi thì adapt ngay"* đã được kiểm định ở dạng
   đo được nhất có thể và **dữ liệu nói không**: adapt theo commit (A) mất 1,18pp/năm, adapt sớm
   hơn theo candidate (C) mất 1,61pp/năm. Cơ chế adapt **đã có sẵn và đang chạy đúng** trong
   production, chỉ không nằm ở chỗ dễ thấy: khi state rời BULL, tier BAL **tự động ngừng mở lệnh
   mới**, và vốn nhàn rỗi **tự động chảy vào custom30V** theo `PARK_STATES`. Thêm một luật bán
   cưỡng bức lên trên chỉ làm hệ bán sau giá 10 phiên.
4. **Trục "sửa cơ chế thoát/tái nhập của BAL" ĐÓNG.** Cộng với vòng 1 (H-EY NO-GO, và Phần 2:
   không indicator kỹ thuật nào sống OOS sau BH), hai hướng khả dĩ duy nhất cho BAL đều đã bị bác
   bằng tiền đăng ký. **Không đề xuất biến thể tiếp trên trục này.**
5. Điều còn lại đáng theo dõi (không hành động): `ey` lúc BAL vào lệnh trôi 0,15 (2019) → 0,059
   (2026). Nếu 2027 tiếp tục, đó mới là bằng chứng alpha decay; hiện Spearman(năm, ret) p = 0,960.
6. Nếu ai muốn đi tiếp bất chấp §7.4, hướng DUY NHẤT còn cơ sở nhân quả là thứ **vòng này cố ý
   không chạm**: nới cổng vào của BAL trong NEUTRAL (để có đường tái nhập thật, không phải qua
   parking). Đó là **đổi thiết kế**, cần tiền đăng ký riêng + user duyệt phạm vi, và N vẫn = 10.

## 8. Vật chứng

`PREREG.md` · `dt_candidate_clock.py` + `dt_candidate_clock_exp.csv` · `simulate_holistic_nav.py`
(copy nghiên cứu, +1 tham số `trailing_tiers`) · `adaptive_engine.py` (copy + overlay `ADAPT_MODE`)
· `run_leg.sh` · `run_{ctrl,A,B,C,D}.log` · `analyze.py` · `ab_metrics.csv` · `peryear.csv` ·
`perwindow.csv` · `mech_2026.py` · `mech_exposure.py`.
NAV CSV: `data/v23_golive_audit_..._exp_baladapt{ctrl,a,b,c,d}.csv`.
