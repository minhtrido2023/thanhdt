# VÒNG 2 BAL — TIỀN ĐĂNG KÝ: cơ chế EXIT/TÁI NHẬP adaptive theo market state
job `Taylor_20260909_112201` · viết **TRƯỚC** khi chạy bất kỳ chân treatment nào · PAPER-ONLY

Mandate user (2026-09-09): *"Khi market state đổi trạng thái thì phải nhanh chóng adapt theo,
không giữ cứng quy tắc gây thiệt hại nặng hơn. Nên có một candidate market state, khi nào hiện
thực chính thức cần adapt chiến lược ngay để không bị động."*

---

## 0. Hai sự thật cơ học phải chốt TRƯỚC, vì chúng loại bớt giả thuyết

Đọc code thật, không suy đoán:

**(0a) "Cho phép BAL mở lệnh lại khi state quay về {4,5}" ĐÃ LÀ HÀNH VI MẶC ĐỊNH.**
Gate regime của BAL nằm ngay trong mệnh đề CASE gán `play_type` (`signal_v11_sql.py:127-137`:
`state5 IN (4,5)`) và trong D1-override (`pt_v23_audit_2014.py:793`: `state5 IN (3,4,5)`), đánh
giá lại **mỗi phiên**. Khi state quay về 4, tín hiệu lại sinh ra và tier lại mua được — không có
khoá một chiều nào. ⇒ **Không tiêu 1 trial cho "re-entry khi state về {4,5}"; nó là no-op.**
Điều BAL thực sự thiếu năm 2026 không phải đường tái nhập khi state về BULL, mà là state **không
hề về BULL** (Phần 1 §5: 100/112 phiên ở state 3).

**(0b) Vốn thoát ra KHÔNG nằm im.** `PARK_STATES="3:0.7"` ⇒ tiền BAL giải phóng trong NEUTRAL tự
động chảy 70% vào rổ custom30V. Nên một luật thoát sớm **tự động** tạo ra một dạng "tái nhập"
gián tiếp: ra khỏi cổ phiếu momentum, vào rổ parking. Đây là kênh duy nhất tham gia được nhịp
tháng 4/2026 mà **không** phải nới gate regime (nới gate = đổi thiết kế, ngoài phạm vi vòng này).
Xác nhận thực nghiệm: Phase 2 CCS bước 0 đo redeploy-ratio **0,913** — vốn cắt ra được hấp thụ lại.

## 1. Bản đồ tier → cổng vào (dùng để định nghĩa luật thoát, KHÔNG có tham số tự do)

| tier BAL (kể cả biến thể `_W` của regime_size) | states được phép MỞ lệnh |
|---|---|
| `MEGA`, `MEGA_W` | {4,5} |
| `MOMENTUM`, `MOMENTUM_W` | {4,5} |
| `DEEP_VALUE_RECOVERY`, `DEEP_VALUE_RECOVERY_W` | {4,5} |
| `RE_BACKLOG_BUY`, `RE_BACKLOG_BUY_W` | {3,4,5} |
| `CAPIT_*` (arm capitulation) | **KHÔNG đụng tới** — mọi luật dưới đây scope theo tier |

Luật thoát của vòng này được phát biểu **duy nhất một cách**: *"thoát khi state hiện tại không còn
nằm trong cổng vào của CHÍNH tier đó"*. Không có ngưỡng nào được chọn — nó suy ra từ bảng trên.

## 2. Bốn chân treatment (N_trials = 4). Không thêm chân nào sau khi thấy số.

Mọi hằng số đều **tái dùng quy ước có sẵn**, không grid-search (kỷ luật bắt buộc: N thật = 10
cửa sổ regime, tune trên chính 10 sự kiện đó là vô nghĩa).

| chân | luật | hằng số lấy từ đâu |
|---|---|---|
| **A — STATE_EXIT** | Ngày nào state ∉ cổng-vào-của-tier → đóng toàn bộ vị thế tier đó (T+1 Open) + huỷ lệnh chờ của tier đó. | Bảng §1. **0 tham số mới.** |
| **B — TRAIL** | Bỏ đồng hồ 45 phiên cho tier BAL (`hold_days_by_tier=9999`); thoát bằng **trailing −20% từ đỉnh**, giữ nguyên stop −20% từ giá vào. | Đúng biên độ stop **−20%** đang chạy production. **0 tham số mới.** |
| **C — CANDIDATE** | Như A, nhưng hành động theo **candidate clock của DT 4-gate**: thoát khi candidate rời {4,5} và đã tích luỹ **k ≥ 10** phiên, thay vì đợi commit. | **10** = đúng hằng số exit-gate của `DT_10_25_25`. **0 tham số mới.** |
| **D — A+B** | A và B cùng lúc. | — |

**Vì sao C ≠ A (không phải trùng lặp).** Từ committed=4: candidate 3 hoặc 2 cần `need=10` ⇒ C
trùng A. Candidate **1 (CRISIS)** cần `need=25` ⇒ **C thoát sớm hơn A 15 phiên**. C cũng thoát ở
những đợt candidate **revert** (chạm k≥10 rồi quay lại) mà A không bao giờ thoát. Đây chính là
"candidate để chuẩn bị / không bị động" theo mandate, phát biểu ở dạng đo được.

**Vì sao D = A+B chứ không phải A+C như gợi ý dispatch.** A+C là suy biến (C bao A ở gần hết
transition, xem trên) ⇒ tổ hợp không sinh thông tin mới. A+B mới là hai trục độc lập (thoát theo
REGIME vs thoát theo GIÁ).

**Hệ quả đã biết và CHẤP NHẬN trước, khai ở đây để không bào chữa sau:**
- A/C/D huỷ cả lệnh **đang chờ khớp** của tier vào ngày thoát. Tín hiệu sinh ở phiên BULL cuối,
  khớp T+1 Open đúng phiên NEUTRAL đầu tiên → bị huỷ. Đó là ý nghĩa của "adapt ngay", không phải bug.
- B tháo đồng hồ thời gian ⇒ vị thế có thể nằm rất lâu, chiếm slot (max 12) và có thể **chặn**
  lệnh mới trong cửa sổ BULL sau. Đây là chi phí thật của B, đo bằng chính NAV.
- Mọi chân đều **không** đụng: gate regime của tín hiệu, DT5G, allocator, CAPIT, custom30V,
  `filter.json`, `macro_state_live.py`.

## 3. Nguồn dữ liệu — cùng vintage với pin, không thêm nguồn ngoài

- State giao dịch: `tav2_bq.vnindex_5state_dt5g_live` (đúng `STATE_TABLE` production).
- Candidate clock (chân C): replay DT 4-gate trên **base v3.4b** =
  `tav2_bq.vnindex_5state_tam_quan_v34b_clean`, **có sẵn trong snapshot pin**
  `data/bq_cache_asof20260729_postrestate/vnindex_5state_tam_quan_v34b_clean.parquet` ⇒ **không có
  lệch vintage** (khác hẳn nợ kỹ thuật `bal_open_pcf.csv` của vòng 1). Logic gate tái dùng
  `mike/agents/Taylor/dt_gate_hazard_research.py::extract_episodes` — bản replication đã self-check
  0-diff vs `dt5g_live`, cũng là bản `dna_report.get_dt_gate_clock()` đang dùng LIVE.
- **Tính nhân quả của clock**: `extract_episodes` đi TIẾN theo thời gian, mỗi ngày chỉ dùng
  `raw[0..t]`. Ta phát ra chuỗi `(date, committed, cand, k, need)` theo đúng vòng lặp đó ⇒ PIT,
  không nhìn trước. **Sẽ tự kiểm chứng bằng test cắt đuôi**: cắt chuỗi tại T, clock tại mọi t ≤ T
  phải trùng khớp với chuỗi đầy đủ (in ra log, coi là điều kiện chặn của chân C).
- **Caveat khai trước**: candidate clock chạy trên BASE, còn state giao dịch là DT5G (base + macro
  cap). Khi macro cap ràng buộc, `committed_base` ≠ DT5G. Sẽ **đo và báo** tỉ lệ 2 chuỗi lệch nhau
  trong report, không giấu.
- **Cấm tuyệt đối làm feature**: `profit_*`, `*_center_*`, `PC1W/PC2W/PC3W/PC1M/PC2M`, `Open_1D`,
  `O1W..O2Y`, `Pattern_*`. Không chân nào ở trên đọc bất kỳ cột nào trong danh sách này.

## 4. Chân control

Chạy TRƯỚC mọi treatment, phải tái lập pin R3 **BYTE-IDENTICAL**:
CAGR **28,8627%** · Final NAV **1.178,0099B** · MaxDD −17,785% · Calmar 1,6229 ·
CSV md5 **`7d053e6201c9d107685ff4d1dd9d2d2a`**.
Lệnh = lệnh pin R3 nguyên văn (`NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap
BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19`, `universe_pit`,
`LAG_ADV_BASIS=price`, `BQ_CACHE_THREADS=1`, `$DNA_PYEXE`).
Bản copy nghiên cứu của `simulate_holistic_nav.py` chỉ thêm **1 tham số** (`trailing_tiers`, mặc
định `None` = y hệt); control chạy trên chính bản copy đó ⇒ nếu md5 không trùng thì **dừng, sửa
harness, không chạy treatment**.

## 5. Tiêu chí GO — phải đạt TẤT CẢ. Thiếu 1 = NO-GO. (7 tiêu chí, khớp vòng 1)

| # | Tiêu chí | Ngưỡng |
|---|---|---|
| C1 | ΔCAGR full-period | **> +0,385pp** (sàn nhiễu của chính harness này, tái dùng từ CCS Phase 2 — KHÔNG chọn lại) |
| C2 | Calmar không xấu đi | Calmar_treat **≥ 1,6229** |
| C3 | Walk-forward | ΔCAGR **IS(2014-19) và OOS(2020+) CÙNG DẤU DƯƠNG** |
| C4a | Leave-one-YEAR-out | không năm nào chiếm **> 50%** tổng delta |
| C4b | **Leave-one-WINDOW-out** (10 cửa sổ BULL/EX-BULL của Phần 1) | không cửa sổ nào chiếm **> 50%** tổng delta. *Đây là tiêu chí quan trọng nhất của vòng này: 2026 và 2021 không được nuốt trọn delta.* |
| C5a | DSR, N_trials = 4, **null = Sharpe của control** | **> 0,95** |
| C5b | PBO (CSCV, S=16) | **< 0,5** |
| C6 | Block bootstrap CI95 của ΔCAGR | **loại trừ 0** (thay cho tiêu chí dose-response của vòng 1 — vòng này không có tham số liều) |
| C7 | Self-check | **0 VND** cả sổ BAL lẫn LAG, **mọi chân** (+ control md5 trùng pin) |

C4a và C4b đều phải đạt (đánh số 4a/4b để giữ đúng 7 tiêu chí như vòng 1).

## 6. Điều đã biết trước là sẽ làm kết quả yếu — nói trước, không bào chữa sau

- **N thật = 10 cửa sổ regime trong 12,5 năm** (Phần 1 §4). Power rất thấp. Một chân PASS đầy đủ
  7 tiêu chí ở N=10 vẫn **chỉ là candidate wire**, còn phải qua `quant-skeptic` + user duyệt.
- Delta của mọi luật thoát sẽ **rẽ nhánh quỹ đạo danh mục** (thoát sớm ⇒ tiền khác ⇒ lệnh sau
  khác). Vòng 1 đã thấy chữ ký này: cùng một hướng nghiêng, λ=0,5 làm 2021 −13,2pp còn λ=1,0 làm
  2021 +12,9pp. C4b tồn tại chính để bắt dạng nhiễu đó.
- Chân A/C **theo cấu trúc** sẽ giảm exposure trong crash (tốt cho MaxDD) và cũng bỏ lỡ các nhịp
  hồi nhanh trong-state (xấu cho CAGR). Nếu kết quả là "MaxDD tốt hơn, CAGR tệ hơn", đó là **NO-GO
  theo C1** — không được đổi sang lý luận "nhưng risk-adjusted tốt hơn" sau khi thấy số. C2 đã là
  chỗ duy nhất rủi ro được tính điểm.

## 7. Vật chứng sẽ nộp

`PREREG.md` (file này) · `dt_candidate_clock.py` + `dt_candidate_clock_exp.csv` (+ log test cắt
đuôi) · `shn_adaptive.py` (copy `simulate_holistic_nav.py` + 1 tham số) · `adaptive_engine.py`
(copy `pt_v23_audit_2014.py` + luật thoát) · `run_leg.sh` · `run_{ctrl,A,B,C,D}.log` ·
`analyze.py` · `ab_metrics.csv` · `peryear.csv` · `perwindow.csv` · `report.md`.
Mọi output NAV mang `AUDIT_EXP_TAG` ⇒ không đè đường dẫn canonical (coding_guidelines §8).
