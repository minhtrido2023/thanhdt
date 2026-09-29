# Nhận biết đỉnh thị trường bằng chỉ báo kỹ thuật ngoài breadth-divergence

> Job `Taylor_20260903_154921` (follow-up thứ 4, tiếp `Taylor_20260903_153554`). **RESEARCH-ONLY,
> không wire.** Đọc trước: `mania_deep_dive_2006_2007_and_cracking_20260903.md` §2 (định nghĩa
> DIVERGE_DAY), §2.5 (base rate — bắt buộc để không đọc sai mọi con số dưới đây), §3 (độ trễ
> DIVERGE→đáy, kết luận "cảnh giác, không timing"). File này SO SÁNH, không thay thế kết luận §3.

**Câu hỏi user**: ngoài breadth-divergence, có chỉ báo kỹ thuật nào khác (khối lượng, trading
value, VAPM tuần/tháng, phân kỳ RSI) nhận biết đỉnh tốt hơn để timing thoát không?

**Trả lời ngắn (xem §5 đầy đủ):** **KHÔNG.** Đã thử 10 biến thể qua 4 họ + 1 tổ hợp
(N_TRIALS=11, khai báo đầy đủ ở §1). Không biến thể nào vượt DIVERGE_DAY (breadth-divergence) trên
3 đại lượng đánh giá chuẩn (§3-style). Phân kỳ RSI (họ 4) là ứng viên bắt-đỉnh-đáng-tin-cậy-nhất
(must-catch cả 3 đỉnh lớn 2007/2018/2022 ở MỌI ngưỡng thử) nhưng biên độ outcome sau tín hiệu gần
như TRÙNG với nền vô điều kiện — bắt được "đỉnh" giỏi hơn breadth nhưng không cho biết ĐỘ SÂU điều
chỉnh sắp tới, nên vẫn không phải công cụ timing. AND-combo (RSI × trading-value) lặp lại đúng bài
học §2.4: kết hợp làm MẤT cả 3 case must-catch.

---

## §1. Thiết kế — N_TRIALS, dữ liệu, PIT

### 1.1 Nguồn dữ liệu — 2 series giá KHÁC NHAU, dùng có chủ đích, không trộn lẫn

- **Giá quy chiếu cho MỌI outcome (đại lượng #1-3 §3-style)**: `crack_daily.csv` — panel
  2008-06-02→2026-09-03 (4.558 phiên), cột `vnindex_close` = `ANY_VALUE(t.VNINDEX)` — **giống hệt
  series đã dùng cho DIVERGE_DAY ở §2/§3 của mania_deep_dive**, đảm bảo so sánh ngang hàng.
- **Chỉ báo kỹ thuật (RSI/Volume/Trading_Value/VAP)**: pull BQ mới `tav2_bq.ticker WHERE
  ticker='VNINDEX'` (VNINDEX được lưu như một pseudo-ticker có đủ OHLCV+kỹ thuật riêng — bẫy tên
  cột trùng tên bảng theo CLAUDE.md §BigQuery bẫy #2, alias `t.` bắt buộc). Cột `Close` của
  pseudo-ticker này **chênh tối đa ~2% (38 điểm/1800)** so với `vnindex_close` mirror — kiểm tra
  bằng merge trực tiếp trên 4.558 ngày trùng. **Quyết định**: không dùng Close của pseudo-ticker
  cho outcome measurement (giữ nguyên `vnindex_close` mirror cho toàn bộ đại lượng #1-3); chỉ lấy
  RSI/Volume/Trading_Value/VAP từ pseudo-ticker để DỰNG tín hiệu — 2 series không bị trộn trong
  cùng một phép tính.
- Artifact: `mania_20260903/toptech/vnindex_tech.csv` (pull BQ, 2000-07-28→2026-09-03, 6.355
  dòng), `analyze_toptech.py` (merge + toàn bộ candidate + outcome).

### 1.2 PIT — xác nhận thực nghiệm, không suy từ tên cột

`D_RSI_Max3M`/`D_RSI_Max3M_Close` được xác nhận **TRAILING** (cửa sổ 63 phiên kết thúc TẠI t, bao
gồm t) bằng cách tính tay trailing-max trên `2022-01-06` và so khớp CHÍNH XÁC với giá trị BQ trả
về (`0.7844969...` cả 2 phía); đối chứng với cửa sổ CENTERED cùng độ rộng cho kết quả KHÁC hẳn
(`0.7065`) — loại trừ khả năng cột này vô tình là centered/forward. `bigquery_dictionary.json`
xác nhận cùng ngữ nghĩa cho họ `D_RSI_Max*`: `"D_RSI_Max3M": "0..1 RSI max over the last 3M"`.
`pct252`/`recent_max_63`/`new_high_126` dùng lại NGUYÊN VĂN hàm từ `analyze_crack.py` (đã audit
causal ở job trước) — không viết lại logic, tránh lệch công thức.

### 1.3 N_TRIALS — khai báo trước khi xem kết quả

| # | Biến thể | Ngưỡng | Lý do chọn (không grid-search hậu-kiểm) |
|---|---|---|---|
| 1 | VOL_DIVERGE (họ 1, `Volume_1M`) | drop≥0,30 | tái dùng nguyên ngưỡng DIVERGE_DAY đã must-catch |
| 2 | TV_DIVERGE (họ 2, `Trading_Value_Total_1W`) | drop≥0,30 | như trên |
| 3 | VAP_EXT_1W (họ 3, `Close/VAP1W−1`) | pct≥0,90 | tái dùng ngưỡng p90 chuẩn của detector chính |
| 4 | VAP_EXT_1M (họ 3, `Close/VAP1M−1`) | pct≥0,90 | như trên |
| 5-9 | RSI_DIVERGE_3M (họ 4) | margin∈{0,02;0,03;0,05;0,08;0,10} | grid 5 điểm, TRÌNH ĐỦ CẢ 5, chọn theo must-catch không theo hiệu năng |
| 10 | RSI_DIVERGE_1W (họ 4, kỳ vọng quá nhiễu) | margin=0,05 | 1 điểm tham khảo, không kỳ vọng thắng |
| combo | RSI_DIVERGE_3M(margin đã chọn) AND TV_DIVERGE | — | 1 tổ hợp DUY NHẤT, có cơ chế rõ ("giá tăng nhưng RSI yếu VÀ tiền vào giảm") |

**N_TRIALS = 10 biến thể độc lập + 1 combo = 11.** Không có biến thể nào bị bỏ khỏi bảng vì kết
quả xấu — §2 dưới trình đủ cả 10.

### 1.4 "VAPM" không tồn tại trong dữ liệu — dùng proxy, nói thẳng

Grep `bigquery_dictionary.json` + `mike/kb/data_registry/` cho `VAPM`: **0 kết quả**. Không có cột
nào tên này trong `tav2_bq.ticker` hay `VNINDEX.csv`. Cột gần nghĩa nhất là **VAP** (Volume-At-Price
— "Close in the largest trading area", tức điểm giá có khối lượng giao dịch tập trung nhiều nhất,
gần khái niệm "point of control" trong market-profile) ở 3 cửa sổ `VAP1W/VAP1M/VAP3M`. §2 dùng
**Close/VAP − 1** (giá hiện tại lệch bao xa khỏi vùng giá tập trung khối lượng) làm proxy cho "giá
đã tách rời khỏi vùng cân bằng cung-cầu" — đây LÀ PROXY, không phải VAPM, ghi rõ trong mọi bảng.

---

## §2. Kết quả theo họ (A)

Tất cả outcome đo trên `vnindex_close` (crack panel), t0 = ngày ĐẦU episode (cluster gap≤10 phiên,
giống DIVERGE), forward window 126 phiên (§3-style) + 1M/3M/6M/maxDD-6M (§2-style).

| Candidate | n ngày flag (%) | n episode | catch 2018-04 | catch 2022-01-06 | catch 2007-03-12* |
|---|---:|---:|---:|---:|---:|
| VOL_DIVERGE (Volume_1M, drop≥0,30) | 74 (1,6%) | 14 | 1 ngày | **False** | n/a |
| TV_DIVERGE (TradingValue1W, drop≥0,30) | 52 (1,1%) | 14 | 0 ngày | **False** | n/a |
| VAP_EXT_1W (Close/VAP1W, pct≥0,90) | 133 (2,9%) | 37 | 3 ngày | **True** | n/a |
| VAP_EXT_1M (Close/VAP1M, pct≥0,90) | 154 (3,4%) | 32 | 0 ngày | **False** | n/a |
| RSI_DIVERGE_3M margin=0,02 | 272 (6,0%) | 45 | 15 ngày | **True** | **True** |
| RSI_DIVERGE_3M margin=0,03 | 251 (5,5%) | 45 | 15 ngày | **True** | **True** |
| RSI_DIVERGE_3M margin=0,05 | 204 (4,5%) | 39 | 15 ngày | **True** | **True** |
| RSI_DIVERGE_3M margin=0,08 | 152 (3,3%) | 34 | 15 ngày | **True** | **True** |
| RSI_DIVERGE_3M margin=0,10 | 117 (2,6%) | 27 | 15 ngày | **True** | **True** |
| RSI_DIVERGE_1W margin=0,05 | 8 (0,2%) | 7 | 0 ngày | **False** | n/a |
| DIVERGE_DAY (§2 tham chiếu) | — | 13 | 13 ngày | **True** | n/a (panel BQ 2008-06+) |

*2007-03-12 là bonus check trên `vnindex_tech.csv` riêng (series giá khác, xem §1.1) — chỉ RSI họ
4 được test (Volume/TV/VAP có warmup pct252 đủ nhưng không chạy bonus này do giới hạn thời gian,
xem §4 giới hạn). RSI margin=0,02 tại 2007-03-12: `D_RSI=0,679` vs `D_RSI_Max3M=0,875`, gap=0,195 —
lớn hơn nhiều so với margin nhỏ nhất trong grid, catch dễ dàng ở CẢ 5 mức.

**Đọc bảng — 2 phát hiện định tính quan trọng trước khi vào outcome:**
1. **VOL_DIVERGE và TV_DIVERGE (money-flow divergence kiểu breadth) đều KHÔNG must-catch 2022-01-06**
   — cơ chế "tiền vào giảm khi giá lên" không khớp với đỉnh mọi thời đại (thực ra Trading_Value
   *tăng* mạnh quanh 2022-01, đúng bối cảnh "margin-forced" đã tìm thấy ở finding 08-31: dòng tiền
   dồn vào đúng lúc đỉnh chứ không rút trước).
2. **RSI_DIVERGE_3M must-catch cả 3 đỉnh lớn (2007/2018/2022) ở MỌI mức margin thử** — mạnh hơn hẳn
   DIVERGE (chỉ 1 ngưỡng breadth-drop 0,30 được xác nhận, chưa thử grid) về độ ổn định must-catch.

### 2.1 Outcome — 3 đại lượng §3-style + maxDD-6M §2-style (median)

| Candidate | n dùng | maxdd_6m | lag_sessions (t0→đáy) | peak_after_signal | dd_from_t0 |
|---|---:|---:|---:|---:|---:|
| **Nền (§2.5/§3, N=197-207)** | 197-207 | **−14,2%** | **35,0** | **1,6%** | **−5,9%** |
| **DIVERGE_DAY (§2/§3, N=12-13)** | 12-13 | **−16,4%** | **49,5** | **2,0%** | **−9,1%** |
| VOL_DIVERGE | 13 | −11,3% | 40,0 | 1,5% | −7,4% |
| TV_DIVERGE | 13 | −10,5% | **8,0** | 0,8% | −1,9% |
| VAP_EXT_1W | 37 | −14,3% | 36,0 | 2,1% | −7,9% |
| VAP_EXT_1M | 32 | −14,7% | 33,0 | 2,6% | −6,9% |
| RSI_DIVERGE_3M m=0,02 | 44 | −14,5% | 35,0 | 0,9% | −7,1% |
| RSI_DIVERGE_3M m=0,03 | 45 | −14,3% | 35,0 | 0,9% | −6,9% |
| RSI_DIVERGE_3M m=0,05 | 39 | −14,3% | 34,0 | 1,6% | −5,4% |
| RSI_DIVERGE_3M m=0,08 | 34 | −14,3% | 31,0 | 1,6% | −6,2% |
| RSI_DIVERGE_3M m=0,10 | 27 | −12,4% | 34,0 | 1,6% | −6,8% |
| RSI_DIVERGE_1W m=0,05 | 7 | −15,4% | 35,0 | 8,5% | −7,5% |

**Đọc theo từng họ:**

- **Họ 1 (Volume) — VOL_DIVERGE**: maxDD-6M **−11,3%**, YẾU HƠN nền (−14,2%) — nghịch hướng kỳ
  vọng. Lag dài hơn nền (40 vs 35) nhưng vẫn ngắn hơn DIVERGE. Không must-catch 2022. **Loại.**
- **Họ 2 (Trading value) — TV_DIVERGE**: maxDD-6M **−10,5%**, yếu nhất trong mọi biến thể. Lag
  RẤT ngắn (median 8 phiên) nhưng `dd_from_t0` chỉ **−1,9%** — đáy tới nhanh nhưng NÔNG, đúng dạng
  "một nhịp giật ngắn" chứ không phải điều chỉnh thật. Không must-catch 2022. **Loại.**
- **Họ 3 (VAP proxy) — VAP_EXT_1W must-catch tốt (2018+2022) nhưng outcome ~ nền y hệt**
  (maxDD −14,3% vs nền −14,2%; lag 36 vs 35). VAP_EXT_1M không must-catch 2022 → loại theo tiêu
  chí §2.4. VAP_EXT_1W có thể giữ làm bổ trợ định tính (catch tốt) nhưng KHÔNG có nội dung
  outcome vượt nền.
- **Họ 4 (RSI divergence) — must-catch xuất sắc, outcome không vượt nền có ý nghĩa.** Không có
  dose-response rõ: maxDD-6M gần như PHẲNG qua 5 mức margin (−14,5/−14,3/−14,3/−14,3/−12,4%,
  KHÔNG đơn điệu theo hướng "margin chặt hơn ⇒ DD sâu hơn" mà lẽ ra một tín hiệu thật phải có) —
  dấu hiệu tín hiệu đang bám sát NHIỄU quanh nền, không phải effect thật có bậc thang theo cường
  độ. `peak_after_signal_pct` (0,9-1,6%) THẤP hơn DIVERGE (2,0%) — điểm CỘNG nhỏ (ít tốn cơ hội
  hơn nếu hành động ngay), nhưng `dd_from_t0` (−5,4% đến −7,1%) đều YẾU HƠN DIVERGE (−9,1%) và ở
  margin 0,02-0,03 còn xấp xỉ NGANG nền.

---

## §3. Tổ hợp (C)

**RSI_DIVERGE_3M (margin=0,02, mức nhỏ nhất — chọn vì ĐÂY LÀ MỨC ĐẦU TIÊN trong grid thoả must-catch
cả 2018 và 2022, không phải mức hiệu năng tốt nhất) AND TV_DIVERGE**:

- **11 episode**, nhưng **KHÔNG must-catch 2018-04 (0 ngày) và KHÔNG must-catch 2022-01-06 (False)**
  — lặp lại chính xác bài học §2.4 (CRACK_DAY = DIVERGE AND CONC làm MẤT case định nghĩa 2022-01-06).
  Cơ chế: TV_DIVERGE đòi trading-value SUY GIẢM, nhưng cả 2 case định nghĩa (2018/2022) đều có
  trading-value TĂNG hoặc ổn định quanh đỉnh (dòng tiền margin-forced dồn vào đúng lúc đỉnh, không
  rút trước — khớp finding 08-31 "margin-forced selloff"), nên AND với TV_DIVERGE loại bỏ đúng 2
  case quan trọng nhất.
- Kết quả outcome của 11 episode còn lại rất TẠP (từ +44,7% đến −26,1% ở cột `6M`, không đồng nhất
  hướng) — không phải một nhóm episode đồng chất, dấu hiệu tổ hợp bắt trúng nhiều dạng khác nhau
  của "giá tăng + RSI yếu + tiền giảm" mà không riêng "đỉnh mania".
- **Kết luận: KHÔNG dùng combo này** — cùng nhóm lỗi với §2.4, không thử thêm tổ hợp khác (tránh
  N_TRIALS phình to sau khi đã thấy 1 combo hỏng must-catch, đúng tinh thần "1-2 tổ hợp có lý do
  rõ" của dispatch, không leo thang thành grid-search tổ hợp).

---

## §4. Giới hạn

1. **N nhỏ cho mọi họ** (13-45 episode/candidate) — không tính DSR/PBO (không đề xuất wire nào).
   Không có kiểm định thống kê hình thức (không có scipy trong môi trường job) — so sánh chỉ bằng
   median/mean, độ chồng lấn phân phối lớn cho hầu hết candidate vs nền.
2. **Bonus 2007-03-12 chỉ chạy cho họ RSI** (do giới hạn thời gian dispatch) — Volume/TV/VAP KHÔNG
   được test trên đỉnh 2007 dù về lý thuyết pct252 đã đủ warmup (~1.494 phiên trước đó, dư so với
   252+63 cần thiết). Nếu cần đầy đủ hoá, chạy lại `analyze_toptech.py`'s helper trên
   `vnindex_tech.csv` độc lập panel, y hệt cách đã làm cho RSI.
3. **2 series giá khác nhau ~2%** (mirror `t.VNINDEX` dùng cho outcome vs `Close` của pseudo-ticker
   dùng cho tín hiệu) — đã tách rõ vai trò (§1.1), không trộn trong 1 phép tính, nhưng nghĩa là
   "new_high_126" (từ mirror) và "RSI đạt đỉnh tại giá X" (từ pseudo-ticker Close) về mặt hình thức
   không đảm bảo tính "giá cao nhất 126 phiên luôn ≥ giá tại đỉnh RSI 63 phiên" một cách logic chặt
   chẽ như nếu dùng chung 1 series — không phát hiện sai lệch thực tế nào từ việc này (RSI_DIVERGE
   vẫn catch đúng cả 3 đỉnh), nhưng ghi nhận đây là điểm cần làm sạch nếu muốn dùng RSI_DIVERGE cho
   việc gì nghiêm túc hơn nghiên cứu mô tả.
4. **VAP dùng đúng 1 ngưỡng (p90) không grid** — không thử ngưỡng khác cho VAP_EXT vì đã đủ để kết
   luận "must-catch được nhưng outcome không vượt nền", câu hỏi vận hành chính đã trả lời được.
5. **W_CMB/M_CMB không tồn tại trong BQ `tav2_bq.ticker`** (chỉ có trong `data/VNINDEX.csv` local,
   file này cũng đã STALE — chỉ tới 2026-05-26, không tới 2026-09-03 như panel BQ) — không dùng làm
   nguồn cho family nào trong report này để tránh trộn vintage dữ liệu; nếu muốn khai thác cột này
   trong tương lai cần xác minh script nào sinh ra `VNINDEX.csv` và tần suất refresh trước (chưa có
   trong `kb/data_registry/`).
6. **RESEARCH-ONLY**, không qua quant-skeptic (không đề xuất production change nào).

---

## §5. Trả lời trực tiếp câu hỏi vận hành (D)

**Không tìm được chỉ báo/tổ hợp nào cho tín hiệu RÚT (timing) tốt hơn DIVERGE_DAY.** Trong 10 biến
thể độc lập qua 4 họ + 1 tổ hợp:

- **Volume/Trading-value divergence (họ 1-2)**: yếu hơn cả nền vô điều kiện trên maxDD-6M, và
  KHÔNG must-catch đỉnh mọi thời đại 2022-01-06 — cơ chế "tiền rút trước khi giá đảo chiều" không
  khớp với cách thị trường VN tạo đỉnh gần đây (dòng tiền margin-forced dồn vào đúng lúc đỉnh).
- **VAP proxy (họ 3)**: VAP_EXT_1W must-catch tốt nhưng outcome trùng khớp gần như tuyệt đối với
  nền — không có nội dung phân biệt.
- **RSI divergence (họ 4) là ứng viên NHẬN DIỆN đỉnh tốt nhất trong số đã thử** — must-catch cả 3
  đỉnh lớn lịch sử (2007-03-12, 2018-04, 2022-01-06) ở **mọi** mức margin trong grid 5 điểm, ổn
  định hơn hẳn DIVERGE (vốn chỉ được xác nhận ở đúng 1 ngưỡng breadth-drop). Nhưng khi đo ĐỘ SÂU
  điều chỉnh sau tín hiệu (3 đại lượng §3-style), RSI divergence **không vượt nền có ý nghĩa** và
  không cho thấy dose-response (bậc thang) qua các mức margin — nghĩa là nó giỏi ở việc GẮN NHÃN
  "đây là một đỉnh" nhưng không cho biết đỉnh này sẽ dẫn tới điều chỉnh SÂU đến đâu, tức KHÔNG có
  nội dung timing/sizing hơn DIVERGE.
- **Tổ hợp RSI × Trading-value LẶP LẠI đúng lỗi đã thấy ở §2.4** (AND làm mất must-catch) — không
  nên kết hợp 2 cơ chế "giá-momentum" và "tiền vào-ra" một cách cứng nhắc cho thị trường VN, vì đỉnh
  gần nhất (2022) không có đặc trưng tiền rút trước.

**Kết luận cho vận hành**: giữ nguyên khung §3 đã chốt — **mọi chỉ báo kỹ thuật "đỉnh" hiện có
(breadth-divergence LẪN RSI-divergence) đóng vai trò CẢNH GIÁC ("cấu trúc đang xấu đi"), không
phải đồng hồ đếm ngược để hẹn giờ giảm tỷ trọng bằng tiền thật.** Nếu muốn nâng độ tin cậy phát
hiện đỉnh (không phải đo độ sâu), RSI_DIVERGE_3M có thể dùng làm tín hiệu BỔ SUNG song song với
DIVERGE_DAY (2 cơ chế độc lập, must-catch chồng lấp ở cả 3 đỉnh lớn) — nhưng đây là đề xuất NGHIÊN
CỨU, chưa qua quant-skeptic, không phải khuyến nghị wire.

---

## Artifact

`mania_20260903/toptech/vnindex_tech.csv` (BQ pull VNINDEX pseudo-ticker) ·
`analyze_toptech.py` (toàn bộ candidate + outcome) ·
`events_vol_diverge_day.csv`, `events_tv_diverge_day.csv`, `events_vap_ext_w_day.csv`,
`events_vap_ext_m_day.csv`, `events_rsi_diverge_3m_{0.02,0.03,0.05,0.08,0.1}.csv`,
`events_rsi_diverge_1w.csv`, `events_combo_rsi_tv.csv` ·
`must_catch_summary.csv`, `candidate_summary.csv` (bảng tổng hợp §2/§2.1) ·
Bus: `top-detection-technical-signals-20260903`.
