# KẾT QUẢ — Pre-ex-date buy avoidance (BAL/LAG) — **WEAK_N** (không đủ mẫu để GO)

- **Job**: `Taylor_20260821_103727` · **PREREG**: `PREREG.md`, commit `ab39975e` (trước khi đọc outcome)
- **Script**: `analyze.py` · **Artifact**: `results_entries_binned.csv`, `results_stats.csv`, `results_cohorts.csv`
- **KHÔNG WIRE.** Chờ Mike review + quant-skeptic.

## 1. Verdict

| | |
|---|---|
| **PREREG §7 verdict** | **WEAK_N** — `N(near_ex)` = **19 (IS)** và **27 (OOS)**, cả hai < 30 ⇒ luật đăng ký trước cấm GO |
| Kết luận nghiệp vụ | **Không có căn cứ cho filter "hoãn entry khi sát ex-date"** — kể cả bỏ qua cổng N, hiệu số trên hệ quy chiếu ĐÚNG ≈ 0 và **đổi dấu giữa IS và OOS** |

## 2. Mẫu

Nguồn entry = CSV pin R3 chính thức 08-03 (`..._exp_repin0803_price_univpit.csv`), `TX/action=buy`,
1 event = 1 `holding_id`, lấy fill đầu tiên.

- 2.582 deal thô → **2.056 deal cổ phiếu đơn lẻ** (loại 526 `play_type=ETF_PARK` = rổ parking custom30V,
  không phải mã đơn lẻ nên không có ex-date). 610 mã, 2014-01-27 → 2026-06-11. LAG 1.900 / BAL 682 (trước lọc).
- Khớp giá BQ: **2.056/2.056 = 100%** (mọi entry cổ phiếu đều có dòng `ticker` tại đúng ngày fill).
- Ex-date: `corporate_action` `DIV`+`executed`, dedup `(ticker, exright_date, dividend_year, dividend_stage_vi)`
  → 13.012 sự kiện; 517/610 mã trong mẫu có ít nhất 1 DIV.

| cohort | định nghĩa | n |
|---|---|---:|
| `near_ex` | ex-date trong 0–10 ngày lịch sau entry | **46** |
| `mid` | 11–29 ngày | 111 |
| `far` | 30–60 ngày | 164 |
| `no_ex` | không có ex-date trong (0,60] | 1.735 |

`near_ex` hiếm vì hai lý do cộng dồn, cả hai là **cấu trúc chứ không phải lỗi**: 215 entry rơi vào mã
không hề trả cổ tức tiền 2013-2026 (book LAG thiên về earnings-drift/tăng trưởng), và cửa sổ 10 ngày
chỉ chiếm 2,7% của một năm. **Đây là trần mẫu cứng của thiết kế này**, không phải thứ chạy thêm data
sẽ gỡ được: kể cả kéo backtest tới 2030 với nhịp deal hiện tại cũng chỉ thêm ~4 near_ex/năm.

## 3. Số

**PRIMARY — BHAR_20 đo trên `Close` (giá ĐÃ điều chỉnh cổ tức):**

| scope | n_near | n_far | mean near | mean far | **Δ (near−far)** | t | p | block-boot 95% CI |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| FULL | 46 | 164 | +1,03pp | +1,71pp | **−0,68pp** | −0,33 | 0,74 | [−4,54 ; +3,69] |
| IS (≤2019) | 19 | 66 | +4,27pp | +2,79pp | **+1,48pp** | +0,45 | 0,65 | [−4,41 ; +7,96] |
| OOS (≥2020) | 27 | 98 | −1,25pp | +0,98pp | **−2,23pp** | −0,87 | 0,39 | [−7,23 ; +3,67] |
| BAL | 14 | 33 | +0,89pp | +4,40pp | −3,52pp | −0,84 | 0,41 | — |
| LAG | 32 | 131 | +1,09pp | +1,03pp | +0,06pp | +0,03 | 0,98 | — |

⇒ **IS và OOS NGƯỢC DẤU**, không nhánh nào đạt `|t| ≥ 2,0`, CI bootstrap chứa 0 ở cả ba scope.
Ngưỡng H1 (−1,5pp, |t|≥2,0) không đạt ở bất kỳ đâu. Điều duy nhất nhất quán là hướng **âm nhẹ** ở
OOS + BAL, nhưng biên độ nằm gọn trong nhiễu (median near_ex −0,90pp vs far +1,16pp; win-rate
45,7% vs 55,5% — gợi ý chứ không phải bằng chứng).

**CHỨNG MINH CƠ HỌC — cùng phép đo trên `Price` (giá THÔ, chưa điều chỉnh):**

| scope | Δ (near−far) | t | p | block-boot 95% CI |
|---|---:|---:|---:|---|
| FULL | **−6,83pp** | −3,20 | 0,0021 | [−11,02 ; −2,33] |
| IS | −4,85pp | −1,39 | 0,18 | [−10,73 ; +2,07] |
| OOS | **−8,26pp** | −3,10 | 0,0037 | [−13,60 ; −2,08] |

Đây chính là cái bẫy §6 của PREREG, **đăng ký trước chứ không phải giải thích hậu nghiệm**: đo BHAR
bằng `Price` qua một ex-date sinh ra chênh lệch âm **thuần kế toán**. Div yield trung bình của cohort
`near_ex` = **4,72%** — cùng bậc độ lớn với phần chênh, phần dư còn lại đến từ các mã có kèm sự kiện
`ISS` (thưởng/chia tách) làm `Price` rơi thêm. Cohort `mid` trên `Price` cũng âm (−2,25 IS / −0,22
OOS) trong khi trên `Close` lại **dương mạnh nhất** (+3,60 / +4,34) — chữ ký kinh điển của hiệu ứng
kế toán, không phải alpha.

**Nếu ai đó chạy nghiên cứu này trên `Price` sẽ ra "t=−3,2, p=0,002, GO" và wire một filter vô nghĩa
vào production.** Tiền cổ tức về tài khoản bù đúng phần giá rơi; nhà đầu tư không mất gì.

## 4. Khuyến nghị

1. **NO-GO cho filter hoãn entry sát ex-date.** Không đủ bằng chứng, và cổng N của PREREG chặn trước
   khi tới bước đó.
2. **Không tái chạy thiết kế này với mẫu lớn hơn** — trần mẫu là cấu trúc (§2). Muốn theo hướng này
   thì phải đổi thiết kế (vd: dùng TOÀN BỘ universe làm event study thay vì chỉ deal đã vào lệnh, khi
   đó N lên hàng nghìn) và **phải PREREG lại**, không được coi là tiếp tục của file này.
3. **Bài học mang đi (ngoài phạm vi job)**: bất kỳ đo lường lợi nhuận nào bắc qua ex-date PHẢI khai
   hệ quy chiếu giá. Đã là luật ở `coding_guidelines §21` cho báo cáo per-position — case này cho thấy
   nó áp cả cho **R&D event study**, nơi chưa có cổng cơ học nào chặn.

## 5. Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
$DNA_PYEXE mike/agents/Taylor/research/pre_exdate_avoidance_20260821/analyze.py
```
Seed bootstrap cố định `20260821`, 5.000 vòng, block = tháng lịch của `entry_date`.
Query BQ nguyên văn: `q_px.sql` (giá) + lệnh DIV/VNINDEX trong git log của commit này.
