<!-- ĐỀ XUẤT — CHƯA GHI VÀO data/results_registry.md. Chờ Mike/user duyệt (§13 + ranh giới dispatch
     job Taylor_20260927_170645: "KHÔNG tự ghi results_registry.md").
     Cách áp: (A) append NGUYÊN KHỐI "## 2026-09-28 — ..." dưới đây vào CUỐI file registry;
              (B) áp PATCH §0 ở mục cuối file này vào khối "## ⭐ CONFIG TỐT NHẤT = V2.4".
     Tiêu đề dùng số (septies) — đã `grep -c "septies" data/results_registry.md` = 0. -->

## 2026-09-28 (septies) — ⭐ **RE-PIN R3 THEO QUY ƯỚC TIỀN NHÀN RỖI MỚI `dep1m`** (lãi huy động 1 tháng Big-4) — job `Taylor_20260927_170645` ⚠️ **PAPER + REGISTRY, `trading_rules.json` KHÔNG ĐỔI, rail KHÔNG ĐỔI**

> **ĐÂY LÀ ĐỔI QUY ƯỚC ĐO, KHÔNG ĐỔI MÔ HÌNH.** Park giữ **0,30** y nguyên (knob live không đụng);
> thay đổi duy nhất là bỏ giả định "lãi tiền gửi nhàn rỗi 0%/năm". User chốt 23:58 ICT 2026-09-27
> (Discord): *"Đồng ý giữ lại parking tỉ lệ 0.3. Tiền mặt thì neo theo lãi suất huy động 1 tháng.
> Lấy căn cứ này làm số pin"*.
> Code: worktree `mike/agents/Taylor/wt-repin-dep1m-2809`, branch `research/repin-dep1m-2709`,
> commit **`d3c37631`**. Báo cáo đầy đủ: `mike/agents/Taylor/research/repin_dep1m_20260928/REPORT.md`.

### 1. Số pin

| Đại lượng | Anchor R3 (sexies, carry 0%) | **PIN MỚI (`dep1m`)** | Δ |
|---|---|---|---|
| CAGR | 23,37% | **25,71%** | **+2,34pp** |
| Sharpe(252) | 1,88 | **2,06** | +0,18 |
| MaxDD | −14,6% | **−14,0%** | +0,6pp (hẹp hơn) |
| Calmar | 1,60 | **1,83** | +0,23 |
| Final NAV | 684,52B | **864,86B** | +180,34B |
| IS 2014-2019 | 20,00% | **22,47%** (Sharpe 2,02 / DD −14,0 / Cal 1,60) | |
| OOS 2020+ | 26,50% | **28,71%** (Sharpe 2,08 / DD −13,0 / Cal 2,20) | |
| **Bootstrap DD 5th-pct (NEO SIZING)** | −25,2% | **−23,6%** | +1,6pp |
| Bootstrap CAGR 5th-pct | 15,5% | **17,8%** | |
| P(DD<−30%) | 1,1% | **0,5%** | |
| DSR | 1,0000 | **1,0000** (N=4 / N_reg=120 / N_reg=200) | |
| PBO | 0,2085 (họ 68) | **0,5000** (họ N=4, THOÁI HOÁ) / **0,1258** (họ N=14) | xem §5 |
| ledger md5 | `4707bcbeb7e801d49a4a851ffd91d5e7` | **`bcd0469f42c2f76937a6ebb10aae9b40`** | |
| self-check | 0 VND | **0 VND** (BAL+LAG, cash-flow + final-NAV identity) | |

Cửa sổ 2014-01-02 → 2026-06-19 (12,46y), NAV 50B. OOS > IS ở **mọi** chiều ⇒ edge không rớt OOS.

### 2. Lệnh pin (tái lập)

```bash
# = lệnh pin anchor R3 (job Taylor_20260927_131635) NGUYÊN VĂN, chỉ thêm IDLE_CARRY_TIER=dep1m
SRC=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-repin-dep1m-2809/WorkingClaude   # d3c37631
cd /home/trido/thanhdt/WorkingClaude && export WORKDIR_8L=/home/trido/thanhdt/WorkingClaude \
  CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python \
  TZ=Asia/Ho_Chi_Minh
env BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=dep1m \
  BASKET_CA_SNAPSHOT=/home/trido/thanhdt/WorkingClaude/data/snapshots/corp_action_share_20260927.parquet \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-06-19 EXP_TAG=rp_pin \
  $DNA_PYEXE "$SRC/pt_v23_audit_2014.py" v23a none postbull 0 edge
# ledger -> data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-30_wtnamecap_advprice_etfcreatpit_exp_rp_pin_univpit_idledep1m.csv
```
Runner đóng gói sẵn: `mike/agents/Taylor/research/repin_dep1m_20260928/run_leg.sh`
(phần thực thi **byte-identical** với `run_leg.sh` của W2/Q2, chỉ khác comment + SRC/OUT).

### 3. Cổng bắt buộc đã QUA trước khi đọc bất kỳ số nào
Chân `rp_ctrl` (cùng lệnh, `IDLE_CARRY_TIER=off`) → ledger md5 **`4707bcbeb7e801d49a4a851ffd91d5e7`**,
`cmp` **sạch** vs anchor R3 (`..._exp_reverify_j131635_univpit.csv`) ⇒ **byte-identical**. Thêm tier
không làm lệch đường đi khi tắt ⇒ mọi Δ là của riêng quy ước carry.

### 4. Quy ước `dep1m` là gì (đọc trước khi trích số)
Lãi suất **huy động kỳ hạn 1 tháng, khách CÁ NHÂN, bình quân nhóm Big 4**. **HAI ĐOẠN, KHÁC BẢN CHẤT:**
- **2019-02 → 2026-09: SỐ THẬT** FiinPro công bố (92 tháng, chụp ngày 15). Trong cửa sổ: **89 tháng**.
- **trước 2019-02: DỰNG LẠI** = `SBV 12M-thấp + median(dep1m − SBV 12M-thấp)` = `sbv_low − 2,525pp`.
  Trong cửa sổ: **53 tháng** + 8 tháng khuyết `sbv_low` được forward-fill.
  Lý do phải dựng: route FiinPro trả **HTTP 500 cho mọi ngày ≤ 2018-12**; trial hết hạn 28/09/2026
  ⇒ **không thể kéo thêm, vĩnh viễn**.

Chọn cầu bằng đo, không bằng ý kiến (n=90 overlap, tự đo lại độc lập):
`dep1m − sbv_low` median **−2,525** / sd **0,883** / corr **+0,619** ⇒ dùng được.
`dep1m − liên NH 1M` median −0,240 / sd **2,472** / corr **−0,141** ⇒ **KHÔNG** bắc cầu được.

PIT giữ nguyên: mốc tháng T dùng từ đầu tháng T+1; không back-fill; ngày trước chuỗi ⇒ 0% fail-safe
(engine in ra số phiên — thực tế **0 phiên**). Carry đã áp: mean **3,501%/năm**, min 1,600%, max 4,975%.

### 5. PBO = 0,5000 trên họ N=4 — CHẠM cờ đỏ, và đây là cách đọc đúng
Luật CLAUDE.md: `PBO≥0,5 → chọn config robust-trung vị, không IS-best`. Giá trị 0,5000 ở đây là
**THOÁI HOÁ**, không phải bằng chứng overfit: 4 chân gần cộng tuyến (corr log-return ngày
**0,98771…0,99998**; `rp_pin` vs `rp_p75` = **0,99998**) nên CSCV không phân biệt được chân nào —
logit λ median 0,00, P(λ<0)=0,5 **đúng bằng tung xu**. Trên họ N=14 (thêm 10 chân W2/Q2 cùng phương
tiện cùng ngày) PBO = **0,1258**.
**Remedy của luật đã được làm TRƯỚC khi đo**: offset **median** là luật định trước của dispatch, và
trên số thực tế chân median cho **CAGR THẤP NHẤT** trong 3 chân (25,71 < 25,80 < 25,89) ⇒ không thể
là IS-best-picking.
Manifest ghim tường minh (không glob động): `data/dsr_family_manifest_repin_dep1m_2026-09-28.json`
(N=4) và `…_ext.json` (N=14).

### 6. Băng bất định của cầu — số pin KHÔNG nhạy với offset

| Offset | carry mean | CAGR | Sharpe | MaxDD | Calmar | DD 5th | md5 |
|---|---|---|---|---|---|---|---|
| p25 −3,400pp | 3,139%/y | 25,89% | 2,08 | −14,1% | 1,84 | −23,27% | `832dee61…` |
| **median −2,525 (PIN)** | 3,501%/y | **25,71%** | **2,06** | **−14,0%** | **1,83** | **−23,56%** | `bcd0469f…` |
| p75 −2,300pp | 3,594%/y | 25,80% | 2,06 | −14,0% | 1,84 | −23,43% | `92fcf1c7…` |
| **Dải** | | **0,181pp** | 0,02 | 0,1pp | **0,01** | 0,29pp | |

⚠️ **Dải engine KHÔNG ĐƠN ĐIỆU**: chân p25 trả carry THẤP NHẤT lại cho CAGR CAO NHẤT ⇒ trật tự
trong dải là **nhiễu đường đi**, không phải hiệu ứng offset (dải overlay thì đơn điệu đúng chiều:
25,207 < 25,421 < 25,476). Cả dải nằm **dưới** sàn nhiễu W2b của chân đã park (**0,46pp**) và dưới
MDE một-chân (0,4pp) ⇒ kết luận CHẮC: số pin không nhạy với lựa chọn offset trong p25–p75.

### 7. Chân đối chứng KHÔNG CẦN BẮC CẦU (88 tháng SỐ THẬT, 0 dựng lại, 0 ff)
Cửa sổ **2019-03-01 → 2026-06-19** (7,30y). Bắt đầu 01/03 vì luật PIT khiến mọi phiên 02/2019 vẫn
đọc mốc 01/2019 (= số dựng lại).

| | carry 0% | dep1m | Δ |
|---|---|---|---|
| CAGR | 22,86% | **24,86%** | **+2,00pp** |
| Sharpe(252) | 1,70 | 1,83 | +0,13 |
| MaxDD | −17,5% | −16,0% | +1,5pp |
| Calmar | 1,31 | 1,56 | +0,25 |
| md5 | `2988c7a3c44de4daf55a71d960cc0c3a` | `13d8e1de79915d1f31737054b90b558a` | |

⇒ Hiệu ứng carry đo trên **DỮ LIỆU THẬT một mình = +2,00pp** vs +2,34pp trên toàn cửa sổ. Đoạn dựng
lại **không bịa ra hiệu ứng**; chênh 0,34pp là do 2014-2019 lãi suất cao hơn (recon 4,08–4,98%/năm
vs 2019+ thực tế mean 3,08%).

### 8. Δ +2,34pp là gì — TÁCH theo W2b, đừng đọc như "hệ tốt lên"

| Cửa sổ | Δ TỔNG (engine) | Δ SỐ HỌC (overlay) | Δ ĐƯỜNG ĐI | % số học |
|---|---|---|---|---|
| FULL (53/150 tháng dựng lại) | +2,337pp | **+2,052pp** | **+0,285pp** | 87,8% |
| Không bắc cầu (0 dựng lại) | +2,007pp | +1,989pp | **+0,018pp** | 99,1% |

Tiền nhàn rỗi chiếm trung bình **46,4% NAV** — đó là đòn mà carry tác động qua.
Phần **đường đi 0,285pp NẰM DƯỚI sàn nhiễu W2b (0,46pp)** và dưới MDE một-chân (0,4pp) ⇒ không phân
biệt được với nhiễu. Overlay tái dùng nguyên văn `w2b_overlay.py` (quant-skeptic CONFIRMED
2026-09-27 16:44Z).

🚩 **Cảnh báo kế thừa (bắt buộc mang theo khi trích mục này):** mọi so sánh **PHƯƠNG TIỆN** (park vs
không park, custom30V vs custom30 vs C6/C10) **VẪN** ở trạng thái W2b — *engine không có sức phân
giải*. Mục này **KHÔNG mở lại** câu hỏi đó. Muốn so phương tiện dưới quy ước `dep1m` thì phải chạy
**ensemble ~160–190 chân** như W2b đề xuất.

### 9. Giới hạn
1. **53/150 tháng là SỐ DỰNG LẠI**, không phải số công bố (§6 và §7 giới hạn tác động, không xoá nó).
2. **Upstream ĐÃ CHẾT** 28/09/2026 (FiinPro-X trial). Mốc sau 2026-09 phải lấy NHNN trực tiếp.
3. Đoạn 2011-01→2025-10 của `sbv_low` (xương sống của cầu) **chưa có nguồn thứ hai xác minh** — di
   sản registry W1, không phát sinh mới.
4. Đây là **lãi tiền gửi thị trường**, KHÔNG phải carry egg DNSE thật (8,543%/năm spot 09/2026 —
   cao hơn cả đầu mút cao NHNN ~1pp, là spread SẢN PHẨM, DNSE không cam kết). Số pin cố ý dùng đầu
   **THẬN TRỌNG**.
5. CAGR thật ≈ CAGR backtest − 1,5% (CLAUDE.md) ⇒ 25,71% → ~**24,2%**.

### 10. ⚠️ HỆ QUẢ PHẢI XỬ — `CLAUDE.md` đang nói NGƯỢC (cần user/Mike quyết, Taylor KHÔNG tự sửa)
`WorkingClaude/CLAUDE.md` § Backtest ghi quy ước chung: *"lãi tiền gửi nhàn rỗi **0%/năm**"*, và
`backtest_fundamental_rating.py` / `simulate_holistic_nav.py` **trích thẳng "per CLAUDE.md"**. Nếu
mục (septies) này thành số pin hiện hành thì registry và CLAUDE.md **mâu thuẫn**. Hai lựa chọn:
- **(A)** cập nhật CLAUDE.md § Backtest: tiền nhàn rỗi = `idle_rate_proxy.r_idle(tier="dep1m")`, và
  nói rõ số pin trước 2026-09-28 đo ở 0%/năm (KHÔNG so trực tiếp với số sau).
- **(B)** giữ CLAUDE.md ở 0% và đánh dấu (septies) là **số song song theo quy ước mới**, không thay
  headline R3 — khi đó phải sửa PATCH §0 bên dưới cho phù hợp.
**Chưa chọn thì đừng áp PATCH §0.**

---

## PATCH §0 — khối "## ⭐ CONFIG TỐT NHẤT = V2.4" (chỉ áp khi user chọn (A) ở §10)

Chèn NGAY TRÊN dòng `> ⭐⭐ **SỐ R3 HIỆN HÀNH (từ 2026-09-27 mục (sexies))...`:

```markdown
> ⭐⭐⭐ **SỐ R3 HIỆN HÀNH (từ 2026-09-28 mục (septies), quy ước tiền nhàn rỗi = lãi huy động 1
> tháng Big-4 `dep1m`) = CAGR 25,71% / Sharpe 2,06 / MaxDD −14,0% / Calmar 1,83** (Final NAV
> 864,86B, IS 22,47% / OOS 28,71%, ledger md5 `bcd0469f…`, bootstrap 5th CAGR 17,8% / DD **−23,6%**
> = NEO SIZING MỚI, DSR 1,0000, PBO 0,1258 họ N=14 / 0,5000 họ N=4 thoái hoá).
> **ĐỔI QUY ƯỚC ĐO, KHÔNG ĐỔI MÔ HÌNH** — park vẫn 0,30, rail không đụng; +2,34pp so (sexies) gồm
> **2,05pp SỐ HỌC** (tiền nhàn rỗi ~46% NAV được trả ~3,5%/năm thay vì 0%) + 0,285pp đường giao dịch
> (DƯỚI sàn nhiễu 0,46pp ⇒ nhiễu). **KHÔNG đọc là "hệ tốt lên", KHÔNG dùng để xếp hạng phương tiện
> park** (vẫn W2b: engine không phân giải). Mục: **"2026-09-28 (septies) — ⭐ RE-PIN R3 THEO QUY ƯỚC
> TIỀN NHÀN RỖI MỚI `dep1m`"** cuối file.
```

Và sửa dòng `> ⭐⭐ **SỐ R3 HIỆN HÀNH (từ 2026-09-27 mục (sexies))` thành
`> ⭐ **SỐ R3 theo quy ước CŨ (tiền nhàn rỗi 0%/năm) — mục (sexies) 2026-09-27**` (giữ toàn bộ nội
dung; đây là số ĐÚNG dưới quy ước cũ, không phải số sai, nên **không gạch ngang**).
