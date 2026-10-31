# oshares_live R12: vá 4 điều kiện arch-review R11 (job Taylor_20261031_092209, 31/10/2026)

Nhánh (CHƯA merge, knob `OSHARES_SOURCE_DEFAULT` giữ `"live"` như main, không đặt lệnh):
- WC `session/oshares-r12-20261031` (worktree `/home/trido/wt-oshares-r12-20261031`) trên R11 `3ad1406ef`; main WC
  vẫn là `8fcfa8b95` = gốc của R11 ⇒ không cần rebase. `dcf_valuation.py` +15/−5, `trading_bot/strategies.py` +30/−1,
  `oshares_dcf_selfcheck.py` +162/−4.
- mike `session/oshares-r12-ops-20261031` (worktree `/home/trido/wt-oshares-r12-ops-20261031`) trên R11 `167036792`
  + merge master `6d9e6cffd` (merge `0b0a0ad15`, không xung đột). `bin/send_plan_report.sh` +39/−14,
  `kb/projects/oshares-live-dcf-20261030.md` +16, `SELFCHECK_R11.md` +3 (đính chính), thư mục này.
(`git diff --numstat` trước commit.) Commit WC `e052526b9`. Interpreter `/home/trido/thanhdt/wc_venv/bin/python`; module nạp từ WT (`run_wt.py`,
dòng `[run_wt] modules ngoài WT: KHÔNG` trong mọi log).

## Kết quả từng việc
| Việc | Nội dung | Kết quả |
|---|---|---|
| 1 | `format_dcf_check` nối ` · số CP quý: [STATUS ]MoS ±x% [không ]robust (cơ sở plan echo)` khi status khác / robust khác / \|ΔMoS\| ≥ 2pp (`OSHARES_FIN_LABEL_MOS`). Quyết theo MoS, KHÔNG theo `oshares_divergence`. Dict live thêm `status_fin`/`robust_fin` (từ `sensitivity_fin` = hộp nhạy cảm trên số quý, cùng `classify_dcf`). | **PASS** — C22 (9 check) + M53/M54 KILLED |
| 2 | `send_plan_report.sh`: plan echo khai `price_date=PRICE_SESSION_UNKNOWN` có chủ đích, gỡ `price_sessions_for`/`prime` ⇒ 0 BQ; mỗi lời gọi DCF trần cứng SIGALRM `SEND_PLAN_DCF_CALL_S`=30s, tổng `SEND_PLAN_DCF_BUDGET_S`=120s; quá ⇒ bỏ dòng DCF + 1 WARN, báo cáo vẫn gửi. Đính chính `SELFCHECK_R11.md` (sau dòng 78) + KB mục 18 (+ mục 19-22 mới). | **PASS** — C23 (6 check, exec CHÍNH khối code của script) + M56/M57 KILLED; replay 279 lệnh: **0 lời gọi BQ** |
| 3 | `price_session_for`: `except Exception: pass` tách đôi — giá hỏng/không khớp ⇒ UNKNOWN IM; lỗi ĐỌC cache/duckdb ⇒ UNKNOWN + `_shout_once` stderr kèm lỗi thật + đường dẫn (§29). | **PASS** — C21 thêm 3 check (`dv.WORKDIR="/nonexistent_r12_c21"` ⇒ stderr `LOI DOC cache … /nonexistent_r12_c21`; không khớp ⇒ 0 byte stderr) + M55 KILLED |
| 4 | Merge mike master vào nhánh R12 (sạch); chạy lại C21 + `eod_report_v2_failopen_selfcheck.sh` + `eod_delivery_wiring_selfcheck.py`; cập nhật impact EOD. | **PASS** — failopen 12/12, wiring 9/9, ở TZ=UTC và env -u TZ |

Vì sao trần thời gian nằm TRONG Python chứ không `timeout 120` bọc heredoc: heredoc là toàn bộ báo cáo duyệt plan
(~1.240 dòng) — `timeout` giết nó là mất cả báo cáo 21:00 vì một dòng DCF. SIGALRM chỉ bỏ dòng DCF của lệnh treo.
Sau việc 2 khối DCF plan echo chỉ đọc parquet local; trần là lưới an toàn, không phải đường thường.

## Đo
**Plan echo 0 BQ** (`measure_impact_r12.py`, exec khối DCF thật của `send_plan_report.sh` WT, KHÔNG prime trước;
chặn + đếm `oshares_dcf.{oshares_for,fetch_cache,pricing_events,prime}`, `oshares_live._fetch`,
`dcf_valuation.price_session(s)_for`, `google.cloud.bigquery.Client.query`): 279 lệnh MUA (plan_date ≥ 2026-09-01)
⇒ **0 lời gọi**, 0 timeout, 0 dòng `!!!!!` stderr (`impact_stderr.txt`, `impact_r12_summary.json`).

**Impact vs R11 / main** (`impact_r12_summary.json`, `out_impact_r12_plans.csv`):
| | R12 vs main | R12 vs R11 |
|---|---|---|
| plan echo | dict 279/279 trùng, dòng 279/279 trùng | 4 dòng đổi (FPT 2026-10-09/20/22/23: R11 live → R12 số quý, vd MoS +15.4% → +23.1%) |
| EOD (khớp phiên như R11, format R12) | — | 26 dòng đổi, **cả 26 chỉ do nối nhãn** (phần trước nhãn trùng R11); đều FPT paper main; SpaceX/ZaloPay 0 |
Nhãn EOD mang đúng MoS mà plan echo đã in: 26/26. Plan echo ≠ EOD: 26 cặp (R11 đo 22 vì R11 cho 4 lệnh FPT plan echo đi live).

**Ca kiểm tay** (`probe_label.py` → `probe_label.txt`, dữ liệu thật, knob live):
- FPT 2026-09-23 @66.600: `MoS +5.6%, không robust) · số CP quý: MoS +14.2% robust (cơ sở plan echo)` — lệch số CP
  9,998% (dưới ngưỡng cảnh báo 10%, không có dòng ⚠ OShares) mà vẫn hiện nhãn.
- PHR 2026-09-15 @31.100: `RICH … MoS -19.4%, robust) · số CP quý: CHEAP MoS +33.7% robust (cơ sở plan echo)`.
- AIG 2026-08-06 @47.000: `RICH … MoS -1.4%, không robust) · số CP quý: CHEAP MoS +11.9% không robust (cơ sở plan echo)`.
- HT1/VNM 2026-10-29 (live = số quý): không nhãn.

**fin byte-identical** (`byte_identical_r12.py`, env `DCF_OSHARES_SOURCE=fin`, main `8fcfa8b95` TZ=UTC vs nhánh
TZ=Asia/Ho_Chi_Minh, toàn universe_pit, asof 2026-10-29 (336 mã) + 2025-10-29 (438 mã)): **3.870/3.870** repr trùng,
`diff_repr 0` (`run_byte_identical_stdout.txt`) — 5 loại × 774: `dcf_check(price=Close)`, `_dcf_check_for_order` (+khớp
phiên), `dcf_check` tự đọc giá, **mới:** `_dcf_check_for_order(price_date=UNKNOWN)` (đường plan echo) và
`format_dcf_check` của nó.

## EOD sau report v2 (việc 4)
Từ master `6d9e6cffd`, `eod_trading_report.sh::_deliver_eod`: report v2 (`bin/report_v2/build.py`, không có DCF —
`grep -n dcf bin/report_v2/*.py` rỗng) rc=0 ⇒ **SpaceX EOD chỉ gửi bản v2 ⇒ KHÔNG mang dòng DCF/nhãn**; ZaloPay = v2 +
nguyên bản text cũ nối dưới (CÓ dòng DCF/nhãn); v2 lỗi (rc≠0, ≠5) ⇒ fallback bản text cũ cho cả hai (CÓ). rc=5 giữ
bản đã giao. Paper DC-book (`dc_book_waterfall_paper.py`) mang dòng DCF/nhãn. Đo 279 lệnh: nhãn chỉ xuất hiện ở paper
main (26), SpaceX/ZaloPay 0 ⇒ hiện tại không lệnh tài khoản thật nào nhận nhãn.

## Selfcheck
`oshares_dcf_selfcheck.py` (WT, `run_selfcheck.sh`, 3 TZ TUẦN TỰ):
| Chạy | Kết quả | Log |
|---|---|---|
| TZ=UTC | 0 FAIL, **55/55** mutant KILLED, rc=0 | `run_selfcheck_UTC.txt` |
| env -u TZ | 0 FAIL, 55/55 mutant KILLED, rc=0 | `run_selfcheck_noTZ.txt` |
| TZ=Asia/Ho_Chi_Minh | 0 FAIL, 55/55 mutant KILLED, rc=0 | `run_selfcheck_ICT.txt` |
Mới: C21 +3 (việc 3), C21 plan echo đổi thành "KHÔNG gọi price_session(s)_for", C22 9 check (việc 1), C23 6 check
(việc 2). Mutant mới M53 không nhãn · M54 nhãn theo ngưỡng divergence · M55 lỗi đọc im · M56 plan echo tự khớp phiên
lại · M57 bỏ trần thời gian — 5/5 KILLED.
Ghi chú vận hành: lượt đầu chạy 3 TZ SONG SONG bị treo ở 3 tiến trình `bq query` (C22 dữ liệu thật gọi oshares_live
⇒ BQ) — đã memo hoá C22 một lần/tiến trình và chạy tuần tự; `bq query 'SELECT 1'` riêng lẻ 2,8s.

Khác: `dcf_check_selfcheck` / `dcf_rate_frame_selfcheck` / `due_diligence_selfcheck` (WT, env -u TZ) rc=0;
`lag_dd_gate_selfcheck.py` (WC_ROOT=WT) TỔNG PASS + 52/52 mutant ở UTC và env -u TZ; `ops_health_check_selfcheck.py`
PASS. Rộng (`run_dcf_selfchecks.sh`, `sc_*`): dcf_refresh_gate / dcf_earning_power / tz_asof_ict_dd_dcf /
basket_* PASS; dcf_selector FAIL có sẵn PROD (`39/40`), test_multi_strategy FAIL có sẵn PROD (SQL `VNINDEX_RSI_Max3M`),
test_trading_bot (`gap_adaptive_enabled`) + custom_basket_forensic (`worktree LẠI có forensic_flags.csv`) = môi trường
worktree — cùng chữ ký R11 (so log R11).
**Không chạy end-to-end** `send_plan_report.sh`/`eod_trading_report.sh` (`signal_holds.py --enforce` sửa plan thật);
bằng chứng chức năng: C23 + replay exec chính khối code DCF của script.

## Còn lại
- Plan echo = số quý cho đến vòng riêng thêm `ref_price_session` có cấu trúc vào lệnh plan (§24) — KHÔNG làm ở R12.
- Ngưỡng nhãn 2pp chọn tay theo dispatch ("~2pp").
- Thứ tự merge: mike trước (C21/C23 đọc chuỗi trong script mike), WC sau. Đường tiền gián tiếp ⇒ arch-review (opus high)
  + quant-skeptic trước merge; KHÔNG tự merge.
