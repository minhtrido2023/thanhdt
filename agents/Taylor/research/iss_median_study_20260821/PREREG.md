# PREREG — ISS/rights offering: test TRUNG VỊ làm primary (HƯỚNG C_RERUN)

- **Job**: `Taylor_20260821_111228` · **Ngày đăng ký**: 2026-08-21
- **Commit file này TRƯỚC khi chạy bất kỳ test outcome nào.** Deviation → `DEVIATIONS.md` cùng
  thư mục, ghi TRƯỚC khi đọc kết quả.
- **KHÔNG override PREREG cũ** (`../iss_event_study_20260821/PREREG.md` giữ nguyên, verdict NO-GO
  trên H1-mean vẫn đứng). **KHÔNG WIRE.** Không tự gọi quant-skeptic.

## 0. KHAI BÁO TRUNG THỰC — đây là LẦN NHÌN THỨ HAI trên CÙNG MỘT MẪU

Study trước (`iss-event-study-20260821`) đăng ký H1 theo **trung bình** và bị bác
(mean +1,22pp, t=+0,85). Trung vị âm bền (−3,51pp, 60,4% âm, Wilcoxon p=2,6e−4) là **lead phát
hiện SAU khi đọc kết quả**, đã ghi vào deviation log + bus. File này hợp thức hoá lead đó bằng
một prereg riêng — **nhưng nó KHÔNG hồi phục tính "chưa nhìn" của dữ liệu.**

Hệ quả bắt buộc, khoá trước:
- Ngưỡng đăng ký chính vẫn là `p ≤ 0,05` (theo dispatch), **nhưng verdict PHẢI báo kèm đọc
  Bonferroni 2 lần nhìn (`p ≤ 0,025`)** và nhãn "second look on same sample".
- **Bằng chứng quyết định thật sự nằm ở H3 và ở tính nhất quán IS/OOS**, không nằm ở p-value —
  vì p-value ở lần nhìn thứ hai không còn diễn giải tần suất sạch.
- Không được thêm bất kỳ scope/biến thể nào ngoài danh sách §4 để "tìm" ý nghĩa.

## 1. Dữ liệu — TÁI DÙNG, không pull lại

- `../iss_event_study_20260821/events.csv` — 632 sự kiện `event_code='ISS'` ∧
  `issue_method_code='Rights'` ∧ `event_status='executed'`, có `exright_date`, có giá tại/liền sau
  ex-right, **`in_universe_pit` tại `t0`**. 369 mã, 2005-02-24 → 2026-04-17, IS 431 / OOS 201.
- `../iss_event_study_20260821/control.csv` — control ghép cặp (cùng `icb_code_lv1`, cùng `t0`,
  `in_universe_pit`, không có Rights nào trong ±90 ngày), phủ 624/632 sự kiện.
- **Hệ quy chiếu `Close`** (giá điều chỉnh) là PRIMARY; `Price` chỉ đối chứng cơ học. Cửa sổ bắt
  đầu TẠI/SAU `exright_date` ⇒ bẫy pha loãng nằm ngoài cửa sổ (đã chứng minh ở study trước).
- **Mới pull cho H3**: bảng ISS/Rights (`ticker`, `exright_date`, `event_status`) — dùng để ghép
  với deal, KHÔNG dùng để đổi mẫu H1/H2.

## 2. Giả thuyết

- **H1 (PRIMARY)**: `median(BHAR_60_close) < −2pp` với **Wilcoxon signed-rank p ≤ 0,05**
  (two-sided). Báo kèm bootstrap 95% CI của trung vị (block bootstrap theo **tháng lịch của
  `exright_date`**, 5.000 lần) — CI là số để đọc độ lớn, p-value là ngưỡng đăng ký.
- **H2**: `median(net_close)` với `net = BHAR_60(event) − BHAR_60(control ghép cặp)` < −2pp,
  cùng test Wilcoxon.
- **H3 (PORTFOLIO IMPACT — quyết định thực tiễn)**: trong **2.056 deal cổ phiếu** BAL/LAG
  (`../pre_exdate_avoidance_20260821/entries.csv`, CSV pin R3 2026-08-03, đã loại `ETF_PARK`,
  1 deal = 1 `holding_id`, `entry_date` = fill ĐẦU TIÊN), đếm số deal mà **cùng ticker** có
  ISS/Rights `executed` với `exright_date ∈ [entry_date − 60 ngày lịch, entry_date]`.
  - `hit_pct < 5%` ⇒ **CONFIRMED_BUT_RARE**
  - `hit_pct ≥ 5%` ⇒ đủ điều kiện tier GO đầy đủ
- **Walk-forward**: IS `exright_date ≤ 2019-12-31`, OOS `≥ 2020-01-01`.
  **H1 và H2 phải CÙNG DẤU ở CẢ HAI giai đoạn** — đây là điều kiện cứng, không thương lượng.

## 3. Luật quyết định (§7)

| Verdict | Điều kiện |
|---|---|
| **CONFIRMED** | H1 đạt ∧ H2 đạt ∧ dấu nhất quán IS+OOS ∧ H3 `hit_pct ≥ 5%` |
| **CONFIRMED_BUT_RARE** | H1 đạt ∧ H2 đạt ∧ dấu nhất quán IS+OOS ∧ H3 `hit_pct < 5%` |
| **NO-GO** | H1 hoặc H2 không đạt, HOẶC IS/OOS ngược dấu |

Ghi chú khoá trước: **H2 là điều kiện CẦN**, không phải secondary. Trung vị âm mà không sống qua
ghép cặp ngành/thời điểm = hiệu ứng thị trường/ngành, không phải hiệu ứng rights offering.

## 4. Danh sách scope ĐÓNG (không thêm)

`FULL` · `IS` · `OOS` · `EX_REGIME` (bỏ DT5G state ∈ {0 CRISIS, 4 EX-BULL}, đọc
`tav2_bq.vnindex_5state_dt5g_live` — **KHÔNG** `vnindex_5state`) · `EX_REGIME_STRICT` (chỉ sự kiện
CÓ nhãn DT5G — bảng phủ từ 2014) · đối chứng cơ học `Price`.

## 5. Artifact

`analyze.py`, `q_iss_ledger.sql`, `iss_ledger.csv`, `results_median.csv`, `results_h3.csv`,
`results_h3_hits.csv`, `RESULTS.md`.
