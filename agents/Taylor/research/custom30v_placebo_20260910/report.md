# VÒNG 5 — custom30V: THÍ NGHIỆM PHÂN RÃ (placebo) nguồn gốc +2,62pp của L1b
job `Taylor_20260909_165335` · 2026-09-10 · **PAPER-ONLY, KHÔNG WIRE GÌ**
Tiền đăng ký: `PREREG.md` (md5 `6c11b1bc908cc74d18bda86b44b3e243`), viết **trước** khi chạy chân nào.

> **Vòng này không có verdict GO/NO-GO** — nó không đi tìm chân để wire. Deliverable là một phép
> cộng sổ. Đúng như PREREG §0 khai trước: **mọi chân đều trượt DSR và mọi CI95 ở cấp NAV đều ôm 0**;
> điều đó không làm hỏng phân rã, nó là kích cỡ mẫu của bài toán.

---

## 0. Trả lời thẳng câu hỏi

**(Y) THÊM TÊN RẺ chiếm ưu thế. (X) PHA LOÃNG NGÀNH không đóng góp gì dương — ở cấp rổ nó ÂM.**

Hai cấp đo, cùng một dấu cho (Y), ngược dấu cho (X):

| | TỔNG (L1b) | **ΔP1 = pha loãng thuần** | **ΔP2 = tên mới** | tương tác |
|---|---|---|---|---|
| **cấp NAV** (V2.4 đủ: park sizing + trần 20%-ADV + tiền mặt) | +2,621pp | **+0,622** (23,7%) | **+1,303** (49,7%) | +0,695 (26,5%) |
| **cấp RỔ gross** (chính cái selector đổi) | +6,325pp | **−3,064** (−48,4%) | **+5,731** (+90,6%) | +3,658 (57,8%) |

- Theo **luật đọc chốt trước (PREREG §1, neo trên số NAV)**: **HỖN HỢP** — ΔP2 = 49,7% TỔNG (dưới
  ngưỡng 60%), ΔP1 = 23,7% (dưới ngưỡng 40%). Không gán nhãn (X)/(Y) theo luật đó. **Ghi đúng như
  luật đã chốt, không sửa luật sau khi thấy số.**
- Bằng chứng **BỔ SUNG, không nằm trong luật tiền đăng ký** (nêu rõ để không lẫn): ở cấp **rổ
  gross** — nơi selector thực sự tác động, không bị tầng park/ADV làm nhiễu — hướng dứt khoát hơn
  nhiều: `P(ΔP2 > ΔP1) = **0,996**`, `P(ΔP1 < 0) = 0,845`, và **ΔP2 là thành phần DUY NHẤT có CI95
  loại trừ 0** (`[+0,05; +8,30]`, P(>0)=0,976).

**Tỷ lệ phân rã không đo được chính xác.** Bootstrap chung (cùng block cho mọi chân) ở cấp NAV cho
`%ΔP1` CI95 **[−52%; +91%]** và `%ΔP2` CI95 **[−46%; +135%]**, `P(ΔP2 > ΔP1) = 0,718`. Con số
"23,7% / 49,7% / 26,5%" là **ước lượng điểm**, không phải một phép chia đã xác lập.

---

## 1. Tiên quyết đã đạt (PREREG §6)

| kiểm tra | kết quả |
|---|---|
| md5 CSV control vs pin R3 | `7d053e6201c9d107685ff4d1dd9d2d2a` = **TRÙNG BYTE** |
| ctrl CAGR / NAV / Calmar / MaxDD vs pin | 28,8627 / 1.178,0099B / 1,6229 / −17,785 — **trùng từng chữ số** |
| `self-check 0 VND` (BAL + LAG, cash-flow **và** final-NAV identity) | **8/8 chân** |
| dump `n_fin` từ NAV đầy đủ vs từ `build_pit` | **trùng từng dòng** (ctrl, L1b) |
| bẫy `sys.path` vòng 2 | `sel_engine.py` re-insert thư mục vòng 5; control đi qua chính đường đó |

## 2. Cơ chế chạy ĐÚNG THIẾT KẾ — kiểm chứng, không giả định

| chân | pool | `n_fin` TB/kỳ | khớp mục tiêu |
|---|---|---|---|
| ctrl | 60 | **9,958** | — |
| L1b | 120 | **6,229** | — |
| P1d / P1r1 / P1r2 | 60 | **6,229** | = L1b **50/50 kỳ** |
| P2d / P2r1 / P2r2 | 120 | **9,958** | = ctrl **50/50 kỳ** |

Khớp **tuyệt đối từng kỳ** (48/48 kỳ có dữ liệu, cộng 2 kỳ warm-up rỗng đầu 2014 → 50/50 dòng),
cả hai chiều, không kỳ nào phải cắt vì thiếu tên tài chính trong pool
(pool 60 có TB 15,1 tên tài chính; pool 120 có 20,6). `%tên tài chính` xác nhận lại độc lập bằng
quy ước `route_asof` khác: ctrl 33,19% → P1* **20,76%** (= L1b), P2* **33,19%** (= ctrl).

### 2b. ⚠️ Ghim SỐ ĐẾM không ghim được TRỌNG SỐ — giới hạn thật của phân rã này

| chân | %tên tài chính | **%TRỌNG SỐ tài chính** | %trọng số BANK |
|---|---|---|---|
| ctrl | 33,19 | **52,81** (OOS 71,36) | 49,14 |
| L1b | 20,76 | **39,48** (OOS 63,46) | 37,13 |
| **P1d** | 20,76 *(= L1b)* | **34,18** *(≠ L1b, thấp hơn 5,3pp)* | 33,11 |
| **P2d** | 33,19 *(= ctrl)* | **59,87** *(≠ ctrl, CAO hơn 7,1pp)* | 52,95 |

`BASKET_PLACEBO_FIN` khớp **số tên**, không khớp **tiền**. Vì trọng số là mcap-cap-0,10, đổi *tên nào*
đổi luôn *bao nhiêu tiền*. ⇒ P1 hơi **quá liều** pha loãng (theo tiền) và P2 **không** trả ngành về
đúng mức ctrl mà **vượt lên** 59,87%. Phải đọc phân rã với sai số đó, và đó là một lý do nữa khiến
số dư "tương tác" không nhỏ.

## 3. Bảng A/B đầy đủ — cấp NAV

| chân | CAGR | ΔCAGR | MaxDD | Calmar | Sharpe | ΔIS | ΔOOS |
|---|---|---|---|---|---|---|---|
| ctrl | 28,8627 | — | −17,785 | 1,6229 | 1,832 | — | — |
| L1b | 31,4835 | **+2,621** | −14,954 | 2,1054 | 2,053 | +1,44 | +3,75 |
| **P1d** | 29,4847 | **+0,622** | −16,825 | 1,7524 | 1,913 | **−0,66** | +1,85 |
| **P2d** | 30,1661 | **+1,303** | −15,516 | 1,9442 | 1,973 | +1,11 | +1,48 |
| P1r1 | 29,0490 | +0,186 | −17,611 | 1,6495 | 1,868 | −0,16 | +0,51 |
| P1r2 | 28,7712 | −0,091 | −16,769 | 1,7157 | 1,874 | −1,39 | +1,15 |
| P2r1 | 28,8184 | −0,044 | −17,185 | 1,6769 | 1,894 | +0,04 | −0,12 |
| P2r2 | 28,9250 | +0,062 | −17,914 | 1,6146 | 1,894 | +0,73 | −0,57 |

Không phải đổi mức rủi ro: `|Δw_equity|` ≤ **0,23pp** mọi chân (ngưỡng 2pp). Turnover: P1d ×1,04 ·
P2d ×1,18 · L1b ×1,20 — dưới trần 1,5×; riêng 2 chân P2 ngẫu nhiên ×1,43-1,47 (vẫn dưới trần).

**Thống kê, đúng như khai trước:** DSR vs SR_ctrl **trượt 0,95 ở TẤT CẢ** (L1b 0,778 · P2d 0,687 ·
P1d 0,611 · random 0,55-0,59). Mọi CI95 bootstrap cấp NAV **ôm 0**. PBO CSCV (S=16, 8 config)
**0,0275**. Tập trung LOYO: L1b sạch (năm 0,24 / cửa sổ 0,37); **P1d 0,87 / 0,56** và **P2d 0,63 /
0,57** đều vượt 0,5 — tức bản thân từng delta con nhỏ so với dao động năm-qua-năm; các chân ngẫu
nhiên tệ hơn nhiều (1,5-11,8). Đây là lý do §0 nói tỷ lệ phân rã là ước lượng điểm.

## 4. Cấp RỔ GROSS — nơi câu trả lời rõ hơn hẳn

Không tiền mặt, không park sizing, không trần ADV, không phí: đúng chuỗi lợi suất của **cái rổ**.
(Tái lập bằng chính vòng lặp trọng số của `build_pit`, self-check lệch tương đối **2,2e-16**; và
**tái lập byte-identical** giữa 2 lần chạy độc lập sau khi vá lỗi cache ở §6.)

| chân | CAGR rổ | Δ | MaxDD rổ | vol | Sharpe |
|---|---|---|---|---|---|
| ctrl | 34,926 | — | −40,01 | 24,25 | 1,368 |
| L1b | 41,251 | **+6,325** | −48,03 | 23,09 | 1,626 |
| **P1d** | 31,861 | **−3,064** | −43,39 | 23,35 | 1,312 |
| **P2d** | 40,657 | **+5,731** | −46,07 | 24,13 | 1,548 |
| P1r (TB 2 seed) | 31,609 | −3,317 | — | — | — |
| P2r (TB 2 seed) | 36,866 | +1,940 | — | — | — |

Block bootstrap chung (L=63, B=4000, cùng chỉ số cho mọi chân), pp/năm:

| | điểm | CI95 | P(>0) |
|---|---|---|---|
| TỔNG | +4,56 | [−1,45; +10,62] | 0,934 |
| **ΔP1 pha loãng** | **−2,30** | [−6,91; +1,98] | 0,155 |
| **ΔP2 tên mới** | **+4,14** | **[+0,05; +8,30]** | **0,976** |
| tương tác | +2,71 | [−0,85; +6,51] | 0,930 |

*(Ước lượng điểm bootstrap thấp hơn Δ toàn mẫu — +4,14 vs +5,73pp cho ΔP2 — vì bootstrap cộng
**log-return** rồi quy về năm, còn bảng trên là hiệu **CAGR**; cùng chênh lệch xuất hiện ở cấp NAV
(L1b: +2,01 bootstrap vs +2,62 CAGR) và ở vòng 4. Dấu và thứ tự không đổi.)*

**Pha loãng ngành, một mình nó, làm rổ TỆ ĐI trên mọi chiều gross**: CAGR −3,06pp, MaxDD sâu hơn
3,4pp, Sharpe 1,31 < 1,368. Cái +0,62pp mà P1d thu được ở cấp NAV **không đến từ rổ tốt hơn** — nó
đến từ đường đi (per-year: 2022 +3,96pp, 2025 +4,44pp, bù cho 2017 −4,96pp; LOYO 0,87 = một năm
chiếm 87% delta). Không nên gọi đó là edge.

## 5. Chân NGẪU NHIÊN nói một điều KHÁC hẳn prior — và nó quan trọng

Prior khai trước (PREREG §3a): *"P1r ≈ P1d, P2r ≈ P2d"*, dựa trên vòng 4 L3 (đổi *tên ngân hàng*
bằng lens Gordon = +0,31pp, dưới sàn nhiễu). **Prior SAI.**

| | ΔP1 | ΔP2 | tương tác |
|---|---|---|---|
| mode=`top` (giữ tài chính điểm cao nhất) | +0,622 | +1,303 | +0,695 (26,5%) |
| mode=`random` (giữ tài chính ngẫu nhiên) | **+0,047** | **+0,009** | **+2,564 (97,8%)** |

Bốc ngẫu nhiên 6/15 tên tài chính thay vì giữ 6 tên điểm cao nhất **xoá sạch cả hai hiệu ứng**;
phân rã cộng tính sụp hoàn toàn (97,8% rơi vào số dư). Kết luận đúng: **thứ hạng của chính
`yieldcombo` bên trong nhóm tài chính CÓ mang thông tin** — phá nó là mất hết.

Không mâu thuẫn với L3: L3 hỏi *"có lens NÀO KHÁC tốt hơn 1/PE không"* → **không**. Vòng này hỏi
*"thứ tự của 1/PE trong nhóm ngân hàng có phải ngẫu nhiên không"* → **không, nó có thật**.

## 6. ⚠️ Một lỗi TRONG HARNESS PHỤ của chính tôi — bắt được, đã vá, và đáng thành luật

`wc_env.sh` export **`BQ_LOCAL_CACHE=data/bq_cache`** — cache **SỐNG**, cron ghi đè lúc 23:45 ICT.
`basket_probe.py` bản đầu dùng `os.environ.setdefault("BQ_LOCAL_CACHE", "<snapshot ghim>")` **sau
khi** `wc_env.sh` đã export ⇒ `setdefault` **không ghi đè được**, probe âm thầm đọc cache sống đang
bị cron viết dở. Triệu chứng: chuỗi lợi suất rổ gross của **cùng chân ctrl** ra 3 giá trị khác nhau
ở 3 lần chạy (level 33,46 / 32,76 / 36,14) trong khi `members`, ADV, `fin_w`, MaxDD **giống hệt** —
đủ giống để không ai nghi ngờ nếu chỉ nhìn một lần chạy.

- **Chân NAV đầy đủ KHÔNG bị ảnh hưởng**: `run_leg.sh` truyền `BQ_LOCAL_CACHE=` tường minh trên
  dòng lệnh `env`, và ctrl tái lập pin R3 byte-identical qua 3 lần chạy độc lập (vòng 3, 4, 5).
- Sau khi gán cứng: 2 lần chạy ctrl độc lập cho chuỗi **giống nhau tuyệt đối** (`max|diff| = 0,0`).
- **Luật rút ra (đề xuất cho `coding_guidelines`)**: script nghiên cứu ghim snapshot BQ **phải GÁN
  CỨNG** `os.environ["BQ_LOCAL_CACHE"]`, không bao giờ `setdefault` — vì `wc_env.sh` luôn export
  biến này trước. Và phải **in ra cache đang dùng** (đã thêm). Nếu số của bạn "gần đúng" mà không
  tái lập được từng byte, hãy nghi cache trước khi nghi mô hình.

## 7. THANH KHOẢN — kết quả vận hành, và nó phủ định giả thuyết của dispatch

| chân | ADV rổ trung vị | sức park 20%/ngày | vs ctrl |
|---|---|---|---|
| ctrl | **1.743,7B/ngày** | 348,7B | — |
| **P1d** (pool 60, ít tài chính) | **1.329,5B** | 265,9B | **−23,8%** |
| P1r1 / P1r2 | 1.379,5B / 1.345,1B | 275,9B / 269,0B | −20,9% / −22,9% |
| **P2d** (pool 120, ngành như ctrl) | 971,8B | 194,4B | −44,3% |
| P2r1 / P2r2 | 824,1B / 841,4B | 164,8B / 168,3B | −52,7% / −51,8% |
| **L1b** (pool 120) | **510,3B** | 102,1B | **−70,7%** |

Dispatch đặt giả thuyết: *"P1 giữ pool 60 nên PHẢI giữ được thanh khoản gần ctrl; nếu P1 thu được
phần lớn edge mà không mất thanh khoản thì đó là kết quả vận hành lớn nhất của cả 5 vòng."*
**Cả hai vế đều không xảy ra**: P1 chỉ thu 23,7% delta ở cấp NAV (và **âm** ở cấp rổ), **và** vẫn
mất 23,8% thanh khoản dù pool không đổi.

**Vì sao — và đây mới là điều đáng nhớ:** giữ nguyên pool 60 **không** giữ được thanh khoản, bởi vì
**chính ngân hàng LÀ nguồn thanh khoản**. Cắt tỷ trọng tài chính từ 52,81% xuống 34,18% buộc rổ
phải lấy tên sâu hơn trong bảng xếp hạng thanh khoản của **cùng** pool 60 ⇒ −24% ADV. Overweight
ngân hàng và thanh khoản của xe đỗ tiền **là cùng một hiện tượng**, không phải hai thứ đánh đổi
được độc lập. Mọi luật giảm ngân hàng — trần ngành, nới pool, hay ép đếm — đều phải trả giá này.

## 8. Hệ quả cho quyết định của user (chính sách 2026-09-09: giảm ngân hàng là mục tiêu tự thân)

User đã chốt: rổ đỗ tiền overweight ngân hàng **không phải chủ ý**, nên giảm nó **không cần biện
minh bằng CAGR**. Với khung đó, con số đáng giá nhất của vòng này **không phải** phân rã, mà là
**giá phải trả để de-bank**:

| nếu muốn | cách rẻ nhất đo được | %trọng số tài chính | %trọng số BANK | ΔCAGR NAV | ADV |
|---|---|---|---|---|---|
| giảm ngân hàng, **giữ pool 60** | ép đếm = P1d | 52,81 → **34,18** (−18,6pp) | 49,14 → **33,11** (−16,0pp) | **+0,62pp** (CI [−0,68; +1,73]) | −23,8% |
| giảm ngân hàng, nới pool | L1b | 52,81 → 39,48 | 49,14 → 37,13 | +2,62pp (CI [−0,12; +3,98]) | **−70,7%** |
| giảm ngân hàng bằng **cắt trọng số** | `fincap` 0,30-0,55 (07-14) | — | — | **−0,32 … −0,84pp** | ~0 |

Đọc thẳng: **cắt 16pp trọng số ngân hàng bằng cách ép SỐ ĐẾM tốn gần như KHÔNG GÌ ở cấp NAV**
(+0,62pp, không phân biệt được với 0 — và các chân ngẫu nhiên cùng mức cắt cũng cho ≈0: +0,19 /
−0,09). Đó là câu trả lời định lượng cho mục tiêu user nêu, và nó **khác hẳn** `fincap` (cắt trọng
số trên **cùng tập tên** — mất tiền thật, đã đo 4 lần năm 07-14). Giá thật của việc de-bank không
phải lợi nhuận, mà là **−24% thanh khoản xe đỗ tiền** (348,7B → 265,9B/ngày ở NAV 50B).

### Dạng luật để Mike/user cân nhắc vòng sau — CHỈ ĐỀ XUẤT, KHÔNG WIRE, CHƯA BACKTEST
PREREG §5.6 nói: *nếu (X) chiếm ưu thế* thì đề xuất trần ngành trong pool 60. **(X) KHÔNG chiếm ưu
thế** (nó âm ở cấp rổ), nên tôi **không** đề xuất trần ngành như một cách tăng lợi nhuận. Nếu user
vẫn muốn giảm ngân hàng vì lý do cấu trúc, dạng đúng theo dữ liệu vòng này là:

> **trần theo SỐ TÊN, không phải theo trọng số**: giới hạn số tên BANK+INSURANCE+SECURITIES trong
> top-30 ở mức `k` (P1d tương đương `k` trung bình ≈ 6), giữ nguyên pool 60, giữ nguyên
> `yieldcombo` chọn **tên tài chính điểm cao nhất** trong hạn mức đó.

Ba điều kiện bắt buộc trước khi ai đó backtest luật này: (a) **phải giữ thứ hạng** — §5 chứng minh
bốc ngẫu nhiên xoá sạch hiệu ứng; (b) `k` **phải chốt trước** bằng lý do cấu trúc, không quét — quét
`k` là tuning và sẽ chết ở DSR y hệt vòng 4; (c) phải khai trước rằng kỳ vọng ΔCAGR là **≈ 0**,
mục tiêu là hồ sơ tập trung ngành, và phải in bảng ADV. Đó là một **tiền đăng ký MỚI**, không phải
phần tiếp của vòng này.

## 9. Kết luận

1. **(Y) thêm tên rẻ chiếm ưu thế; (X) pha loãng ngành âm ở cấp rổ.** Theo luật NAV chốt trước:
   *hỗn hợp*, ΔP2 gấp ~2,1× ΔP1. Ở cấp rổ gross: ΔP2 = +90,6% TỔNG với CI loại trừ 0, ΔP1 = −48,4%.
   ⇒ **132 tên đã qua cổng chất lượng nhưng chưa bao giờ được chấm điểm định giá** là nguồn thật
   của +2,62pp, không phải việc rổ có ít ngân hàng hơn.
2. **Tỷ lệ phân rã KHÔNG đo chính xác được** với 12,5 năm / 48 kỳ: `%ΔP1` CI [−52%; +91%].
   Đừng ai trích "23,7% / 49,7%" như một con số đã xác lập.
3. **Thứ hạng `yieldcombo` bên trong nhóm tài chính có thông tin** (mode=random xoá sạch cả 2 hiệu
   ứng) — prior của tôi sai, ghi lại tường minh.
4. **Không có đòn bẩy rẻ.** Ngân hàng = thanh khoản; giảm ngân hàng luôn trả bằng ADV, kể cả khi
   giữ nguyên pool (−24%). Nới pool cho +2,62pp thì trả −71%.
5. **Không wire gì. Không đề xuất chân nào để wire.** Mọi chân trượt DSR và mọi CI cấp NAV ôm 0 —
   đúng như PREREG §0 khai trước; đó là *chưa chứng minh được*, không phải *đã bác bỏ*.
6. Bắt được và vá một lỗi cache trong harness phụ của chính vòng này (§6) — chân NAV không bị ảnh
   hưởng, đã chứng minh bằng md5 pin + tái lập byte-identical.

**Artifacts:** `PREREG.md` · `custom_basket.py` (bản copy nghiên cứu; `BASKET_PLACEBO_MODE` +
`BASKET_FINCOUNT_DUMP`, cả hai mặc định OFF ⇒ byte-identical) · `sel_engine.py` · `run_leg.sh` ·
`basket_probe.py` · `analyze.py` / `analyze_out.txt` · `decomp_ci.py` / `decomp_ci_out.txt` ·
`decomp_gross.py` / `decomp_gross_out.txt` · `ab_metrics.csv` · `decomp.csv` · `gross_metrics.csv` ·
`fincount_{ctrl,L1b,P1d,P2d,P1r1,P1r2,P2r1,P2r2}.csv` + `fincount_probe_*.csv` ·
`members_decomp.csv` · `adv.csv` · `exposure_decomp.csv` · `peryear.csv` · `perwindow.csv` ·
`dailyw_*.csv` · `basketret_*.csv` · `run_*.log` · `probe_*.log`
