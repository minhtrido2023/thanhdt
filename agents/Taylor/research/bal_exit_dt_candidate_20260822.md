# B1 — BAL exit theo DT candidate streak (PAPER-ONLY, KHÔNG wire)

**Job** `Taylor_20260822_141143` · **Ngày** 2026-08-22 · **Tác giả** Taylor
**Kết luận một câu: NO-GO cả hai variant.** Variant A (exit khi DT5G committed downgrade) chỉ cải
thiện DD **trong IS**, OOS đứng yên/xấu hơn; variant B (candidate streak xấp xỉ) **anti-predictive
có ý nghĩa thống kê** — nó bán đúng lúc thị trường sắp bật lên.

---

## 1. Nguồn dữ liệu & self-check

| Nguồn | Trạng thái | Dùng làm gì |
|---|---|---|
| pin R3 2026-08-03 (`v23_golive_audit_..._repin0803_price_univpit.csv`) | CANONICAL, self-check 0 VND ở bản gốc | TX ledger BAL (2.619 leg) + `nav_bal_ref` + `state` (DT5G committed) |
| `tav2_bq.ticker.Close` (adj) | CANONICAL | MTM 236 mã BAL |
| `CUSTOM_BASKET` rows trong chính file pin | CANONICAL | chuỗi chỉ số rổ parking custom30V |
| `tav2_bq.vnindex_5state` (v3.4b BASE) | **dùng làm XẤP XỈ** candidate streak — xem caveat §5 | variant B |

Không dùng cột `profit_*`. Thực thi mọi exit sớm ở **T+1** sau phiên trigger (không nhìn trước).

**Self-check tái dựng NAV** — tái dựng sổ BAL từ TX ledger + giá, so với `nav_bal_ref` của pin:

| Metric | pin `nav_bal_ref` | tái dựng | lệch |
|---|---:|---:|---:|
| CAGR FULL | 27,57% | 27,57% | 0,00pp |
| Sharpe FULL | 1,56 | 1,55 | −0,01 |
| MaxDD FULL | −22,22% | −22,49% | −0,27pp |
| Calmar FULL | 1,24 | 1,23 | −0,01 |
| NAV cuối kỳ | 519.486.726.936 | 519.486.726.936 | **0 VND** |

⚠️ **Một hiệu chỉnh BẮT BUỘC đã phải thêm, ghi lại vì nó sẽ cắn người sau:** `Close` của BQ là giá
điều chỉnh ngược về cơ sở HÔM NAY, còn engine chạy point-in-time ⇒ `adj_price` trong TX lệch khỏi
`Close` theo mã và theo kỳ (LHG 2016: tỷ lệ engine/BQ = **1,148**; ITD = 1,194). MTM thẳng bằng
`Close` cho sai số giữa đường **10,09% NAV** và DD lệch 2,3pp. Cách chữa: lấy chính `adj_price` của
TX làm MỐC, nội suy hệ số `f = adj_price/Close` theo thời gian rồi MTM bằng `Close × f` → sai số DD
còn 0,27pp. Hệ số: median 1,0010, p1 0,916, p99 1,212.

Phí dùng cho variant = **median thực nghiệm của chính sổ BAL** (buy 0,150% / sell 0,250%), không ưu ái variant.

---

## 2. Thiết kế

Đối tượng: **505 vị thế BAL non-park** (DEEP_VALUE_RECOVERY 761 leg, RE_BACKLOG_BUY, MOMENTUM,
CAPITB_*; exit gốc: TIME 280 / ABANDONED_REFUND 191 / STOP 33). **Không đụng ETF_PARK** — parking đã
có luật thoát theo regime riêng (`ETF_REBAL_state*`).

- **Variant A** — exit sớm khi DT5G **committed** hạ bậc (`state[t] < state[t−1]`) trong hold window.
  24 phiên downgrade trên 3.107 phiên → chạm **156 vị thế / 19 episode**.
- **Variant B** — exit sớm khi **candidate streak xuống ≥ 10 phiên**. Xấp xỉ = số phiên liên tiếp
  BASE state < committed state. 245 phiên thoả → chạm **147 vị thế / 33 episode**.
- Tiền thu về sau exit sớm **nằm yên 0%/năm** (không tái đầu tư — ta không có bộ sinh tín hiệu để
  biết engine sẽ mua gì thay thế). Đây là giả định thiên vị theo chu kỳ, nên **kết luận chính neo
  vào test sự kiện §4**, không neo vào NAV.

---

## 3. Kết quả NAV

| Cửa sổ | Variant | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---:|---:|---:|---:|
| **FULL** | BAL gốc | 27,57% | 1,55 | −22,49% | 1,23 |
| | variant A | **27,14%** | 1,61 | **−18,93%** | **1,43** |
| | variant B | 24,86% | 1,36 | −25,10% | 0,99 |
| **IS 2014-2019** | BAL gốc | 20,81% | 1,38 | −22,49% | 0,93 |
| | variant A | 20,84% | 1,44 | **−18,39%** | **1,13** |
| | variant B | 20,33% | 1,42 | **−15,88%** | **1,28** |
| **OOS 2020-2026** | BAL gốc | 34,13% | 1,69 | −18,88% | **1,81** |
| | variant A | 33,31% | 1,76 | −18,93% | 1,76 |
| | variant B | 29,17% | 1,36 | −25,10% | 1,16 |

**Đọc bảng này theo đúng thứ tự IS → OOS thì câu chuyện sập:**
- Variant A cải thiện DD **+4,10pp trong IS** nhưng **OOS đứng yên (−18,88% → −18,93%)** và Calmar OOS
  **giảm** 1,81 → 1,76. Toàn bộ "cải thiện DD" ở cột FULL là do IS (episode 2018) kéo.
- Variant B cải thiện DD IS mạnh nhất (+6,6pp) và **xấu nhất OOS** (−18,88% → −25,10%), CAGR −4,96pp.
  Đây là chữ ký sách giáo khoa của IS-artifact.

**Per-year (delta CAGR so với gốc)** — biên độ khổng lồ, không phải edge:

| Năm | base | Δ A | Δ B | | Năm | base | Δ A | Δ B |
|---|---:|---:|---:|---|---|---:|---:|---:|
| 2014 | 9,55% | +0,00 | +0,00 | | 2021 | 117,20% | **−46,30** | +0,60 |
| 2015 | 14,13% | +0,76 | +0,00 | | 2022 | −13,76% | **+8,71** | −0,45 |
| 2016 | 25,41% | +1,05 | −4,55 | | 2023 | 12,12% | +1,90 | +1,29 |
| 2017 | 38,13% | −0,61 | +1,42 | | 2024 | 26,59% | −1,88 | **−19,88** |
| 2018 | 22,75% | −0,66 | +0,93 | | 2025 | 56,69% | +2,88 | −0,16 |
| 2019 | 14,36% | −0,59 | −0,74 | | 2026 | −5,19% | **+19,14** | +3,07 |
| 2020 | 61,50% | +1,76 | −13,89 | | | | | |

CAGR FULL gần như không đổi (−0,43pp) **chỉ vì 2021 (−46pp) và 2026 (+19pp) triệt tiêu nhau**.
Đó là phương sai, không phải alpha.

---

## 4. Test sự kiện — phần quyết định

Câu hỏi thật: **trigger có dự báo được lợi suất âm phía trước không?** Đo `r_avoided` = lợi suất
của chính vị thế đó **từ ngày exit sớm (T+1) tới ngày exit gốc**. Có edge ⇒ phải ÂM có ý nghĩa.
Cụm theo ngày trigger (episode) rồi block-bootstrap 10.000 vòng trên episode.

| Variant | n vị thế | **n episode** | mean `r_avoided` (episode-lvl) | CI 95% | p | median | % vị thế âm | days saved (median) |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| A | 156 | **19** | **+2,28%** | [−1,06; +6,06] | 0,195 | +0,35% | 44,9% | 22 |
| B | 147 | **33** | **+10,23%** | [+4,72; +16,26] | **<0,001** | +3,93% | 34,7% | 23 |

- **Variant A: không có tín hiệu.** Dấu NGƯỢC kỳ vọng (bán đi thì mất +2,28%), p=0,195. LOO theo năm:
  bỏ 2021 ra thì mean rơi từ +2,28% xuống **+0,2%** ⇒ con số vốn đã yếu lại còn do một năm chi phối.
- **Variant B: anti-predictive, CÓ ý nghĩa.** Bán theo streak làm mất **+10,23%** lợi suất phía trước,
  p<0,001, dấu ổn định qua toàn bộ 10 lần LOO (+8,8% … +10,8%). Nhìn ngày trigger là hiểu ngay: chúng
  dồn cục vào **04/2024 (5 phiên) và 04/2025 (8 phiên)** — tức đúng vùng đáy sau nhịp rơi. Xấp xỉ
  "BASE < COMMITTED" theo định nghĩa chỉ bật SAU khi giá đã rơi, nên nó là tín hiệu **mua**, không
  phải tín hiệu bán.

---

## 5. Caveat phải mang theo

1. **Variant B KHÔNG phải candidate streak thật.** `get_dt_gate_clock()` đếm phiên tích luỹ theo luật
   DT_10_25_25 của chính engine; ở đây tôi xấp xỉ bằng "số phiên liên tiếp BASE < COMMITTED". Kết quả
   anti-predictive mạnh tới mức khó lật, nhưng nếu ai muốn theo hướng này thì phải lấy clock thật rồi
   prereg lại — đừng trích số của tôi làm bằng chứng về clock thật.
2. **Tiền nằm yên 0%.** Giả định này ăn điểm cho variant trong gấu và trừ điểm trong bò. Nó giải thích
   2021 (−46pp) và 2022 (+8,7pp). Test sự kiện §4 miễn nhiễm với giả định này — đó là lý do kết luận
   neo vào §4.
3. **N hiệu dụng nhỏ**: A có **19 episode**, B có 33 nhưng dồn cục theo tháng. Với A, không một kiểm
   định nào ở N=19 có sức phân giải để tuyên bố cải thiện DD 3,5pp là thật.
4. Tái dựng NAV lệch DD 0,27pp so với pin (đã hiệu chỉnh cơ sở giá). Mọi so sánh trong báo cáo là
   **variant vs tái dựng**, cùng một chuỗi giá — nội bộ nhất quán.

---

## 6. Kết luận & khuyến nghị

**NO-GO, archive.** Không đề xuất wire, không đề xuất prereg tiếp cho variant B.

- Giả thuyết gốc ("BAL exit mù regime là nguồn của −24,8% excess ở CRISIS×ĐẮT") **không được số liệu
  ủng hộ theo hướng này**: gắn regime vào exit không tạo ra DD tốt hơn ngoài mẫu.
- Nếu ai muốn theo tiếp hướng "exit thông minh hơn", hướng còn sống KHÔNG phải là regime-gate mà là:
  (a) lấy `get_dt_gate_clock()` thật thay xấp xỉ, và (b) mô hình hoá **tái đầu tư** (tiền thoát sớm đi
  vào parking custom30V thay vì nằm yên) — hai thay đổi này đổi bài toán đủ nhiều để phải prereg mới.
- Một quan sát dùng được ngay dù NO-GO: **streak "BASE thấp hơn COMMITTED" là tín hiệu ĐÁY**
  (+10,2% forward, p<0,001, 33 episode). Nó nằm đúng hướng với cơ chế CAPIT hiện có. Chưa đủ để
  wire (chưa prereg, chưa quant-skeptic, và nó chồng lấn CAPIT trigger sẵn có), nhưng đáng ghi lại.

**Artifacts**: `strategy_regime_matrix_20260822/b1_metrics.csv`, `b1_peryear.csv`,
`b1_events_A.csv`, `b1_events_B.csv`, `b1_summary.json` · script
`strategy_regime_matrix_20260822_b1.py`.
