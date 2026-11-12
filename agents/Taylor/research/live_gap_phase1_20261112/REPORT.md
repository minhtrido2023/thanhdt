# GĐ1 — Waterfall gap backtest-vs-live 01/07→11/11/2026 (job `Taylor_20261112_104204`)

> Nhánh nghiên cứu `research/live-gap-p1-20261112` (worktree `WorkingClaude/wt-livegap-p1-1112`, commit `5512bfe3d`).
> **KHÔNG merge, KHÔNG đổi production/cron/data canonical.** Mọi ledger tên `_exp_gap_*`, nằm ở `ledgers/` (đã chuyển khỏi `data/`).
> Trials: 15 lần chạy engine (6 tiền đề + 7 bậc + 2 warm-start). Không chọn cấu hình nào theo kết quả ⇒ không có DSR/PBO để tính.

## 0. Kết luận (chỉ phần đã đo)

1. **W0 KHÔNG được nhận diện tới ±3pp — phụ thuộc quy ước khởi động engine:**
   - *cold-start* (AUDIT_START=07-01, 100% tiền, lệnh đầu tiên **21/07**): **−0,50% @50B**, +0,02% @1B.
   - *warm-start* (chạy 2014→11-12, đọc NAV 30/06→11/11): **+2,96% @50B-gốc-2014** (NAV ~575B lúc vào cửa sổ),
     −1,32% @1B-gốc-2014 (NAV ~13B lúc vào cửa sổ).
   ⇒ Engine pin trên cửa sổ này ở khoảng **−1,3% … +3,0%**, tức quanh/dưới tiết kiệm (+2,70%). Kỳ vọng "23%/năm" không áp
   được cho 4 tháng này — đó là phần **thị trường/kỳ vọng** (W0) và nó thật, nhưng độ lớn của nó chỉ biết trong dải đó.
2. **Live thua engine 2,6–6,8pp** (SpaceX −3,86% vs dải −1,3..+3,0; ZaloPay bot −2,61%). Phần này **không nằm ở W1–W2a**
   (W1 +0,52pp cold; W2a `LIQ_ZERO_BLOCK=lag` 0,00pp, byte-identical) mà ở các bậc **chưa đo** W2b–W5 (§3).
   Theo tháng (live SpaceX − engine W1 cold): **T7 −4,96pp** · T8 −3,26pp · T9 +3,00pp · T10 +2,01pp — dồn vào T7–T8.
   T7: engine cold ngồi tiền tới 21/07, engine warm @50B chỉ −0,10% (phơi nhiễm TB cửa sổ 45%), live −6,16%.
3. Cổng dừng theo plan: **không gọi được một nhánh duy nhất.** Gap live-vs-hurdle (−6,4pp SpaceX) ≈ một phần W0
   (0..−4pp tuỳ quy ước) + phần dư live-vs-engine (2,6–6,8pp) chưa phân rã. Bằng chứng đã đo KHÔNG ủng hộ "hệ live trôi khỏi
   hệ pin ở các luật engine biểu diễn được" (W1–W2a nhỏ). Phần dư lớn nhất rơi vào T7 (go-live) — cần W3/W4/W5 để nói là
   người/thực thi/exposure; chưa đo thì không kết luận.

**N**: MỘT cửa sổ 4 tháng, MỘT đường đi. Engine cold @1B có 8 lệnh mua BAL + 7 LAG; BAL live = 1 deal. Đây là MỘT mẫu,
không phải bằng chứng thống kê về edge.

## 1. Waterfall (`waterfall.csv`, `waterfall.png`)

| TK | Bậc (đổi đúng 1 trục) | Lợi suất kỳ | Δ bậc trước | ledger md5 |
|---|---|---|---|---|
| SpaceX 01/07→11/11 | W0 pin park0, NAV 50B | −0,499% | — | `7895ddef71bdcb80967cfeeefbf99f0c` |
| | W1 NAV_TOTAL_B=1 | +0,016% | +0,515pp | `82f73258972fc77b7cd54a4cb2677770` |
| | W2a + LIQ_ZERO_BLOCK=lag | +0,016% | 0,000pp | `82f73258…` (byte-identical W1) |
| | W2b sàn ADV 2 tỷ / mã cờ / LAG DD-zone / excluded_tickers | **chưa đo** | | |
| | W3 lệnh tay · W4 fill thật · W5 egg | **chưa đo** | | |
| | *(W0-warm @50B gốc 2014, cửa sổ 30/06→11/11)* | *+2,961%* | *(quy ước khởi động, không phải 1 bậc)* | `a63b200089dae9e0c29eb4cc684dcade` |
| | *(W1-warm @1B gốc 2014)* | *−1,318%* | | `b2841d8c94b855ab3ff54dd59b1cf4cd` |
| | **LIVE** (unit ledger) | **−3,862%** | −3,878pp (dư chưa phân rã) | `nav_period_returns.py` |
| ZaloPay 06/07→11/11 | W0 | −0,499% | — | `78412d150e7a811e7fa6ef0d47b87e41` |
| | W1 | +0,016% | +0,515pp | `3554bdf9bcccb079251e48fa1f130c9b` |
| | W2a | +0,016% | 0,000pp | `3554bdf9…` |
| | **LIVE bot sleeve** (tách DGC) | **−2,609%** | −2,625pp | GĐ0 `vs_savings_table.csv` |
| | LIVE cả tài khoản | −7,511% | | |

Tham chiếu: tiết kiệm 7,4%/năm +2,70% (SpaceX) / +2,60% (ZaloPay); VN-Index −6,08% / −5,24%.
ZaloPay W0–W2a = engine bắt đầu 06/07; số trùng SpaceX vì lệnh đầu tiên của engine cold rơi vào 21/07 ở cả hai (đã kiểm TX đầu tiên).

Theo tháng (NAV cuối tháng, %): engine W1 T7 −1,20 · T8 +8,29 · T9 −3,41 · T10 −3,90 | live SpaceX T7 −6,16 · T8 +5,03 · T9 −0,41 · T10 −1,89.
Tỷ trọng cổ phiếu TB engine W1: 66% NAV (park 0 ⇒ không có custom30V); live: ~79% NAV ở Trứng vàng (số GĐ0/plan, không đo lại ở đây).
Live phơi nhiễm thấp hơn engine mà vẫn lỗ hơn ⇒ phần dư KHÔNG giải thích được bằng cash drag thuần — cần W3/W4 để tách.

## 2. Tiền đề kỹ thuật

**(d) Control — KHÔNG tái hiện 4707bcbe.** Đúng lệnh pin sexies (park 0,3, carry off, 0729_postrestate, AUDIT_END 06-19, NAV 50B,
threads=1) → **CAGR 24,31% / Final 752,73B / md5 `d7091b4b…`** thay vì 23,37% / 684,52B / `4707bcbe`. Cùng ra `d7091b4b` trên
3 bộ code: main hiện tại, nhánh có vá (a), và **code đúng lúc pin `f66dab18`** ⇒ lệch là **DATA, không phải code**: các file
`data/` không thuộc BQ cache được làm mới hằng ngày (`earnings_surprise_data.pkl`, `earnings_events_classified.csv`,
`lag_edge_health.csv` — mtime 2026-11-12) không được snapshot cùng pin. Hệ quả: **số pin R3 hiện không tái lập được từ `data/`
canonical**; W0 không neo được vào pin bằng chân control (khai chênh, theo §8c). Chưa xác định file nào gây lệch (chưa đo).

**(a) Vá sort ổn định — INERT, và KHÔNG chữa được bất tất định.** Đổi 2 `sort_values` trong `regime_size_overlay.py`
(dòng 43, 93) sang `kind="mergesort"`: ledger byte-identical với bản chưa vá ở cả AUDIT_END 06-19 (`d7091b4b`) và 07-29
(`4e3fc1f5`) ⇒ **số pin cũ không đổi**. Nhưng so 06-19 vs 07-29 trên 3.107 phiên chung: **1.986 phiên lệch NAV, 89/149 tháng
lệch lợi suất, 0 tháng đổi dấu, lệch tối đa 16,5B, lệch đầu tiên 2018-07-06** — giống hệt có/không vá. Truy nguồn: mọi TX
trước 2018-07-06 trùng khớp; lệch đầu tiên là **size lệnh CAPIT `CAPITB_E5` mua GAS (72.813 vs 75.012 cp)** — size CAPIT =
`size × cash_pct` của base-run BAL (`pt_v23_audit_2014.py` `add_capit_arm`, ~dòng 1449–1478) ⇒ base-run BAL đã phụ thuộc
AUDIT_END. Thêm một dấu hiệu: ngày gốc chỉ số `CUSTOM_VN30EXVIC_PITG` đổi theo AUDIT_END (2025-03-11 vs 03-21). Nguyên nhân
gốc **chưa xác định**; giả thuyết "quicksort trong regime_size_overlay" bị bác bởi chính phép thử. Trên cửa sổ GĐ1:
AUDIT_END 11-11 vs 11-12 → NAV hằng ngày trùng tới VND (93/93 phiên) ⇒ waterfall không bị ảnh hưởng.

**(b) LAG cache adjusted — INERT cho engine này trên cửa sổ này.** Sandbox `adj` (4 file LAG của nhánh
`feat/lag-cache-adjusted-20261110` v2, pkl end 2026-11-09) vs `ctrl` (data canonical, chép đông cứng): ledger W0
**byte-identical** (`7895ddef`). `pt_v23_audit_2014.py` lấy giá LAG từ BQ cache, không từ `earnings_px.pkl` ⇒ lỗi trộn cơ sở
giá chỉ chạm các engine paper (pt_v4/v12/v22), không chạm W0–W2a. Không phải merge gì.

**(c) Vintage**: không có `tav2_pin` nào phủ tới 11/11 (pin mới nhất `_pin_202611` chụp 01/11). Dùng bản chép đông cứng
`data/bq_cache` (verified 2026-11-11T16:59Z, VNINDEX 11-11 khớp BQ) → `bq_cache_asof20261111/` (manifest md5 `4370ecca…`).
Dữ liệu tới 11/11; AUDIT_END=11-12 không thêm phiên. universe_pit (không ticker_prune).

## 3. Vì sao W2b–W5 "chưa đo"
- **W2b**: engine không có knob cho sàn ADV 2 tỷ, LAG DD-zone gate, excluded_tickers (đã liệt kê toàn bộ env knob của
  `pt_v23_audit_2014.py`). `LAG_FORENSIC_GATE` mặc định đã ON; CAPIT lever đã tắt sẵn trong cấu hình pin ⇒ "CAPIT off" inert.
  Đo cần code mới trong engine (mỗi luật 1 knob, 1 bậc).
- **W3/W4/W5**: cần bộ replay theo lệnh thật (journal + `dnse_raw_*` + chuỗi egg), không phải knob engine. Không dựng trong job này.
- Đề xuất cho vòng sau: (i) truy file data gây lệch control + snapshot các file LAG phái sinh cùng mỗi pin;
  (ii) 3 knob W2b; (iii) replay W3–W5 bắt đầu từ tháng 7 (nơi dồn phần dư).

## 4. Tái lập
```bash
R=mike/agents/Taylor/research/live_gap_phase1_20261112; CODE=WorkingClaude/wt-livegap-p1-1112/WorkingClaude  # @5512bfe3d
$R/make_sandbox.sh adj; $R/make_sandbox.sh ctrl
B="BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 AUDIT_END=2026-11-12 BQ_LOCAL_CACHE=$PWD/$R/bq_cache_asof20261111"
$R/run_leg.sh exp_gap_W0_adj  $CODE $R/sandbox_adj $B AUDIT_START=2026-07-01                 # W0
$R/run_leg.sh exp_gap_W1_adj  $CODE $R/sandbox_adj $B AUDIT_START=2026-07-01 NAV_TOTAL_B=1   # W1
$R/run_leg.sh exp_gap_W2a_adj $CODE $R/sandbox_adj $B AUDIT_START=2026-07-01 NAV_TOTAL_B=1 LIQ_ZERO_BLOCK=lag
# ZaloPay: như trên với AUDIT_START=2026-07-06 (tag Z*). Control: run_leg.sh exp_gap_C0main WorkingClaude WorkingClaude \
#   BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=off   (mặc định run_leg = 0729_postrestate, 06-19, 50B)
$DNA_PYEXE $R/leg_summary.py $R/legs.json $R/ledgers/*W*_adj*.csv $R/ledgers/*Z*_adj*.csv; $DNA_PYEXE $R/waterfall.py
$R/run_leg.sh exp_gap_W0warm_adj $CODE $R/sandbox_adj $B   # warm (không AUDIT_START); thêm NAV_TOTAL_B=1 cho W1warm
$DNA_PYEXE $R/determinism_check.py <ledger AUDIT_END A> <ledger AUDIT_END B>
```
Self-check 0 VND (BAL+LAG, tiền + NAV identity) ở cả 15 chân (`grep selfcheck logs/*.log`).
