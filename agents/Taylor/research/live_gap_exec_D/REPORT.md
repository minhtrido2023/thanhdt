# Luồng D: trả nợ GĐ2/GĐ3 theo quant-skeptic (job `Taylor_20261112_151837`, resume `Taylor_20261112_162001`, 12/11/2026)

Brief: `brief.md`. PAPER-ONLY: không wire, không merge, không đổi production, `trading_rules.json` không đổi.
Code engine: worktree `/home/trido/thanhdt/WorkingClaude/wt-livegap-D-1112` @ `14fff84a7` (engine `sb` + knob carry), sandbox `sb_D/` (`make_sandbox.sh`), data đóng băng `bq_cache_asof20260729_postrestate` + frozen_lag phase1b; chạy chân bằng `run_leg.sh`.
md5 mọi output: `MD5SUMS`.

## 0. Tóm tắt

**D1 (GĐ3):**
- **P(V2.4 thắng tiết kiệm 12T trong cửa sổ 12T) phụ thuộc giả định lãi tiền nhàn rỗi.** Hai đầu dải: **77,6% (pin0%) … 84,6% (pin1M)**. Nếu trừ 1,5pp/năm (quy đổi CAGR thật): **74,0% … 82,1%**.
- CI90 theo N_eff thì rộng hơn nhiều so với con số 65–88% của GĐ3:

  | Cách tính CI90 | pin0% | pin1M |
  |---|---|---|
  | Clopper–Pearson, n_eff = 9 | 45–96% | 52–98% |
  | Đếm thật 12 cửa sổ tháng 1 không chồng (pin0% 10/12, pin1M 10/12) | 56–97% | 56–97% |
  | Bootstrap khối 36 tháng | 71–85% | 77–93% |
- **Chính sách "chuyển sang tiết kiệm 1T khi DT5G ∈ {CRISIS, BEAR}"**, so cùng quy ước lãi nhàn rỗi, trễ T+1:

  | | pin0% | pin1M |
  |---|---|---|
  | CAGR | **−0,90pp** | **−1,78pp** |
  | MaxDD | +4,5pp | +2,7pp |
  | Sharpe | +0,19 | +0,14 |
  | Hạng so với placebo khối tháng (DD / Sharpe) | 92% / 98% | 88% / 97% |

  Câu "CAGR gần như không đổi" của GĐ3 **sai, gỡ bỏ**. Chính sách này tốn lợi nhuận để đổi lấy DD, tức là **bảo hiểm**, khớp với KB.
- **Sizing:** cân lại hằng ngày với tiết kiệm 12T là không thực hiện được. Thay bằng tiết kiệm 1T thì **P(thắng) giảm khi w giảm**: pin0% w=0,3 còn 66% so với 78% ở w=1. Câu "P(thắng) không phụ thuộc w" của GĐ3 **chỉ đúng với chân 12T không khả thi**.
- **Nguồn PE:** lý do đổi nguồn PE trong GĐ3 sai (`VNINDEX_PE` có dữ liệu từ 2006-03-30). `VNINDEX_pe_only.csv` đã được đăng ký vào data_registry với trạng thái **DEPRECATED**.

**D2 (GĐ2B):**
- Đồng hồ DT đã dựng lại đúng: replay khớp `get_dt_gate_clock()`, lệch 0/3207 phiên.
- Nhị phân kiểm bằng point-biserial; placebo dùng khối tháng R=500; MDE tính theo luật quyết định thật (BH + cả hai era, nsim=400).
- Kết quả: **0 đặc trưng qua** trên mọi tập (liqz_all, liqz_adv100, old_adv100, phí native).
- MDE80 theo luật trên liqz_all: **BAL ρ≈0,5, LAG ρ≈0,3**. Ngoài ra là "không đủ lực".
- H5: không tách được khỏi mức năm, chỉ có 1–6 episode.

**N trials:** D2 có họ FDR 91 phép (IS) / 92 phép (OOS) mỗi tập, 4 tập. D1 không thêm phép thử điều kiện mới: (a), (c), (f) là mô tả; (b) là 1 chính sách tham chiếu đã khai trong PREREG GĐ3, chạy × 2 quy ước × 2 đoạn.
**N độc lập:** 12T không chồng ≈ 12 cửa sổ (9–12); D2 có 28–43 cụm tháng mỗi ô; chính sách có 28 lần đổi, 16 lần từ 2019-03.

## 1. Engine (self-check)

| Chân | Lệnh (`run_leg.sh <TAG> <sb_D> <sb_D> …`) | Ledger md5 | Self-check | CAGR / Sharpe / MaxDD |
|---|---|---|---|---|
| **P0 pin0% (CONTROL)** | `LIQ_ZERO_BLOCK=lag BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0 IDLE_CARRY_TIER=off` | `84f796bdedde8fefa02b37012e65bdde` = **byte-identical** ledger P0 của GĐ3 | BAL/LAG cash-flow 0 VND, NAV identity 0 VND (`logs/exp_gapD_p0_off.log`) | 23,39% / 1,82 / −17,1% |
| **P0 pin1M** | như trên, `IDLE_CARRY_TIER=dep1m` | `35c8968f81cf68d3721c4c549e4eaafd` | 0 VND (`logs/exp_gapD_p0_dep1m.log`) | 26,77% / 2,05 / −14,8% |

- Knob carry giống pin registry `## 2026-10-08 — ⭐ R3 ĐO Ở KNOB LIVE park=0`: tier `dep1m` của `idle_rate_proxy.py`, trả theo ngày, PIT (mốc tháng T dùng từ đầu tháng T+1).
- Log chân pin1M ghi độ phủ dep1m 2014-01..2026-06: 89 tháng SỐ THẬT, 53 tháng DỰNG LẠI (từ sbv_low − 2,525pp), 8 tháng ffill.
- Khác pin 10-08 ở `LIQ_ZERO_BLOCK=lag`, code vá mergesort và data frozen. Vì vậy 26,77% **không so được** với số pin 25,42%: đây là cặp đối chiếu nội bộ của Luồng D, không phải số để re-pin.
- Trạng thái DT5G (`state`) của hai chân trùng nhau 100% (assert trong `D1/analyze_d1.py`).

## 2. D1 — GĐ3 sửa (`D1/`, lệnh `D1/REPRO_cmd.txt`, log `D1/analyze_d1.log`)

### (a)+(c) P(thắng 12T) hai đầu dải + CI theo N_eff (`d1ac_pwin.csv`, `d1a_pwin_by_year.csv`, `d1c_nonoverlap_offsets.csv`)
Cách tính nhãn:
- excess = NAV(s+12T)/NAV(s) − 1 − tiết kiệm cùng kỳ.
- Cột "hurdle 12T" dùng `deposit_rate_vn` (26 mốc neo hồi tố, chỉ dùng làm nhãn ex-post).
- Cột "hurdle 1T" dùng dep1m (số thật PIT từ 2019-02; trước đó là dựng lại, không PIT).
- "−1,5pp" nghĩa là NAV × (1−0,015)^năm.

| Chân | −1,5pp | Nhãn | P(thắng) | Bootstrap khối 12 | Bootstrap khối 36 | Wilson n=9 | CP n=9 | CP n=12 | Tháng 1 không chồng k/n (CP90) | 12 offset tháng: P min–max |
|---|---|---|---|---|---|---|---|---|---|---|
| pin0% | không | 12T | **77,6%** | 65–89 | 71–85 | 50–92 | 45–96 | 50–94 ᵃ | 10/12 (56–97) | 73–83% |
| pin0% | có | 12T | **74,0%** | 60–86 | 68–82 | 47–90 | 41–94 | — | 9/12 (47–93) | 58–83% |
| pin1M | không | 12T | **84,6%** | 73–94 | 77–93 | 58–96 | 52–98 | — | 10/12 (56–97) | 73–100% |
| pin1M | có | 12T | **82,1%** | 70–93 | 74–90 | 55–95 | 50–98 | — | 10/12 (56–97) | 73–100% |
| pin0% | không | 1T | 84,4% | 73–94 | 77–92 | 57–96 | 52–98 | — | 11/12 | 73–100% |
| pin1M | không | 1T | 91,4% | 84–98 | 86–97 | 65–98 | 60–100 | — | 12/12 (78–100) | 82–100% |

ᵃ Các ô CP n=12 khác nằm trong `d1ac_pwin.csv` (cột `cp_n12_*`). Wilson n=12 cho pin0% không trừ là 54–91%.

Cách đọc:
- **Dải đúng để trích dẫn: 74–85% (P điểm, hai đầu dải × có/không −1,5pp, nhãn 12T).** CI90 trung thực theo N_eff ≈ 9–12 rơi vào khoảng **45–98%**.
- Bootstrap khối 12 tháng (65–88% của GĐ3) **quá hẹp** so với CI theo N_eff. Khối 36 lại cho CI HẸP hơn khối 12 — ngược trực giác; chưa chẩn đoán trong phiên này (`block_ci` của GĐ3 nối vòng, ~144 tháng chỉ có 4 khối/mẫu), nên không dùng bootstrap làm CI chính.
- Vì vậy chỉ dùng **Clopper–Pearson trên số cửa sổ không chồng** làm cận bảo thủ.
- Theo era (12T, không trừ):

  | | IS | 2019 | OOS |
  |---|---|---|---|
  | pin0% | 82% | 36% | 81% |
  | pin1M | 94% | 38% | 85% |
- Theo năm khởi đầu, chênh lệch giữa hai đầu dải tập trung ở **2016**: 59% ở pin0% so với 100% ở pin1M. Năm đó nắm nhiều tiền nhàn rỗi, nên giả định lãi quyết định kết quả.
- 2019 (36% / 38%) và 2022 (20% / 34%) vẫn là năm thua ở cả hai đầu.

### (b) Chính sách "tiết kiệm khi DT5G ∈ {CRISIS,BEAR}", hai chân cùng quy ước (`d1b_policy.csv`)
Cách dựng:
- Engine và chính sách đọc **cùng một ledger**, nên tiền nhàn rỗi bên trong engine có cùng quy ước lãi.
- Khi tắt engine, chính sách hưởng lãi **1T** (dep1m tier của `idle_rate_proxy`). Trạng thái tại t áp dụng từ phiên t+1 (T+1); phí 0,1% mỗi lần đổi.
- Placebo **khối tháng**: trong mỗi năm, hoán vị thứ tự nguyên các khối tháng của mặt nạ tắt (giữ % tắt của năm và cấu trúc trong tháng), 500 lần.

| Quy ước | Đoạn | % tắt | Số lần đổi | CAGR engine → chính sách | ΔCAGR | MaxDD engine → chính sách | ΔDD | Sharpe Δ | Hạng placebo CAGR / DD / Sharpe |
|---|---|---|---|---|---|---|---|---|---|
| pin0% | 2014–2026-06 | 23,5% | 28 | 23,39 → 22,49% | **−0,90pp** | −17,1 → −12,6% | +4,5pp | +0,19 | 96% / 92% / 98% |
| pin0% | 2019-03+ (lãi 1T là số thật) | 29,2% | 16 | 25,60 → 23,96% | **−1,64pp** | −17,1 → −12,6% | +4,5pp | +0,18 | 87% / 98% / 93% |
| pin1M | 2014–2026-06 | 23,5% | 28 | 26,77 → 24,99% | **−1,78pp** | −14,8 → −12,1% | +2,7pp | +0,14 | 94% / 88% / 97% |
| pin1M | 2019-03+ | 29,2% | 16 | 28,84 → 26,18% | **−2,66pp** | −14,5 → −12,1% | +2,4pp | +0,12 | 83% / 70% / 90% |

Đọc kết quả:
- Cùng quy ước thì chính sách **tốn 0,9–2,7pp CAGR**, đổi lại DD giảm 2,4–4,5pp và Sharpe tăng 0,12–0,19.
- Câu "CAGR 23,2% so với 23,4%, gần như không đổi" của GĐ3 là sản phẩm của việc so lệch quy ước (engine lãi 0% vs chính sách lãi 12T). **Gỡ bỏ.**
- Hạng so với placebo khối tháng thấp hơn hạng so với placebo trong-năm của GĐ3 (98/99%). Ở pin1M 2019+, hạng DD chỉ 70%, nghĩa là không phân biệt được với tắt ngẫu nhiên theo tháng.
- Kết luận giữ: **bảo hiểm DD, không phải nguồn lợi nhuận.** Không phải ứng viên.
- Ghi chú: lãi 1T trước 2019-02 là dựng lại (54 tháng `recon`), **không PIT**. Đoạn 2019-03+ mới sạch.

### (d) Khai báo + sửa lý do PE
- **Lần chạy thử P30 trước bản cuối (GĐ3):** skeptic ghi nhận GĐ3 có một lần chạy thử trên chân P30 trước bản cuối, nhưng REPORT GĐ3 không khai. Dấu vết còn lại:
  - `analyze.py` sửa lần cuối lúc 20:38:08 (+07). Thời điểm này SAU heartbeat "analyze.py viết xong, chờ engine P0" (13:37:26Z = 20:37:26) và TRƯỚC lần chạy chính (heartbeat 20:38:35).
  - Kết quả lần chạy thử không được lưu.
  - Transcript phiên GĐ3 không còn truy được trong `~/.claude/projects` (chỉ thấy phiên Mike tham chiếu job), nên **không xác minh được** lần thử đó đã xem những gì.
  - Bằng chứng không có điều chỉnh sau khi xem kết quả: `PREREG.md` md5 hiện tại `7c9bde3f7518ef5f9de857517e307703` = md5 phát lên bus lúc 13:33Z. Biến, ngưỡng và thước đo không đổi.
  - Lần thử được tính là **1 lần xem dữ liệu chưa khai**. Nó không làm đổi null 0/6, vì không có biến nào gần ngưỡng: q IS 0,945, q OOS ≥ 0,977.
- **Lý do đổi nguồn PE, sửa lại:** GĐ3 viết "`VNINDEX.csv` chỉ có `VNINDEX_PE`, NULL trước 2016". Câu này **sai**. Đo lại:
  - `VNINDEX_PE` trong `data/VNINDEX.csv` có 5008 phiên non-null, **2006-03-30 → 2026-05-26** (backfill ngày 2026-07-29).
  - So với `VNINDEX_pe_only.csv` (cột `Pe`, 2014-01-02 → 2026-03-30):

    | Giai đoạn | Số phiên | Khớp | max\|Δ\| |
    |---|---|---|---|
    | 2014–2018 | 1245 | trùng 100% | 0 |
    | 2019+ | 1803 | 85,0% phiên có \|Δ\| < 0,01 | 3,99 |
  - Brief ghi "trùng từ 2019" là ngược chiều: chỗ trùng tuyệt đối là 2014–18; 2019+ chỉ gần trùng (corr 0,989).
  - GĐ3 bước 4 chỉ dùng tháng 2019+, nên ~15% phiên có PE lệch nhẹ. Kết luận bước 4 (2–6 episode/lớp, không có bằng chứng) không phụ thuộc vào chênh lệch này. Chưa chạy lại bước 4 với `VNINDEX_PE`.

### (e) data_registry
Mục mới: `mike/kb/data_registry/research-caches/vnindex_pe_only_csv.md`, trạng thái **DEPRECATED**. Đã thêm dòng vào index nhóm và CHANGELOG. Bằng chứng xác minh:
- Writer duy nhất là `rebuild_vnindex_csv.py:50`: shutil.copy bản VNINDEX.csv cũ trước khi rebuild; không có cron.
- mtime 2026-05-10 20:37.
- So sánh với VNINDEX.csv như mục (d).
- Readers còn sống: 2 script research.

### (f) Sizing (`d1f_sizing.csv`)
- **Chân "tiết kiệm 12T cân lại hằng ngày" của GĐ3 không thực hiện được.** Rút trước hạn mất lãi kỳ hạn, nên phần (1−w) không thể hưởng lãi 12T nếu cân lại hằng ngày. Thay bằng **lãi 1T** (dep1m, cân lại hằng ngày vẫn là giản lược; thực tế là cuộn 1T).

| Chân | w | CAGR | MaxDD | Bootstrap MaxDD p5 | P(thắng tiết kiệm 12T) | Thua trung vị |
|---|---|---|---|---|---|---|
| pin0% + 1T | 0,3 / 0,4 / 0,5 / 0,6 / 0,8 / 1,0 | 9,3 / 11,3 / 13,3 / 15,2 / 19,3 / 23,4% | −4,4 / −6,1 / −7,7 / −9,3 / −13,2 / −17,1% | −5,9 / −8,4 / −10,9 / −13,5 / −18,7 / −23,6% | 66 / 70 / 73 / 74 / 76 / 78% | −2,2 … −4,0pp |
| pin1M + 1T | cùng w | 10,2 / 12,5 / 14,8 / 17,1 / 21,9 / 26,8% | −4,3 / −5,8 / −7,4 / −8,9 / −11,9 / −14,8% | −5,5 / −7,8 / −10,0 / −12,2 / −16,8 / −21,4% | 73 / 78 / 81 / 83 / 84 / 85% | −1,8 … −2,9pp |
| pin0% + 12T (GĐ3, tham chiếu) | cùng w | 11,2 … 23,4% | | −5,1 … −23,6% | 78–79% (phẳng) | |

Đọc kết quả:
- w lớn nhất có MaxDD-p5 bootstrap ≥ −10% / −15% / −20%, chỉ trên lưới w = 0,3 / 0,4 / 0,5 / 0,6 / 0,8 / 1,0 (không có 0,7 và 0,9):

  | Chân | −10% | −15% | −20% |
  |---|---|---|---|
  | pin0% + 1T | 0,4 | 0,6 | 0,8 |
  | pin1M + 1T | 0,5 (−9,99%, sát biên) | 0,6 | 0,8 |
- **Độ nhạy theo lãi 1T: P(thắng tiết kiệm 12T) GIẢM khi giảm w** (pin0%: 78% → 66% khi w 1,0 → 0,3). Lý do: phần (1−w) hưởng lãi 1T, thấp hơn lãi 12T dùng làm hurdle.
- Vì vậy câu "đổi w chỉ co giãn độ lớn của lần thua, không đổi xác suất thua" chỉ đúng với chân 12T không khả thi. Với chân thực hiện được, giảm w **làm tăng** xác suất thua so với tiết kiệm 12T, nhưng giảm độ lớn của lần thua.

## 3. D2 — GĐ2B sửa (`D2/`, chạy `analyze_d2.py [tag]`, `episodes_d2.py`; log `D2/analyze_d2.log`)

**(a) Đồng hồ DT dựng lại** (`clock.py`, `dt_clock_daily.csv`, `clock_selfcheck.json`, `clock_truncation_check.log`)
- `dtc_k` là streak của ứng viên trong DT 4-gate, theo logic `get_dt_gate_clock()`.
- Selfcheck:
  - Trạng thái commit so với DT4-gate: lệch 0.
  - k cuối episode (non-commit): lệch 0 trên 129 episode.
  - Replay truncation: 3206 phiên, lệch 0.
  - Cache so với BQ: 3207 phiên chồng, lệch 0.
  - Kết quả hôm nay khớp `get_dt_gate_clock()`: committed=3, inactive.
- Định nghĩa cũ `state_raw≠state` thực chất là **macro cap DT5G vs DT4** (50 ngày), không phải đồng hồ.

**(b) Đặc trưng nhị phân kiểm bằng point-biserial** (họ FDR mới: 91 IS / 92 OOS, liqz_all)
- Nay đã kiểm thêm `cfoa_pos`, `dt5g_state` (BAL IS), `dtc_active`, `refi_chg6m` (BAL IS).
- Không ô nào qua. Ô mạnh nhất là `cfoa_pos` LAG IS: r +0,149, p 0,005, q 0,152. Ô này OOS ≈ 0 (r −0,000, q 0,99).
- `dtc_k`: |ρ| ≤ 0,18, q ≥ 0,48 ở mọi ô.
- Không kiểm được: `comm_chg3m` BAL IS (n<30).

**(c) Placebo khối tháng và MDE theo luật**
- Placebo R=500, B=500. Với liqz_all, placebo có trung bình 0,71 phát hiện q<0,10 ở IS và 4,12 ở OOS (p95 OOS = 13). Thật có 1 / 1.
- Chỉ 2% lần placebo qua cả hai era. Thật: 0 qua.
- MDE80 theo **luật quyết định thật** (cấy ρ vào cả IS và OOS, BH q<0,10 cùng (m−1) p thật, nsim=400):

  | Tập | BAL | LAG |
  |---|---|---|
  | liqz_all | ρ ≈ 0,5 (lực 0,845) | ρ ≈ 0,3 (lực 0,92; ρ 0,25 cho 0,79) |
  | liqz_adv100 và old_adv100 | > 0,5 | > 0,5 |
- MDE80 ở các tập lọc ADV lớn hơn vì m thật có p nhỏ hơn hoặc vì n giảm (`mde_rule_*.csv`).

**(d) Phí native (liqz_all)**
- 0 qua. Các ô gần như y hệt: q min mỗi ô IS-BAL 0,152 / IS-LAG 0,046 / OOS-BAL 0,046 / OOS-LAG 0,215.

**(e) liqz_adv100**
- 0 qua. Ô gần nhất là `comp_v3` và `FSCORE` LAG IS (q 0,091), nhưng OOS chỉ ρ 0,04, q 0,90.

**Value LAG** (`value_lag_decay_liqz_all.csv`; trả lời yêu cầu skeptic sửa claim 7)
- `ey`: ρ IS +0,145 → OOS +0,084, Δ +0,061, CI [−0,107, +0,233], p(Δ≤0) 0,28.
- `comp_v3`: +0,139 → +0,038, Δ CI [−0,054, +0,253], p 0,15.
- Cách đọc đúng: IS dương nhỏ, ổn định qua các tập sạch; OOS gần 0. Bản thân **mức suy giảm không có ý nghĩa thống kê**. Vì vậy cả "suy giảm thật" lẫn "hiện vật fill ảo" đều không đứng; đây là **không đủ lực**.

**(f) H5 hai band + Δ trong-năm** (`h5_d2.csv`; chuỗi fiinprox dep1m PIT)

| Tập | Band | Gồm 2026 | Episode có sự kiện | n trong/ngoài | Δ thô | Δ trong-năm | Episode âm/dương (trong-năm) |
|---|---|---|---|---|---|---|---|
| liqz_all | 0,0 | có | 6 | 124/430 | −1,18 | −0,37 | 4/2 |
| liqz_all | 0,0 | bỏ | 5 | 96/415 | +2,45 | −0,10 | 3/2 |
| liqz_all | 0,2 | có | 2 | 42/512 | −10,78 | −0,55 | 1/1 |
| liqz_all | 0,2 | bỏ | 1 | 14/497 | −1,32 | +0,48 | 0/1 |
| liqz_adv100 | 0,0 / 0,2 | có | 6 / 2 | | −1,29 / −10,39 | −0,39 / −0,32 | |
| old_adv100 | 0,2 | có | 2 | 10/381 | −15,56 | −4,08 | 2/0 |

- Δ thô −10,8pp ở band 0,2 đến từ **một episode 2026**. Bỏ episode đó thì còn −1,3pp.
- Khử mức năm hấp thụ gần hết hiệu ứng.
- Kết luận: **H5 không tách được khỏi mức năm; N = 1–6 episode ⇒ không kết luận.**

### Bảng kết luận D2

| Đặc trưng | Kết luận |
|---|---|
| (bất kỳ) | **Sống sót: không có** (0 qua BH q<0,10 cả hai era, trên cả 4 tập) |
| `dtc_k`, `dtc_active`, `dt5g_state`, `refi_chg6m`, `cfoa_pos` (BAL), `log_adv20`, H1, quality (`ROE_Min5Y`, `ROIC5Y`) | **Không phát hiện**: ρ IS/OOS nhỏ, dấu không nhất quán, nằm dưới MDE nhưng không có bằng chứng ủng hộ |
| `FSCORE` LAG, `cfoa_pos` LAG, value LAG (`ey`, `comp_v3`, `psy`), `dd52` BAL OOS | **Không đủ lực**: có một era dương với ρ 0,13–0,22 (một số ô q<0,10 ở MỘT era), OOS ≈ 0 hoặc khác tập. Thấp hơn MDE80 (BAL 0,5 / LAG 0,3), nên không bác được cũng không nhận được |
| H5 (hurdle tăng) | **Không đủ lực**: 1–6 episode, không tách được khỏi mức năm |
| `comm_chg3m` BAL IS | Không kiểm được (n<30) |

## 4. Giới hạn
- Tất cả là số backtest. CAGR thật ≈ backtest − 1,5pp (mục a đã có cột trừ). Chưa trừ gap live−engine của GĐ1/1c.
- Lãi 1T trước 2019-02 là dựng lại, không PIT. Hurdle 12T có 26 mốc neo hồi tố, chỉ dùng làm nhãn.
- Ledger dùng LIQ_ZERO_BLOCK=lag + code vá mergesort + data frozen ⇒ không so trực tiếp với các số pin registry.
- Chưa qua quant-skeptic vòng này.
