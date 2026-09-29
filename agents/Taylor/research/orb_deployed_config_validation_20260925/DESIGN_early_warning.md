# Thiết kế cơ chế CẢNH BÁO SỚM lệch kỳ vọng — ORB intraday (paper)

Job `Taylor_20260925_103217` · 2026-09-25 · **PAPER-ONLY, không chạm tiền thật**

> **Phạm vi cứng.** Cơ chế này **CHỈ GIÁM SÁT**. Nó không đổi tham số chiến lược, không
> dừng paper program, không ghi vào `data/orb_pt_log.csv` hay bất kỳ file production nào.
> Mọi hành động dựa trên cảnh báo **phải qua Mike/user**. Ở mức ALERT script chỉ ghi một
> bus **`question`** (loại event cần người quyết định) — không bao giờ ghi `decision`.
> Cả hai điều này được assert trong selfcheck (`monitor_khong_ghi_vao_log_production`,
> `escalate_ghi_question_khong_phai_decision`).

## 1. "Kỳ vọng" là gì — định nghĩa và nguồn

Đóng băng ở `orb_drift_baseline.json`, lấy từ **Việc A, chỉ 670 phiên PRE-LIVE** của
**đúng config đang deploy** (không dùng phiên live nào — nếu dùng thì monitor so live với
chính live và không bao giờ báo được gì):

| | giá trị |
|---|---|
| mean/phiên μ₀ | **+9,341 bps** |
| sd/phiên σ₀ | **93,09 bps** |
| SNR = μ₀/σ₀ | **0,1003** |
| Sharpe_ann | +1,59 |
| win rate | 52,5% |
| skew / kurtosis | +0,02 / **5,76** |
| long fraction | 50,1% |
| mean \|OR\| | 0,231% |

Ngoài moment, baseline còn chứa **envelope bootstrap** (40.000 lần, khối liên tiếp) cho
`cum` và `sd` của k ∈ {10,20,25,30,40,50,60,75,100,125,150} phiên liên tiếp. Đây là phần
làm nên tính "calibrated by construction" của ngưỡng ở tầng T1.

## 2. Ràng buộc vật lý phải nói trước (quyết định toàn bộ thiết kế)

SNR = 0,1003/phiên. Hai hệ quả **đo bằng mô phỏng ARL trên residual THẬT** (giữ kurtosis
5,76), không lấy từ bảng Gauss — `calibrate_cusum.py`, `calibrate_cusum2.py`:

1. Cần **~614 phiên** để phân biệt μ₀ với 0 ở α=5%/power=80%. Hiện có **75**.
2. CUSUM nhắm "edge về 0" ở ngưỡng đủ nhạy (h=5–10) cho **ARL0/ARL1 chỉ 1,6–2,2** —
   tức báo động khi hỏng và khi KHÔNG hỏng xảy ra gần như như nhau (FPR/250 phiên
   72–99%). Rolling-N Sharpe còn tệ hơn: ở N=25, sd của Sharpe annualised ≈ 3,2.

**Kết luận thẳng: không tồn tại ngưỡng nào vừa nhạy vừa ít báo giả TRÊN CHUỖI LỢI NHUẬN.**
Vì vậy thiết kế chia 4 tầng theo **độ phát hiện được**, và nói rõ tầng nào là "phát hiện
thật", tầng nào chỉ là "hiện trạng".

## 3. Bốn tầng

### T0 — Sức khoẻ số liệu (power cao, phát hiện trong 1 phiên) → nơi có giá trị thật
Hầu hết cách một paper program "lệch kỳ vọng" trong thực tế là **hỏng đường ống**
(vendor đổi dữ liệu, log đứt, công thức pnl đổi, size sai), không phải alpha decay.

| check | ngưỡng | mức |
|---|---|---|
| trùng ngày / ngày không tăng đơn điệu / NaN | bất kỳ | ALERT |
| `net` tái tính từ `entry/exit/sig` | lệch > 1e-9 | ALERT |
| cột `nav` khớp `net` | lệch > 1 VND | ALERT |
| độ tuổi sổ paper | > 1 phiên → WARN; > 3 phiên → ALERT | WARN/ALERT |
| biến động sd (envelope bootstrap, k lớn nhất ≤ n) | > p95 → WARN; > p99,5 → ALERT; **sụp đổ** (< p0,5 **và** < 50% σ₀) → ALERT | WARN/ALERT |
| cân bằng long/short (binomial) | p < 0,01 | WARN |
| biên độ OR (đặc tính tape) | p < 0,01 | WARN |
| \|net\| > 6σ | bất kỳ | WARN |
| vendor revision log | có dòng | WARN |

Hướng của check sd **không đối xứng có chủ ý**: sd thấp hơn kỳ vọng không phải vấn đề
(chỉ là phiên êm); chỉ báo khi sd **vượt trần** (rủi ro đang bị ước thiếu) hoặc **sụp đổ**
(dấu hiệu đường ống hỏng).

Độ tuổi sổ dùng `trading_days_between()` có **loại nghỉ lễ VN** qua
`trading_bot.vn_market.is_holiday` — `np.busday_count` trần đếm kỳ Quốc khánh 31/08→02/09
thành 4 "trading day" (coding_guidelines §16 RULE 2, incident 2026-09-04). Selfcheck
`trading_days_between_loai_nghi_le` pin đúng ca đó: holiday-aware **1** vs busday trần **4**.

### T1 — Envelope phân phối (ngưỡng calibrated by construction) → TÍNH vào trạng thái
`cum` của k phiên gần nhất so với phân phối `cum` của k phiên **liên tiếp** trong 670
phiên pre-live. `< p5` → WARN, `< p1` → ALERT. Ngưỡng p5 fire đúng 5% thời gian khi mọi
thứ bình thường — đó là **định nghĩa** của ngưỡng, không phải ước lượng.

Chỉ **2 cửa sổ** tính vào trạng thái: dài nhất (toàn bộ live) + 25 phiên (gần đây). Cửa sổ
trung gian in ra ở tier `T1i` (INFO) và **không** tính. Lý do: vòng 1 dry-run tính cả 6
cửa sổ chồng lấn → tỷ lệ WARN đội lên 19,6% trên dữ liệu bình thường, cao hơn nhiều mức 5%
mà ngưỡng p5 hứa.

### T2 — CUSUM (phát hiện CHẬM, chỉ bắt sự cố lớn)
`S_i = max(0, S_{i-1} − (x_i − k)/σ₀)`, h chọn bằng **mô phỏng ARL** (30–40k đường,
bootstrap residual thật):

| | mục tiêu | k | h | ARL0 | ARL1 | FPR/250 phiên | mức |
|---|---|---|---|---|---|---|---|
| **A_warn** | μ → 0 (edge chết) | μ₀/2 = +4,67 bps | **18** | 809 | 215 | 26,6% | WARN |
| **B_alert** | μ → −μ₀ (edge đảo dấu) | 0 bps | **22** | 3.580 | 184 | 6,7% | ALERT |

A_warn cố ý lỏng (FPR 27%/năm) vì WARN chỉ ghi log. B_alert là tầng escalate: bắt đảo dấu
hoàn toàn trong ~184 phiên với 6,7% báo giả mỗi năm (tỷ số ARL0/ARL1 = **19,4** — đây là
thiết kế CUSUM duy nhất trong bài toán này có tỷ số dùng được).

**Nói thẳng:** ngay cả tầng ALERT cũng cần ~184–300 phiên để phát hiện một lần đảo dấu
hoàn toàn. Selfcheck pin đúng điều này: ở 184 phiên đảo dấu S mới đi được > 50% ngưỡng,
phải tới 400 phiên mới chắc ALERT.

### T3 — SPRT: **thanh tiến độ, KHÔNG phải trigger**
H0: μ=μ₀ vs H1: μ=0, α=0,05, β=0,20 → biên `+2,773` / `−1,558`.
LLR mỗi phiên = ((μ₁−μ₀)/σ₀²)·(x − (μ₀+μ₁)/2). Kỳ vọng ~551 phiên để kết luận "edge chết"
nếu edge thực sự = 0; ~310 phiên để kết luận "edge còn sống" nếu edge đúng bằng μ₀.
In ra LLR + còn bao nhiêu phiên nữa — **để không ai tưởng đã có kết luận.**

## 4. Hành động theo mức

| mức | exit code | hành động |
|---|---|---|
| **OK** | 0 | không làm gì, ghi 1 dòng log |
| **WARN** | 10 | ghi log + 1 dòng trong báo cáo paper kế tiếp. **Không** escalate, **không** đổi gì |
| **ALERT** | 20 | escalate bus `question` cho Mike (cần cờ `--escalate`). **Không** tự dừng paper, **không** tự đổi tham số. Mike/user quyết định |

Mặc định `--escalate` **TẮT** — chạy monitor không bao giờ tự ghi lên bus nếu không được
bật tường minh.

## 5. Validate thiết kế trước khi đề xuất đưa vào sản xuất

**5a. Dry-run false-positive** — `python3 orb_drift_monitor.py --replay`: phát lại từng
phiên từ phiên 20 → 75 (56 lần chạy) trên chính 75 phiên mà Việc B đã xác nhận là bình
thường (phân vị 50 của phân phối kỳ vọng).

| trạng thái | số lần | tỷ lệ |
|---|---|---|
| OK | 50 | 89,3% |
| WARN | 6 | 10,7% |
| **ALERT** | **0** | **0,0%** |

6 lần WARN đều từ envelope 25-phiên, dồn vào đoạn drawdown 08→09/2026 — nhất quán với mức
p5 danh nghĩa khi cửa sổ chồng lấn. WARN = chỉ ghi log, chấp nhận được.

> **Vòng 1 của dry-run KHÔNG đạt: 8/56 lần ALERT giả (14,3%).** Nguyên nhân: bản đầu dùng
> **χ² hai phía** cho check sd, mà χ² giả định chuẩn còn phân phối lợi nhuận có kurtosis
> 5,76 ⇒ p-value của nó sai ở n nhỏ; thêm nữa sd THẤP bị tính là lỗi. Đã thay bằng
> **envelope bootstrap một phía + nhánh sụp-đổ riêng**. Đây chính là tác dụng của bước
> validate này — không phải hình thức.

**5b. Selfcheck mutation — chứng minh monitor KHÔNG vacuous.** Dry-run chỉ chứng minh
không báo giả; một monitor luôn trả OK cũng qua được bước đó.
`orb_drift_monitor_selfcheck.py`: **22/22 PASS**, mỗi assert có tên.

Bơm từng dạng hỏng: trùng ngày · NaN · công thức pnl đổi (×1,5) · cột nav lệch · sổ cũ 17
phiên (ALERT) và trễ 2 phiên (chỉ WARN) · nghỉ lễ · sd phình ×2,2 (205bps → ALERT) · sd sụp
đổ (0,18bps → ALERT) · sd thấp hợp lý (70bps → **không** báo, đúng thiết kế bất đối xứng) ·
edge chết 200 phiên (CUSUM-A kêu) · edge đảo dấu 184/400 phiên · sụp đổ nhanh (envelope
p1) · toàn long · outlier 6σ · SPRT đạt biên H1 sau 675 phiên · 2 assert về phạm vi
(không ghi production, escalate là `question`).

**5c. Độc lập môi trường** (coding_guidelines §16 + skill `verify-before-done`): PASS 22/22
dưới **cả hai** interpreter (`python3` 3.10 và `$DNA_PYEXE` 3.12) và dưới `env -u TZ`,
`TZ=America/New_York`, `TZ=UTC`. Bước này bắt được một bug thật: bản đầu wrap
`sys.stdout` bằng `TextIOWrapper` mới, khi bị import bởi selfcheck (đã tự wrap) thì wrapper
cũ bị GC và **đóng luôn buffer gốc** → `I/O operation on closed file`, chỉ hiện dưới 3.12.
Đã sửa thành `sys.stdout.reconfigure()`. Không chạy đa-interpreter thì không thấy.
`normstat.py` (Φ/Φ⁻¹ tự viết, không cần scipy) cũng được đối chiếu ngược lại scipy:
max|dCDF| 2,4e-17, max|dPPF| 1,1e-11.

## 6. Còn thiếu gì trước khi Mike cân nhắc triển khai

1. **Chưa cài cron** — cố ý, để Mike quyết định sau khi xem thiết kế. Nếu cài: sau
   `orb_pt.py` hằng ngày (≥15:00 ICT), và phải vào `kb/cron_registry.md`
   (coding_guidelines §11).
2. **Vị trí file**: hiện ở `research/`. Nếu thành công cụ vận hành thì nên chuyển sang
   `mike/bin/` + baseline vào `data/` — kèm §10 (archive biến thể bị thay thế).
3. **Baseline sẽ cũ**: nó là ảnh của 670 phiên pre-live. Nếu config đang chạy **đổi** thì
   baseline **phải dựng lại** (`make_baseline.py`) — nó pin `orb_pt.py` sha256 nhưng
   **chưa tự kiểm** hash đó lúc chạy. Đề xuất bổ sung nếu đưa vào sản xuất.
4. **Rủi ro vận hành liên quan trực tiếp tới T0**: `orb_pt.py` đang gọi API vnstock **đã bị
   ngừng hỗ trợ** (`Vnstock().stock(...).quote.history(...)`). Hiện chỉ in cảnh báo migration.
   Khi vendor bỏ hẳn, paper program sẽ **im lặng đứt** — và đó chính là ca mà check "độ tuổi sổ
   paper" của T0 tồn tại để bắt (> 3 phiên → ALERT). Đường thay thế đã xác nhận chạy:
   `from vnstock.api.quote import Quote; Quote(symbol=..., source='VCI').history(...)`.
   Chưa sửa — ngoài phạm vi job, cần Mike quyết định.
5. **Giới hạn dữ liệu của baseline**: vendor không có bar 1 phút nào trước **2023-09-11** (thử
   trực tiếp 2026-09-25: mọi request sớm hơn trả `RetryError`). VN30F1M chạy từ 2017-08-10 ⇒
   baseline dựng từ 3,04 năm của một công cụ 9,1 năm, thiếu đúng 2018 / COVID 2020 / bear 2022.
6. **Điểm mù đã biết**: baseline được dựng từ một giai đoạn mà DT5G gần như luôn NEUTRAL.
   Monitor sẽ coi một regime BEAR/CRISIS là "lệch kỳ vọng" mặc dù đó có thể là hành vi
   bình thường trong regime chưa từng lấy mẫu. Không sửa được bằng thống kê — chỉ ghi rõ.

## 7. File

| file | vai trò |
|---|---|
| `orb_core.py` | tái dùng CHÍNH xác logic `orb_pt.py` (self-check ngược sổ paper 75/75 @1e-16) |
| `viec_a_validate.py` / `viec_a_result.json` | A1–A5 |
| `viec_a_robust.py` / `viec_a_robust_result.json` | A6 trễ thực thi + chi phí + bootstrap |
| `neighbourhood_grid.csv` | 60 tổ hợp lân cận |
| `viec_b_live.py` / `viec_b_result.json` | Việc B |
| `calibrate_cusum.py`, `calibrate_cusum2.py`, `cusum_arl*.json` | mô phỏng ARL chọn h |
| `make_baseline.py` / `orb_drift_baseline.json` | đóng băng kỳ vọng |
| `normstat.py` | Φ/Φ⁻¹ không cần scipy (chạy được dưới cron python3) |
| **`orb_drift_monitor.py`** | monitor 4 tầng |
| **`orb_drift_monitor_selfcheck.py`** | 22 assert mutation |
| `drift_monitor_replay.csv` | kết quả dry-run từng phiên |
