# PREREG — Sàn thanh khoản LAG: Động vs Tĩnh

**Job:** `Taylor_20260825_094721` · **Ngày ghi:** 2026-08-25 · **Tác giả:** Taylor
**Trạng thái:** ĐĂNG KÝ TRƯỚC — ghi xong TRƯỚC khi chạy bất kỳ chân backtest nào của job này.
**Phạm vi:** research paper-only. **KHÔNG wire**, không sửa file production, không tạo `pending_*` patch.

---

## 0. Câu hỏi

Sàn hiện tại `ADV_MIN_VND = 2e9` (`lag_liquidity_filter.py:29`, user chốt 2026-08-10) là một hằng số
**danh nghĩa cứng**. Câu hỏi mở của dispatch: **nó có bị xói mòn theo thời gian khi thanh khoản chung
của thị trường tăng không**, và nếu có thì biến thể sàn ĐỘNG nào (nếu có) đáng xem xét thay thế?

## 1. Điều đã BỊ KHOÁ — không đụng tới trong job này

| Kết luận khoá | Nguồn | Ràng buộc |
|---|---|---|
| Edge của gate `ADV>0` vs hiện vật mô hình fill | `kb/projects/lag-adv-filter-tracking.md` | **chờ checkpoint 2026-12-15 / rà soát đầy đủ 2027-03-31.** Job này KHÔNG trích `+3,85pp…+4,11pp` như edge, KHÔNG chạy lại phép A/B đó |
| Thang liều PHẲNG 0,5→5 tỷ, PBO = 0,916 | `Taylor_20260804_080547` (quant-skeptic CONFIRMED cao) | Mọi "điểm tối ưu" tìm được trên lịch sử phải mặc định coi là **nhiễu**; job này đo lại thang tĩnh chỉ để làm **chân đối chứng**, không để tìm optimum |
| Băng 0,1–2 tỷ = 1,6% vốn, 93,4% bỏ dở, OOS n=8 CI95 chứa 0 | `Taylor_20260810_073541` (CONFIRMED medium) | Đây là **trần công suất** của toàn bộ câu hỏi: bất kỳ biến thể động nào cũng chỉ dịch chuyển sàn TRONG/QUANH băng này ⇒ kỳ vọng tiên nghiệm là **hiệu ứng nhỏ và không có ý nghĩa thống kê** |
| Cơ sở giá ADV = `price` (không phải `close`) | CONFIRMED 2026-08-02 | Giữ `LAG_ADV_BASIS=price` ở mọi chân, không đảo lại |

## 2. Ba giả thuyết

### H1 — Thang liều tĩnh vẫn PHẲNG trong dải [1B, 4B]
**H1₀:** CAGR OOS(2020+) của các sàn tĩnh {1,0 · 1,5 · 2,0 · 3,0 · 4,0} tỷ không khác nhau
có ý nghĩa; không tồn tại điểm gãy thật.
**H1₁:** tồn tại ít nhất một điểm gãy (bước nhảy ≥ 1,0pp CAGR OOS giữa 2 ngưỡng liền kề)
**và** điểm gãy đó sống sót LOO theo năm.
**Tiên nghiệm:** kỳ vọng KHÔNG bác được H1₀ — 08-04 đã đo biên độ 0,21pp trên dải 0,5→5 tỷ.
Chân này chủ yếu là **control leg** để xác nhận harness tái lập, không phải phép thử khám phá.

### H2 — Sàn danh nghĩa cứng bị xói mòn theo thanh khoản thị trường
**H2₀:** sàn 2B cứng và sàn động (biến thể A deflate-lạm-phát, biến thể B percentile thị trường)
cho **cùng một tập ứng viên** trong sai số nhỏ; số ứng viên pass/fail per year không lệch có hệ thống
theo thời gian.
**H2₁:** sàn 2B cứng lọc **chặt dần** (hoặc **lỏng dần**) một cách đơn điệu theo năm so với sàn động
⇒ tồn tại xói mòn danh nghĩa thật.
**Đo bằng:** tỷ lệ ứng viên bị chặn per year, chênh lệch (động − tĩnh), test xu hướng đơn điệu
(Spearman ρ giữa năm và Δ tỷ-lệ-chặn).
**Tiên nghiệm:** biến thể A **chắc chắn** tạo Δ đơn điệu **theo cấu tạo** (công thức là hàm mũ của
thời gian) ⇒ H2₁ với A là **tautology, KHÔNG phải phát hiện**. Phép thử có nội dung thật chỉ nằm ở
**B** (percentile thị trường), nơi độ dốc do dữ liệu quyết định chứ không do công thức áp đặt.
Ghi rõ điều này TRƯỚC để không tự khen một kết quả rỗng.

### H3 — Sàn "đúng bản chất" theo capacity KHÁC HẲN sàn đang dùng
**H3₀:** sàn suy ra từ ràng buộc fill (size mục tiêu / (5 phiên × X% ADV)) nằm cùng bậc độ lớn với
2B tại NAV hiện hành.
**H3₁:** sàn capacity ≥ 2× sàn đang dùng tại NAV 50B, và giãn tuyến tính theo NAV ⇒ sàn 2B **không
phải** ràng buộc đang binding; ràng buộc thật là capacity và nó sẽ tự siết khi NAV lớn lên.
**Tiên nghiệm (số dispatch đưa, tôi tái tính độc lập ở §Bước 2C):** X=3,86% ⇒ ~13,5B; X=10% ⇒ ~5,2B
⇒ kỳ vọng **bác H3₀**. Đây là phép tính số học, **KHÔNG phải phép thử thống kê** ⇒ **không** vào
rổ BH FDR.

## 3. Metric chính + thứ cấp (khoá trước)

**Chính:** `CAGR OOS (2020-01-01 → 2026-06-19)`.
**Thứ cấp (báo cáo, KHÔNG dùng để chọn):** CAGR Full, CAGR IS(2014-2019), Sharpe(252), MaxDD, Calmar,
Final NAV, số ứng viên LAG bị chặn **per year**, số mã distinct bị chặn.
**Δ luôn quy về baseline = sàn 2B tĩnh** (không phải control ADV=0), vì 2B là hiện trạng production.

**Quy tắc quyết định khoá trước:** khuyến nghị "đáng xem xét thay thế 2B cứng" CHỈ khi cả 3 điều kiện:
1. Δ CAGR OOS vs 2B ≥ **+1,0pp**, VÀ
2. p-value sau hiệu chỉnh BH < 0,05, VÀ
3. dấu của Δ **không đảo** khi bỏ bất kỳ 1 năm nào (LOO).
Thiếu bất kỳ điều nào ⇒ kết luận **NO-GO / giữ nguyên 2B**, bất kể con số điểm đẹp tới đâu.

## 4. Hiệu chỉnh đa phép thử (BH FDR)

**Đếm test TRƯỚC khi chạy** — rổ BH gồm đúng các so sánh CAGR OOS vs baseline 2B:

| # | Chân | Nhóm |
|---|---|---|
| 1–4 | tĩnh 1,0 / 1,5 / 3,0 / 4,0 tỷ | Bước 1 (H1) |
| 5 | biến thể A — deflate lạm phát 7%/năm | Bước 2 (H2) |
| 6–8 | biến thể B — percentile k=20 / 25 / 30 | Bước 2 (H2) |

**m = 8.** BH ở q = 0,05: sắp p tăng dần, ngưỡng thứ i = i × 0,05/8. Ngưỡng cho p nhỏ nhất =
**0,00625**. Biến thể C **không** vào rổ (số học, không có p-value). Nếu phát sinh chân ngoài kế
hoạch, **m tăng theo** và phải ghi rõ trong báo cáo — không được giữ m=8 rồi thêm test.

**p-value đến từ đâu:** bootstrap khối (block bootstrap) trên chuỗi lợi suất ngày OOS, 10.000 lần,
khối 21 phiên (≈1 tháng, giữ tự tương quan). Hai đuôi. **N hiệu dụng = số EVENT LAG độc lập bị ảnh
hưởng** (dự kiến vài chục, xem §5), KHÔNG phải số dòng NAV — khai rõ trong báo cáo theo skill
`quant-research` §"N as independent events".

## 5. Rủi ro chính — ghi trước để không bào chữa sau

| # | Rủi ro | Vì sao nghiêm trọng | Xử lý đã khoá trước |
|---|---|---|---|
| R1 | **N thấp** — vùng bị tác động = băng 0,1–2 tỷ = **1,6% vốn lịch sử**, chỉ **23 deal khớp** trong 12,5 năm, OOS còn **n=8** | Mọi Δ đo được nằm dưới nhiễu của chính engine; một sàn động chỉ dịch biên vài trăm triệu VND sẽ tác động tới **vài** event | Báo cáo **bắt buộc** in n-event bị ảnh hưởng cạnh MỌI Δ CAGR. Δ mà n<30 event ⇒ dán nhãn `UNDERPOWERED`, không được diễn giải theo hướng ủng hộ |
| R2 | **Fill-model uncertainty** — engine giả định fill 20%/ADV/phiên, fill THẬT đo được ở DNSE là **3,86%** | Sàn thanh khoản là mệnh đề VỀ fill; engine đang dùng giả định fill rộng hơn thực tế **~5,2×** ⇒ engine **đánh giá thấp** mức độ mã mỏng không vào nổi hàng | Không dùng backtest để trả lời "sàn nào đúng"; backtest chỉ trả lời "sàn nào đổi kết quả **trong mô hình này**". Biến thể C (capacity) chạy ở CẢ HAI X để phơi độ nhạy |
| R3 | **Tautology của biến thể A** | Công thức A là hàm mũ theo thời gian ⇒ chắc chắn sinh xu hướng đơn điệu; dễ bị đọc nhầm là "phát hiện xói mòn" | Đã khai ở H2. A được báo cáo như **phép chuẩn hoá đơn vị**, không phải bằng chứng thực nghiệm |
| R4 | **Calibrate k của biến thể B nhìn vào đích** — chọn k sao cho sàn 2026-08-10 ≈ 2B là dùng thông tin điểm cuối | Nếu sau đó khen B "tự nhiên trùng 2B hôm nay" thì đó là lập luận vòng | Calibrate là **thao tác quy đơn vị bắt buộc để so apple-to-apple**, và **cấm** trích "B khớp 2B hôm nay" như bằng chứng ủng hộ B |
| R5 | **PBO 0,916 đã đo cho chính họ tham số này** | Không gian sàn ADV đã được chứng minh là overfit-prone | Quy tắc quyết định §3 đặt ngưỡng ≥1,0pp (cao hơn hẳn biên độ nhiễu 0,21pp đo 08-04) và bắt buộc LOO sống sót |
| R6 | Snapshot BQ pin `asof20260729_postrestate` cũ hơn hôm nay | Kết quả không phản ánh dữ liệu mới nhất | **Cố ý** — bắt buộc để chân control tái lập pin R3 từng chữ số. Ghi rõ trong báo cáo |

## 6. Thiết kế thực nghiệm (khoá trước)

- **Engine:** BẢN SAO nghiên cứu `mike/agents/Taylor/exp_lag_advdyn_20260825/pt_v23_advdyn.py`,
  dẫn xuất từ `exp_lag_advgate_20260804/pt_v23_advgate.py` (đã CONFIRMED), thêm **đúng một** knob
  `LAG_ADV_MIN_MODE ∈ {static, inflate, pctile}` + `LAG_ADV_PCTILE_CSV`. **No-op khi mode=static,
  LAG_ADV_MIN_VND=0.** Production `pt_v23_audit_2014.py` **không được chạm** (`git status` sạch).
- **Lệnh pin R3 nguyên văn:** `NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap
  BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 … v23a none postbull 0 edge`,
  `BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`, `BQ_CACHE_THREADS=1`, `$DNA_PYEXE`.
- **`EXP_TAG` cho MỌI chân** ⇒ không ghi đè CSV canonical (§8 coding_guidelines).
- **Điều kiện hợp lệ (gate, đăng ký trước):** chân `mode=static, LAG_ADV_MIN_VND=0` PHẢI tái lập pin
  R3 **28,86 / 1,90 / −17,8 / 1,62 / 1.178,01B** từng chữ số, và `[selfcheck BAL]`/`[selfcheck LAG]`
  = **0 VND** trên MỌI chân. Không đạt ⇒ **dừng, không báo số nào**.
- **Điểm chèn gate:** vòng sinh tín hiệu LAG, tra `liq_lag[(ticker, signal_date)]` = ADV **tại ngày
  tín hiệu** (point-in-time, cơ sở `price`); thiếu khoá ⇒ **loại (fail-closed)**, đúng ngữ nghĩa
  gate live.
- **ADV3T:** `Volume_3M_P50 × COALESCE(Price, Close)` — một công thức duy nhất, nhất quán với
  `lag_liquidity_filter.py:156`, `signal_v11_sql.py:95`, `trading_bot/due_diligence.py::adv_vnd`.
- **Nguồn market-wide:** `tav2_mike.universe_pit` (point-in-time). **KHÔNG** dùng `ticker_prune`.
- **LOO theo năm:** bỏ từng năm 2014…2026, tính lại CAGR Δ; báo cáo năm nào lật dấu.

## 7. Deliverable đã cam kết

1. File này (prereg).
2. `lag_dynamic_threshold_20260825.md` — kết quả + khuyến nghị.
3. Bus finding riêng: Bước 1, biến thể A, biến thể B, biến thể C, Bước 3 (BAL).
4. Khuyến nghị cuối + **điều kiện cần thêm** để ra quyết định.

**Cam kết công bố âm tính:** nếu mọi biến thể đều trượt quy tắc §3 thì báo cáo kết luận
**"giữ nguyên 2B cứng"** và nói rõ vì sao — không đi tìm cách cắt lát dữ liệu khác để cứu một biến thể.
