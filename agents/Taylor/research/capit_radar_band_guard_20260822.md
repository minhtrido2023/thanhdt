# B3 — CAPIT × Value Radar band guard (PAPER-ONLY, KHÔNG wire)

**Job** `Taylor_20260822_141143` · **Ngày** 2026-08-22 · **Tác giả** Taylor

**Kết luận một câu: ARCHIVE, không prereg.** Giả thuyết "CAPIT fire khi radar 0-20 thì nên giảm
size" **bị số liệu bác theo đúng chiều ngược lại** — 4 lần CAPIT fire ở radar<20 là 4 lần VNINDEX
chạy mạnh nhất sau đó (250 phiên: median **+30,6%**, cả 4 nằm trong [+20,7; +36,4], **không lần nào
âm**), trong khi nhóm radar≥20 chỉ có median **+11,9%**. Band guard sẽ cắt size đúng 4 thời điểm
tốt nhất.

---

## 1. Bối cảnh & vì sao câu hỏi này hợp lý khi đặt ra

- Phụ lục C (`market_regime_probability_20260729`): **dải radar 0-20 có P(bear) = 20,9%** — tệ hơn
  dải 20-33 (11,7%). Không đơn điệu ở đầu RẺ.
- A2 (job `_131318`): ô CRISIS+RẺ có radar TB = 17,0 ⇒ "rẻ nhưng còn dư địa rơi".
- `capit_base(state, dd52w, vn_cooling)` hiện **mù radar**.
⇒ Câu hỏi: khi radar < 20 lúc CAPIT fire, có nên hạ size xuống 50%?

---

## 2. Dữ liệu

Pin R3 2026-08-03: **18 dòng `EVENT_CAPIT`**, trong đó **16 lần fire thật** (2 lần `size=0` là cổng
từ chối đúng, không tính). Radar score tại ngày fire lấy từ `panel_daily.csv`
(`value_radar.load_series`, CANONICAL, DISPLAY-ONLY). Forward return tính từ **T+1** sau ngày fire.
0/18 sự kiện thiếu radar score. Không dùng cột `profit_*`.

| # | ngày | size | regime | zone | radar | nhóm | COMB60 | COMB250 | EX250 |
|---:|---|---:|---|---|---:|---|---:|---:|---:|
| 0 | 2014-05-08 | 1,000 | CRISIS | TRUNGTINH | 36,6 | ≥20 | +17,9 | +47,9 | +44,9 |
| 1 | 2015-05-18 | 0,750 | NEUTRAL | RẺ | 27,2 | ≥20 | +24,8 | +43,0 | +26,6 |
| 2 | 2015-08-24 | 0,375 | NEUTRAL | RẺ | 21,3 | ≥20 | +14,1 | +30,3 | +5,5 |
| **3** | **2016-01-18** | 0,750 | NEUTRAL | RẺ | **19,5** | **<20** | +15,4 | +22,1 | −6,7 |
| 4 | 2018-05-28 | 1,000 | CRISIS | ĐẮT | 88,3 | ≥20 | +17,2 | +31,4 | +27,2 |
| 5 | 2018-07-05 | 0,375 | NEUTRAL | ĐẮT | 84,0 | ≥20 | +38,1 | +40,0 | +32,5 |
| 6 | 2020-02-03 | 0,750 | NEUTRAL | TRUNGTINH | 52,8 | ≥20 | −2,9 | +33,8 | +8,2 |
| 7 | 2020-03-11 | 0,250 | BEAR | TRUNGTINH | 37,1 | ≥20 | +2,1 | +58,0 | +13,8 |
| 8 | 2020-07-27 | 0,375 | NEUTRAL | RẺ | 27,4 | ≥20 | +28,0 | +98,6 | +36,5 |
| 9 | 2022-04-19 | **0,000** | CRISIS | TRUNGTINH | 54,9 | (gate từ chối) | +0,4 | −7,9 | +17,1 |
| 10 | 2022-06-15 | 0,250 | BEAR | RẺ | 27,1 | ≥20 | +1,6 | −3,9 | +4,1 |
| 11 | 2022-09-28 | **0,000** | BEAR | RẺ | 16,6 | (gate từ chối) | −4,4 | +14,7 | +13,9 |
| **12** | **2023-10-30** | 1,000 | CRISIS | RẺ | **3,2** | **<20** | +16,9 | +33,3 | +12,6 |
| 13 | 2024-04-17 | 0,500 | BULL | RẺ | 22,9 | ≥20 | +14,5 | +31,9 | +30,8 |
| **14** | **2024-08-05** | 0,500 | CRISIS | RẺ | **18,1** | **<20** | +3,9 | +58,9 | +26,4 |
| **15** | **2025-04-03** | 0,500 | BULL | RẺ | **9,1** | **<20** | +20,2 | +40,0 | +3,6 |
| 16 | 2025-10-20 | 0,750 | NEUTRAL | TRUNGTINH | 47,1 | ≥20 | +6,3 | n/a | n/a |
| 17 | 2026-03-09 | 0,750 | NEUTRAL | TRUNGTINH | 34,3 | ≥20 | −3,2 | n/a | n/a |

**Chỉ 4/16 lần fire rơi vào radar<20.** Đây đã là câu trả lời một nửa: band guard là một luật gần
như không bao giờ chạm — 4 lần trong 12,5 năm.

---

## 3. So sánh 2 nhóm

| horizon | nhóm | n | COMB median | COMB mean | dải | EXCESS median | **VNI median** |
|---|---|---:|---:|---:|---|---:|---:|
| 60 | radar<20 | 4 | +16,2% | +14,1% | [+3,9; +20,2] | +5,7pp | +10,3% |
| | radar≥20 | 12 | +14,3% | +13,2% | [−3,2; +38,1] | +6,0pp | +12,0% |
| 120 | radar<20 | 4 | +20,8% | +23,7% | [+7,9; +45,3] | +1,2pp | +21,2% |
| | radar≥20 | 11 | +18,8% | +16,7% | [−7,4; +51,6] | +6,7pp | +7,8% |
| 250 | radar<20 | 4 | +36,7% | +38,6% | [+22,1; +58,9] | +8,1pp | **+30,6%** |
| | radar≥20 | 10 | +36,9% | +41,1% | [−3,9; +98,6] | +26,9pp | **+11,9%** |

**Permutation test** (hoán vị 20.000 lần trên median 2 nhóm — chỉ để biết "có thể do ngẫu nhiên không"):

| horizon | metric | Δ median (<20 − ≥20) | p_perm |
|---|---|---:|---:|
| 60 | COMB | +1,8pp | 0,828 |
| 60 | EXCESS | −0,3pp | 0,947 |
| 120 | COMB | +1,9pp | 0,911 |
| 120 | EXCESS | −5,4pp | 0,560 |
| 250 | COMB | −0,3pp | 1,000 |
| 250 | EXCESS | **−18,8pp** | **0,156** |

**Không một test nào có ý nghĩa.** Chỉ số duy nhất đi đúng hướng phòng thủ là EXCESS@250 (−18,8pp),
và nó **không phải tín hiệu** — nó là hệ quả cơ học của mẫu số:

> `EXCESS = COMB − VNI`. COMB@250 của hai nhóm **bằng nhau** (+36,7% vs +36,9%). Cái khác là VNI:
> **+30,6% (radar<20) vs +11,9% (radar≥20)**. Nhóm radar<20 có excess thấp **vì thị trường chạy
> mạnh**, không phải vì hệ làm dở. Kết quả tuyệt đối của 4 lần đó: +22,1% / +33,3% / +58,9% / +40,0%.

Và VNI@250 sau 4 lần radar<20: **+28,8% / +20,7% / +32,5% / +36,4% — không lần nào âm.** Đó là chữ
ký của ĐÁY, không phải "còn dư địa rơi".

---

## 4. NAV giả định — half-size cho 4 sự kiện radar<20

Tái dựng sổ từ TX ledger (áp dụng hiệu chỉnh cơ sở giá đã học ở B1), nhân 0,5 vào mọi leg
`CAPITB_E{3,12,14,15}` / `CAPITL_E{3,12,14,15}`; tiền tiết kiệm nằm yên 0%.

Self-check tái dựng: **BAL** CAGR 27,57% vs pin 27,57%, NAV cuối khớp **tuyệt đối**
(519.486.726.936 VND). **LAG** CAGR 28,92% vs 28,89%, NAV cuối 592,44B vs 590,76B (lệch 0,28%).

| Sổ | Cửa sổ | full-size CAGR / DD / Calmar | guard CAGR / DD / Calmar | ΔCAGR | ΔDD |
|---|---|---|---|---:|---:|
| BAL | FULL | 27,57% / −22,49% / 1,23 | 27,56% / −22,63% / 1,22 | −0,01pp | **−0,14pp** |
| | IS | 20,81% / −22,49% / 0,93 | 20,70% / −22,63% / 0,91 | −0,11pp | −0,14pp |
| | OOS | 34,13% / −18,88% / 1,81 | 34,21% / −18,91% / 1,81 | +0,08pp | −0,03pp |
| LAG | FULL | 28,92% / −24,62% / 1,17 | 28,63% / −24,73% / 1,16 | −0,29pp | **−0,11pp** |
| | IS | 28,37% / −17,18% / 1,65 | 28,27% / −17,11% / 1,65 | −0,10pp | +0,06pp |
| | OOS | 29,47% / −23,16% / 1,27 | 29,00% / −23,27% / 1,25 | −0,47pp | −0,11pp |

**Guard mất CAGR và KHÔNG cải thiện DD** — ΔDD âm ở 4/6 dòng (DD xấu đi), Calmar không tăng ở dòng
nào. Đây là kết quả sạch: nó không phải "đánh đổi", nó là mất cả hai.

---

## 5. Hoà giải với Phụ lục C — không mâu thuẫn

Phụ lục C nói **P(bear | radar ∈ 0-20) = 20,9%** trên toàn bộ phiên, **không điều kiện**. B3 hỏi
một xác suất **có điều kiện khác hẳn**: `P(kết quả xấu | radar<20 **VÀ** CAPIT đã fire)`. CAPIT chỉ
fire khi đã có drawdown 52 tuần đáng kể + các cổng khác. Giao của hai điều kiện = "**rẻ VÀ đã rơi
đủ sâu để cổng bật**" — đó là mô tả của đáy, không phải của bẫy giá trị. Hai kết quả cùng đúng, chỉ
là hai điều kiện khác nhau. **Đừng trích Phụ lục C để biện minh cho một luật áp lên sự kiện CAPIT.**

---

## 6. Caveat

1. **n = 4 ở nhóm radar<20.** Mọi con số trong báo cáo này là **báo cáo điểm**, không phải kiểm định
   có sức mạnh. Kết luận "ARCHIVE" vững vì nó là *thiếu bằng chứng theo hướng đề xuất* **cộng với**
   bằng chứng đảo chiều nhất quán 4/4 — không phải vì p-value.
2. **Tiền tiết kiệm nằm yên 0%** (giống B1). Với guard chỉ chạm 4 sự kiện, ảnh hưởng nhỏ.
3. **Không dựng NAV combined** — combined của pin đi qua allocator có rebalance band, không tái dựng
   được từ ledger. Báo cáo theo TỪNG SỔ, đó là nơi hiệu ứng thật sự nằm.
4. Tái dựng LAG lệch 0,28% NAV cuối kỳ (BAL lệch 0). Không đủ để đổi dấu bất kỳ kết luận nào.

---

## 7. Kết luận

**ARCHIVE. Không prereg, không wire.** `capit_base()` giữ nguyên — mù radar là ĐÚNG ở đây.

Ba thứ đáng mang đi:
- Radar thấp **tại thời điểm CAPIT fire** là dấu hiệu **tốt**, không phải dấu hiệu xấu (VNI@250
  median +30,6%, 4/4 dương).
- Không được chuyển một xác suất **không điều kiện** (Phụ lục C) thành một luật áp lên **tập con có
  điều kiện** (sự kiện CAPIT) mà không kiểm định lại trên chính tập con đó. Đây là cái bẫy chung, B3
  chỉ là một ca cụ thể.
- Một luật chỉ chạm 4 lần trong 12,5 năm về bản chất **không kiểm định được**. Kể cả nếu số liệu
  ủng hộ, nó cũng sẽ không bao giờ qua nổi cổng quant-skeptic.

**Artifacts**: `strategy_regime_matrix_20260822/b3_events.csv`, `b3_groups.csv`, `b3_nav.csv` ·
script `strategy_regime_matrix_20260822_b3.py`.
