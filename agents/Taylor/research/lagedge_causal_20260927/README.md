# FAIL-C — cổng `w_LAG` đọc chuỗi edge-health look-ahead 25 phiên: SỬA + A/B R3

job `Taylor_20260927_045243` · 2026-09-27 · Taylor · **PAPER-ONLY, worktree, CHƯA MERGE**
Nguồn: `research/measurement_integrity_audit_20260927/REPORT.md` §2 FAIL-C.

## Kết luận một dòng
Look-ahead là **THẬT và cơ học** (nhãn sớm đúng 25 phiên, 5.488/5.488 dòng), nhưng **tác động lên
R3 gần bằng không và đi theo hướng NGƯỢC với "peek có lợi"**: bản CAUSAL cho CAGR **24,44%** so với
control **24,38%** — tức con số pin hiện tại **không hề được thổi lên** bởi lỗi này. Không có
re-pin nào bị hạ. LIVE **không đổi một byte hành vi**.

## Lỗi (nhắc lại gọn)
`edge_health_monitor.py:163-167` — `ret` là return FORWARD 25 phiên tính từ `entry`, nhưng dòng
được dán nhãn theo chính `entry`. Consumer (`pt_v23_audit_2014.py:2057`, `pt_v22_dt5g.py:777`) đọc
`parse_dates=["entry"]` rồi `.reindex(daily, method="ffill")` ⇒ **backtest** đọc mỗi giá trị
`mean12` sớm 25 phiên. **Live bảo thủ** vì dòng chỉ xuất hiện khi sự kiện đã hoàn tất.

## Bản sửa (2 file, worktree)
| Repo / branch | File | Thay đổi |
|---|---|---|
| WorkingClaude `fix/lag-edge-health-causal-label` | `edge_health_monitor.py` | thêm cột `known_date = idx[pos+25]`; **giữ nguyên `entry`**; `LAG_EDGE_OUT` để ghi ra tên KHÔNG canonical; `asof` trả `known_date` |
| WorkingClaude (cùng branch) | `pt_v23_audit_2014.py` | index lên `known_date` khi có, fallback `entry`; `EDGE_HEALTH_CSV` để A/B; in `source=/label_col=/rows=` |
| mike `fix/lag-edge-health-causal-label` | `bin/asof_label_selfcheck.py` | **MỚI** — cổng bất biến nhãn-as-of |

**`known_date` là ảnh ĐƠN ĐIỆU NGẶT của `entry`** (`pos → pos+25`), nên cửa sổ trailing-12M cũ đã
chỉ chứa sự kiện có `known_date ≤ known_date[i]`. **Bản sửa đổi NHÃN, không đổi thành phần cửa
sổ** — đây là phép DỊCH THỜI GIAN thuần, đúng như audit đã mô tả.
Bằng chứng: CSV causal có `entry/ret/mean12/win12/n12` **IDENTICAL** canonical (pandas `.equals`),
chỉ thêm 1 cột. `data/lag_edge_health.csv` **KHÔNG bị ghi đè**; bản mới ở
`data/lag_edge_health_exp_causal.csv`.

## A/B R3 — lệnh pin nguyên văn
`run_leg.sh` (copy verbatim từ `research/c30v_retleg_repin_20260927/run_leg.sh`): snapshot
`bq_cache_asof20260729_postrestate`, `BQ_CACHE_THREADS=1`, `$DNA_PYEXE`, `universe_pit`,
`NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.7
AUDIT_END=2026-06-19`.

| Leg | nguồn edge-health | cột nhãn | CAGR | Sharpe | MaxDD | Calmar | Final NAV | IS 14-19 | OOS 20+ | self-check | CSV md5 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `lagedgectl` control | `lag_edge_health.csv` | `entry` | **24,38%** | 1,69 | −18,8% | 1,30 | **757,61B** | 19,26% | 29,24% | 0 VND BAL+LAG | **`3f836927c0df82915c4cfb973d8f4af3`** |
| `lagedgecausal` | `..._exp_causal.csv` | `known_date` | **24,44%** | 1,70 | −18,7% | 1,31 | **762,43B** | 19,38% | 29,25% | 0 VND BAL+LAG | `457ba1da3b5b6aae6c1ba5da6a09a227` |
| **Δ (causal − control)** | | | **+0,06pp** | +0,01 | **+0,1pp tốt hơn** | +0,01 | +4,82B (+0,64%) | +0,12pp | +0,01pp | | |

**Control tái lập TUYỆT ĐỐI**: `diff` với artifact pin `..._exp_c30vnew_univpit.csv` = **0 dòng**,
md5 khớp `3f836927`. Điều này đồng thời chứng minh bản vá engine **TRƠ** khi `EDGE_HEALTH_CSV`
không được đặt (đường production mặc định).
IS/OOS **tính lại độc lập** từ chính CSV bằng `extract_peryear.py` (không đọc số engine tự in).

## Vì sao Δ ~ 0 (giải thích, không phải biện hộ)
Trên đúng cửa sổ engine (2014-01-02→2026-06-19, 3.109 phiên): cổng đổi **293 ngày (9,4%)** —
**134** ngày peek CÓ LỢI (control bật 0,65 trong khi causal 0,50) vs **159** ngày peek BẤT LỢI.
Tổng thời gian bật 0,65: control 1.471 phiên / causal 1.496 phiên. Lệch nghiêng nhẹ về phía
**BẤT LỢI cho control**, khớp dấu Δ dương của causal. Đây là DỊCH THỜI GIAN, không phải nhìn trộm
có hướng — khác hẳn ca custom30V (đơn hướng, −4,48pp).

## LIVE: KHÔNG đổi hành vi
1. **Đo thật hôm nay (2026-09-27), 2 bản:** legacy nhãn cuối `2026-08-14`, causal nhãn cuối
   `2026-09-23`, **cùng `mean12 = −0,6048`** ⇒ **cùng `w_LAG = 0,50`**.
2. **Lý do cấu trúc, không phải trùng hợp:** generator chỉ ghi dòng khi `pos+25 < len(idx)`, tức
   `known_date` đã tồn tại trong lịch. Nên dòng mới nhất luôn có `known_date ≤ hôm nay`, và cả hai
   cách index đều `ffill` vào **cùng một dòng cuối**. Live đúng theo cấu trúc, mọi ngày.
3. **Không có code đường tiền nào đọc giá trị này.** `grep -rn lag_edge_health mike/bin
   mike/trading_bot` → 3 hit, tất cả KHÔNG đọc giá trị: `bq_freshness_check.sh:392` chỉ dò *mtime*;
   `compute_active_nav.py:594` và `discretionary_accumulation_inject.py:392` chỉ **nhắc tên trong
   comment** (sự cố 07-12). Consumer thật đều là backtest/research:
   `pt_v23_audit_2014.py`, `pt_v22_dt5g.py`, `pt_v23_lagqual_research.py`, `pt_v23_lagcap_research.py`,
   `pt_v23_audit_ddpark.py`, `lag_dnpr_harness.py`, `converge_fullharness_test.py`,
   `c1_shadow_paper.py`, `edge_wlag_gate_selfcheck.py`.
   **Cột `entry` được GIỮ** nên mọi consumer chưa sửa vẫn chạy y như cũ (chỉ tiếp tục mang lỗi
   nhãn — cần sửa lần lượt, không phải trong job này).

## Selfcheck `mike/bin/asof_label_selfcheck.py`
Bất biến: *nhãn ngày của một dòng phải ≥ ngày cuối cùng của dữ liệu đã sinh ra giá trị dòng đó*.
Lịch phiên dựng từ CHÍNH nguồn giá sinh ra chuỗi (`data/earnings_px.pkl`), không dùng
`np.busday_count` (coding_guidelines §16 RULE 2).

- 7/7 unit test synthetic PASS (gồm: sớm đúng 1 phiên vẫn bị bắt; horizon=0 hợp lệ; dòng có cửa sổ
  chưa đóng bị loại tường minh chứ không âm thầm pass; fallback cột nhãn).
- **FIRE đúng file cũ**: `lag_edge_health.csv` → `vi_pham=5488/5488`, `som_toi_da=25 phien`, rc=1.
- **SẠCH bản causal**: `lag_edge_health_exp_causal.csv` → `vi_pham=0`, rc=0.
- Chạy lại dưới `TZ=Asia/Ho_Chi_Minh / America/New_York / UTC / env -u TZ` → **kết quả giống hệt**
  (§19 verify-before-done). Unit-only cũng chạy được dưới `python3` 3.10.

## Đề xuất (CHỜ USER SIGN-OFF — chưa merge)
1. Merge bản vá; **không cần re-pin R3** (Δ +0,06pp nằm trong nhiễu và đi theo hướng có lợi) —
   hoặc re-pin sang 24,44% nếu user muốn con số pin đúng hệ nhân quả. **Khuyến nghị: re-pin sang
   24,44%**, vì mục đích của pin là "số đúng", không phải "số cao".
2. Gắn `asof_label_selfcheck.py` vào `run_selfchecks.sh` — nó sẽ RED cho tới khi CSV canonical được
   sinh lại bằng generator đã vá (chạy `edge_health_monitor.py` trong `papertrade_daily.sh` step [22]).
3. Các consumer research còn lại vẫn index lên `entry` — sửa lần lượt, KHÔNG gộp vào job này.

## File
`run_leg.sh` · `lagedgectl.log` · `lagedgecausal.log` · `selfcheck_asof_label_*.log`
Artifact: `data/lag_edge_health_exp_causal.csv` ·
`data/v23_golive_..._exp_{lagedgectl,lagedgecausal}_univpit.csv`
