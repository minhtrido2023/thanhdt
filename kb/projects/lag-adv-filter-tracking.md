# LAG ADV>0 liquidity filter — theo dõi để phân rã edge thật vs hiện vật mô hình fill

**Trạng thái: ĐANG MỞ — tích luỹ dữ liệu, KHÔNG kết luận gì cho tới mốc rà soát.**
Mở 2026-08-03 (job `Taylor_20260803_035250`, việc 3). Chủ: Taylor.

## Câu hỏi cần trả lời (và vì sao vẫn chưa trả lời được)

`lag_filter_illiquid()` (`lag_liquidity_filter.py`, LIVE từ **2026-07-21**) loại ứng viên LAG
không đo được thanh khoản (ADV ≤ 0 / thiếu / dòng giá quá cũ). A/B backtest gán cho nó
**+3,85pp → +4,11pp CAGR** (con số đổi theo vintage). **quant-skeptic đã chấm INCONCLUSIVE BA
LẦN** — không phải vì đo cẩu thả, mà vì hai giả thuyết để lại **cùng một dấu vết** trên CSV:

1. **EDGE THẬT** — mã bị chặn không chiếm chỗ ⇒ vốn chảy sang event LAG kế tiếp (velocity vốn).
2. **HIỆN VẬT MÔ HÌNH FILL** — book đơn giản *không fill nổi* mã LAG ở quy mô 25B, và engine
   backtest chỉ đang mô phỏng lại chính giới hạn đó.

Đầu mối mạnh nhất (quant-skeptic): nhánh TREAT **vào lệnh nhiều hơn +30,1%** (1.652→2.149)
nhưng **vị thế HOÀN TẤT lại ít hơn −16,3%** (674→564), `ABANDONED_REFUND` 59,2% → **73,8%**.

⚠️ **Chạy lại backtest lần thứ tư sẽ KHÔNG tách được** — cả hai giả thuyết đều là mệnh đề về
*mô hình fill*, mà backtest dùng chính mô hình đó. Thứ có thẩm quyền phân xử là **fill THẬT của
book live**. Vì vậy dự án này là *tích luỹ dữ liệu theo thời gian*, không phải một phép đo.

## Khe hổng đã vá (2026-08-03) — `edge_health_monitor.py` KHÔNG dùng được cho việc này

Đã kiểm tra trực tiếp theo yêu cầu. `edge_health_monitor.py::lag_edge_health()` (ghi
`data/lag_edge_health.csv`, rolling 12M cohort LAG/PEAD e3) **CHƯA** tách được đóng góp của
`lag_filter_illiquid()`, và **không thể** tách bằng cách thêm cột — 3 lý do cơ chế:

| # | Lý do | Bằng chứng |
|---|---|---|
| a | Hàng ghi ra chỉ có `{entry, ret}` — **không có ticker** ⇒ không quy chiếu ngược mã nào | `edge_health_monitor.py:166` `rows.append({"entry":…, "ret":…})` |
| b | Không có cột thanh khoản/ADV nào; cohort e3 là cohort **nghiên cứu** (NP_R≥15, prior_n_good≥4, pa_HL3≥5), **không hề áp** `lag_filter_illiquid()` | cùng hàm, `e3 = ev[…]` |
| c | **Quyết định** — nó đo `p0/p1` close-to-close với **giả định fill lý tưởng**, trùng đúng giả định đang bị nghi ngờ ⇒ về nguyên tắc không dùng nó để bác chính giả định đó được | cùng hàm |

Thêm nữa `lag_edge_health.csv` là **input SỐNG của production** (`golive_recommend_v23.py:287`
chọn `w_LAG`) ⇒ schema của nó là hợp đồng, **cấm** thêm cột vào. Nên đã làm **file riêng**.

### Đo thật: cái gì tái tạo được về sau, cái gì thì không

| Dữ liệu | Có lịch sử? | Kết luận |
|---|---|---|
| Nhánh **BỊ LOẠI** (mã nào, lý do, mỗi phiên) | ❌ **KHÔNG** — `data/golive_v23_status.json` có ghi `lag_liq_excluded` (07-31: 21 mã) nhưng **bị ghi đè mỗi lần chạy** + nằm trong `.gitignore` (`git log` = **0 commit**) | **KHÔNG tái tạo được**: bộ lọc chốt theo dòng ADV *tại thời điểm chạy*, mà `Volume_3M_P50` là trung vị trượt 3 tháng ⇒ replay sau **không** cho lại đúng tập mã. ⇒ phải log NGAY |
| Nhánh **ĐƯỢC GIỮ** | ✅ có sẵn — `deploy_golive_dt5g_v4/out/golive_v23_recommendations_<date>.csv` (38 file có ngày) | không cần log thêm |
| **Kết cục** (return) cả 2 nhánh | ✅ BQ giá lịch sử không đổi | truy hồi sau, **cố ý** không log |
| **Fill thật** của book live | ✅ `data/execution_logs/dnse_raw_*.jsonl` | đã có, **cố ý** không log lại |

⇒ Mở rộng **tối thiểu**: chỉ vá đúng một ô ❌ duy nhất.

## Đã làm (2026-08-03)

- **`lag_liq_ledger.py`** (mới) — sổ **append-only** `data/lag_liq_ledger.csv`, cột
  `signal_date, gate, ticker, reason_kind, metric, reason, first_seen_ts`. Ghi cả 3 cổng loại
  ứng viên LAG ở tầng tín hiệu (`liq` / `rating` / `forensic`) vào **cùng một sổ** — câu hỏi cần
  trả lời là "vốn chảy đi đâu khi một mã bị chặn", cả 3 cổng đều chặn theo đúng cơ chế đó.
  - **Idempotent** theo khoá `(signal_date, gate, ticker)`; `first_seen_ts` dòng cũ không bị ghi
    đè; ghi `tmp` + `os.replace` (§5 coding_guidelines).
  - **Không chạm production**: parse chuỗi `reason` (3 template cố định) thay vì sửa
    `lag_liquidity_filter.py`; template đổi thì rơi về `kind='other'`, **không mất dòng**.
  - Selfcheck `--selfcheck` **15/15 PASS**, chạy lại dưới `TZ=America/New_York` và `env -i`
    (§16/§19 — kiểm cả phụ thuộc môi trường, không chỉ phiên tác giả).
- **Wire** vào `mike/bin/bq_freshness_check.sh` ngay sau `[pipeline-2] golive_recommend_v23`
  (17:30 ICT). **Cố ý không dùng `_run_pipeline`** + có `|| true`: đây là bước theo dõi, tuyệt
  đối không được chặn chuỗi lập plan T+1. Phải nằm ngay sau pipeline-2 vì nó đọc đúng file bị
  ghi đè. ShellCheck gate PASS.
- **`.gitignore`**: thêm ngoại lệ `!WorkingClaude/data/lag_liq_ledger.csv`. Lý do của rule gốc
  là *"regenerable from BigQuery"* — sổ này **không** tái tạo được, và nhỏ (~vài trăm KB sau 2
  quý) ⇒ phải được `backup.sh` đẩy lên GitHub, nếu không thì mất trắng khi hỏng đĩa.
- Bắt được phiên đầu: **2026-07-31, 86 dòng** (liq=21, rating=65; forensic=0 vì gate forensic
  mới wire cùng ngày, chưa chạy phiên nào).

### ⚠️ Đã mất, nói thẳng
Bộ lọc live từ **2026-07-21**, sổ bắt đầu **2026-08-03** ⇒ danh sách bị loại của khoảng **9
phiên (07-21 → 07-30) mất vĩnh viễn**, không có cách nào dựng lại (lý do ở bảng trên). Mẫu chỉ
tính từ 07-31. Đây là chi phí của việc phát hiện muộn, không phải thứ sẽ vá được sau.

## Mốc rà soát — NGÀY CỤ THỂ (tính từ lịch công bố BCTC VN, không phải ước chừng)

Căn cứ: Thông tư 96/2020/TT-BTC — BCTC quý công bố trong **20 ngày** (riêng lẻ) / **30 ngày**
(hợp nhất) kể từ ngày kết thúc quý. Book LAG vào lệnh **T+5** sau release, giữ **25 phiên**.

| Kỳ | Hạn công bố (30d) | Entry T+5 | Hoàn tất 25 phiên |
|---|---|---|---|
| Q3/2026 | 2026-10-30 | 2026-11-06 | **2026-12-11** |
| Q4/2026 | 2027-01-30 | 2027-02-15¹ | **2027-03-22** |

¹ đã trừ nghỉ **Tết Nguyên Đán 2027** (mùng 1 = 2027-02-06, thị trường nghỉ ~2027-02-05→02-12).

- **☑ Checkpoint giữa kỳ — 2026-12-15**: cohort Q3/2026 đã hoàn tất. **Chỉ kiểm tra sổ có đang
  tích luỹ dữ liệu DÙNG ĐƯỢC hay không** (số phiên bắt được vs số phiên EOD thực chạy, có mã nào
  rơi `reason_kind='other'` không, đã có mã bị chặn nào mà sau đó fill được ở book khác chưa).
  **KHÔNG kết luận** về +4,11pp ở mốc này — mẫu 1 quý quá mỏng. Mục đích duy nhất: phát hiện lỗ
  hổng thu thập khi còn sửa kịp, thay vì tới 2027-03 mới biết sổ hỏng.
- **☑ RÀ SOÁT ĐẦY ĐỦ — 2027-03-31**: cả Q3 và Q4/2026 đã hoàn tất 25 phiên (= "thêm 2 quý" theo
  yêu cầu user), cộng đệm cho ingest BQ + doanh nghiệp nộp muộn.

> 📌 **Đính chính mốc trong dispatch**: gợi ý "cuối 01/đầu 02/2027" là **quá sớm** — tại
> 2027-02-01 cohort Q4/2026 thậm chí **chưa vào lệnh** (entry 2027-02-15 do Tết). Dùng bảng trên.

### Tới mốc thì làm gì (viết sẵn để lần sau khỏi phải nghĩ lại)
1. Nối `data/lag_liq_ledger.csv` (nhánh bị loại) với giá BQ → kết cục **giả định** 25 phiên của
   mã bị chặn ⇒ đo cấu phần **né-lỗ-trực-tiếp**.
2. Nối `dnse_raw_*.jsonl` → **tỷ lệ fill THẬT** của các mã LAG đã mua live. Đây là phép thử phân
   xử: nếu live fill **trót lọt hơn hẳn** mức engine dự báo (`ABANDONED_REFUND` 73,8%) ⇒ +4,11pp
   nghiêng về **hiện vật**; nếu live cũng bỏ dở tương đương ⇒ nghiêng về **edge thật**.
3. Chỉ khi (1)+(2) tách được mới đưa quant-skeptic. **Trước đó không trích dẫn +4,11pp như edge.**

## Ràng buộc còn hiệu lực (đừng nới khi chưa tới mốc)
- Engine giữ `LIQ_ZERO_BLOCK=""` (**opt-in**) cho tới khi phân rã xong.
- Số dùng được duy nhất là pin R3 hiện hành, hiểu như **cận dưới**. Khoảng
  `[~27,2%; ~31,3%]` đã **HẾT HIỆU LỰC** từ 2026-08-03 và **không có khoảng mới thay thế**.
- Sổ này **không** feed vào bất kỳ gate production nào, và **không** kết luận gì.

## Liên quan
- `lag_liquidity_filter.py` (docstring = nguồn chuẩn tắc về cơ chế + 2 lần đính chính trước)
- `kb/projects/lag-edge-health-staleness.md`, `kb/projects/lag-0724-ivs-tmg-trc.md`
- `mike/agents/Taylor/research/lag_quality_gate_20260803.md` (báo cáo mở ra việc này)
- `data/results_registry.md` mục **2026-08-03 RE-PIN R3 … LAG_ADV_BASIS=price**

---

## 2026-08-04 — Câu hỏi LÂN CẬN đã đóng: "nâng 2 tỷ/phiên thành GATE CỨNG?" → NO-GO (vì lợi nhuận)

**Job `Taylor_20260804_080547`, quant-skeptic CONFIRMED cao** (`mike/logs/verify_20260804_083418.log`
— skeptic tự chạy lại `dsr_pbo_advgate.py`, tự tính lại sign test + LOO drop-3 + ADV median).
Báo cáo: `mike/agents/Taylor/research/lag_hard_adv_gate_2ty_20260804.md`.

**Vì sao ghi vào ĐÚNG file này dù dispatch nói "câu hỏi KHÁC":** đúng, câu hỏi xuất phát khác
(ngưỡng ĐỘ LỚN 2 tỷ vs gate nhị phân ADV≤0 của dự án này) — **nhưng kết quả cho thấy hai câu hỏi hội
tụ về CÙNG một cơ chế**, nên mọi con số của nó bị chặn bởi đúng 2 mốc cứng của dự án này.

**Cơ chế (đây là phần đáng nhớ, không phải con số):** tập `ADV < 2 tỷ` là **tập cha** của tập
`ADV ≤ 0`. Vì thế một gate độ lớn 2 tỷ **tự động bao trọn** hiệu ứng `LIQ_ZERO_BLOCK` đã đo. Muốn
biết ngưỡng 2 tỷ có nội dung riêng hay không thì **phải đo phần GIA TĂNG trên nền L1**, không được
so thẳng với pin R3 — so thẳng sẽ đọc ra "+3,58pp" và tưởng là edge mới.
- L1 (chặn ADV≤0) = 32,71% · **L1 + gate 2 tỷ = 32,45%** ⇒ phần gia tăng **−0,26pp CAGR, −0,02
  Sharpe, −0,92pp OOS**; chỉ được MaxDD −19,1→−18,2% và Calmar 1,71→1,78.
- Thang liều **phẳng**: 0→0,5 tỷ ăn 98% hiệu ứng, 0,5→5 tỷ biên độ 0,21pp (5 tỷ *thấp hơn* 2 tỷ).
- Δ vs pin **đổi dấu (−1,24pp)** khi bỏ đồng thời 2017+2020+2021; thắng 6/13 năm (p=0,709);
  **PBO = 0,916** (CSCV S=16, 0/16 khối suy biến) ⇒ không ngưỡng nào trong họ được chọn theo IS.

**Hiện vật vận hành đáng giữ (dùng được cho câu hỏi MỨC của dự án này):** ở chân control, nhóm ứng
viên có ADV<2 tỷ hút **28% tổng vốn triển khai LAG** (4.539B/16.099B) để sinh **1,682%/chu kỳ** (vs
4,234% nhóm còn lại) và **bỏ dở 68,1%**. Cắt nhóm đó làm mất **60,8% ứng viên** và 436 vị thế nhưng
**chỉ −47 deal HOÀN TẤT (−4,5%)** — vì 89,2% phần bị cắt vốn đã không fill nổi.

**Lập luận CÒN SỐNG (chưa quyết, không dựa vào CAGR):** nếu user muốn gate này thì chọn nó như
**luật khả-thi-thi-hành** (đừng đặt mục tiêu vào mã không mua nổi — cùng tinh thần
`lag_filter_illiquid`), và ngưỡng phải neo vào **năng lực fill THẬT**: ở NAV 50B, w_LAG≈65%, một vị
thế `LAG_HI` ≈3,25B, fill trong `max_fill_days=5` ở mức live đã xác nhận 3,86%ADV/phiên ⇒ cần
**ADV ≳ ~17 tỷ/phiên**. Tức **2 tỷ vẫn lỏng hơn ~8 lần** so với yêu cầu vận hành — chọn 2 tỷ vì nó
là ngưỡng đã dùng ở rổ CAPIT, KHÔNG phải vì backtest.
