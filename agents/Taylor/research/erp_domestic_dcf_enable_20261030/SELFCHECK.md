# SELFCHECK — bật DCF_RATE_FRAME=domestic_v2 an toàn (job Taylor_20261030_050926)

User duyệt bật domestic_v2 lúc 30/10 12:08. Job này làm đủ 5 điều kiện quant-skeptic đặt ra trước khi bật
(`mike/logs/verify_20261030_044415_2663162.log`). **Chưa merge.** Mike chạy arch-review và quant-skeptic rồi mới merge.

## Nhánh / file đổi (`git diff --numstat`)

**Repo ngoài**: nhánh `session/erp-domestic-dcf-20261030`, worktree `/home/trido/thanhdt/wt-erp-domestic-dcf-20261030`, base f3f756256.

| File | +/− | Nội dung |
|---|---|---|
| `WorkingClaude/dcf_valuation.py` | +68/−12 | Thêm `RATE_FRAME_DEFAULT = "domestic_v2"` làm nguồn sự thật duy nhất. Gõ sai thì fallback về legacy và kêu. Ép cap_rf. Thêm `ke_range_note()` |
| `WorkingClaude/dcf_earning_power.py` | +5/−2 | cap_rf ủy quyền cho `D.terminal_growth_mode` |
| `WorkingClaude/cctg_deposit_wiring_selfcheck.py` | +13/−0 | Pin legacy cho mục 5/7, thêm assert v2 |
| `WorkingClaude/cctg_tier2_series_selfcheck.py` | +10/−2 | Pin legacy cho dòng `dcf.discount_rate` |
| `WorkingClaude/dcf_rate_frame_selfcheck.py` | +271/−33 | 30 check: 5 điều kiện cộng 6 mutation |

**Repo mike**: nhánh `session/erp-domestic-dcf-ops-20261030`, worktree `/home/trido/thanhdt/WorkingClaude/wt-erp-domestic-dcf-ops-20261030`, base 584aa20e0.

| File | +/− | Nội dung |
|---|---|---|
| `bin/ops_health_check.sh` | +64/−0 | Mục 16, khối `CHECKDCFRF` (chạy 1 lần/lượt, pure Python) |

**Rollback**: đổi đúng một từ ở `dcf_valuation.py`: `RATE_FRAME_DEFAULT = "domestic_v2"` thành `"legacy"`. Bản legacy trùng byte với main (md5 `4c0cf6e6ee6b267937c793c7dfda9a44`, 336 mã, 145 tính được). Selfcheck (a) kiểm điều này.

## 5 điều kiện — nguyên nhân, cách vá, check + mutation

1. **Ép cap_rf khi domestic_v2.**
   - Kẽ hở: với `DCF_TERMINAL_MODE=cpi_gdp_full`, r vẫn 12,25 nhưng g_T lên 9,66, tức chỉ r bị đổi riêng.
   - Vá, tầng env: lúc import, `DEFAULT_TERM_MODE` bị ép về `cap_rf` và in cảnh báo. Không raise, vì raise ở đây sẽ thành ValueError cho từng mã, rồi bị nuốt thành NOT_COMPUTED.
   - Vá, tầng gọi: `terminal_growth_mode(mode≠cap_rf)` tường minh dưới v2 thì raise. Production không truyền `term_mode`, đã grep.
   - Check [1a] [1b] [1c]: legacy vẫn tôn trọng env.
   - Mutation: [M1] gỡ ép thì [1a] đỏ. Mutant này crash (rc 1) đúng kiểu lỗi NOT_COMPUTED-tràn, nên lớp ép env là bắt buộc. [M1b] gỡ raise thì [1b] đỏ.
2. **Knob gõ sai.**
   - Trước đây: ValueError lúc import, bị nuốt thành NOT_COMPUTED, nên cờ DINH_GIA_NA tràn sang LAG.
   - Vá: `_resolve_rate_frame()` fallback về `legacy` (mô hình trước knob) và kêu bằng `!!!!! [dcf_valuation] … KHONG HOP LE` trên stderr và `logging.warning`.
   - ops_health mục 16 WARN khi: env của cron mang `DCF_RATE_FRAME`; giá trị `RATE_FRAME_DEFAULT` sai; hoặc crontab / `wc_env.sh` / `mike/bin/*.sh` tự gán `DCF_RATE_FRAME` hay `DCF_TERMINAL_MODE`.
   - Check [2a]: gõ sai thì rc 0, trùng byte legacy, có tiếng kêu. [2b]: biến rỗng thì dùng mặc định. [2c–2i]: trích khối `CHECKDCFRF` thật, chạy trên cây giả. Ca sạch cho OK; 5 ca hỏng mỗi ca đúng 1 WARN; dòng comment trong crontab bị bỏ qua.
   - Mutation [M2]: trả lại raise thì [2a] đỏ.
   - Thêm đường consumer thật: `trading_bot.strategies._dcf_check_for_order` với 37 mã live và `DCF_RATE_FRAME=domestc` cho ra 0 `dcf_error`, status giống hệt legacy.
3. **Một nguồn sự thật.**
   - Chọn hằng số trong chính `dcf_valuation.py`, không dùng `trading_rules.json` hay `wc_env.sh`. Lý do: mọi consumer đều import file này, gồm bot, lag_dd_pack (qua strategies), send_plan_report, eod_trading_report, dcf_refresh_gate, sector_lens/converge/alphalens (qua `dcf_line`), dc_book_waterfall_paper và custom_basket overlay. Vì vậy không phụ thuộc cron có source `wc_env.sh` hay không. Không cần đọc JSON lúc import, nên không có thêm đường lỗi nào. Rollback nằm trong cùng file với logic, được git version.
   - Env `DCF_RATE_FRAME` chỉ còn là override cho nghiên cứu/selfcheck. Mọi giá trị khác mặc định đều bị kêu.
   - [3a] quét 2715 file (`*.py`/`*.sh` gốc, `trading_bot/`, `mike/bin/*.sh|*.py`, `wc_env.sh`) cộng crontab: 0 chỗ gán. [3a0] là đối chứng dương cho regex quét: bắt được cả gán shell và gán env trong Python, bỏ qua docstring.
   - [3b]: import dưới 5 kiểu khởi chạy đều thấy `domestic_v2` và không cảnh báo: `env -i` kiểu cron + python3 hệ thống (pandas 2.3); `env -i` + venv; `env -i` với TZ=Pacific/Kiritimati; `source wc_env.sh` + `$DNA_PYEXE`; env phiên hiện tại.
4. **`dcf_earning_power.py:53` và 2 selfcheck CCTG.** Nguyên nhân từng cái:
   - `dcf_earning_power.py:53`: dòng này tính `rf = D.discount_rate − erp/100`. Phép trừ đó chỉ ra lãi huy động khi frame là legacy. Dưới v2 nó cho 12,25 − 6,5 = 5,75%, không phải rf 6,75 cũng không phải trần 5,5. Đây là bản chép tay công thức cap_rf của production nhưng không biết frame. Vá: ủy quyền cho `D.terminal_growth_mode(asof, "cap_rf", erp)`. Ở legacy hai bên dùng cùng nguồn CPI/GDP/rf nên ra cùng float. [4a] cho 0.07400000000000001 ở cả hai bên; [4b] dưới v2 cho 0.055. Mutation [M4] khôi phục dòng cũ thì [4b] đỏ còn [4a] vẫn xanh.
   - `cctg_deposit_wiring_selfcheck.py`: **4 FAIL thật** khi mặc định là v2, ở các assert "r = CCTG + ERP" của mục 5/7. Đây không phải lỗi code. Assert kiểm đường lãi huy động → r, mà đường này chỉ tồn tại ở legacy; dưới v2, r cố ý là hằng. Vá: pin `DCF.RATE_FRAME = "legacy"` cho mục 5/7 (biến module đọc lúc gọi), rồi khôi phục. Thêm assert v2: r = 0,1225 với cả knob CCTG 0/1 và asof trước/sau mốc. Kết quả 0 FAIL.
   - `cctg_tier2_series_selfcheck.py`: **không đỏ (92/92), nhưng rỗng nghĩa**. B1 "dcf.discount_rate vắng tier2 == có tier2" đúng một cách tầm thường khi r là hằng, nên mất khả năng bắt rò tier2 vào r. REPORT v2 ghi "sẽ hỏng"; đo thật thì là xanh rỗng nghĩa. Vá: pin legacy riêng cho dòng đó. Kết quả 92/92.
5. **Báo Ke theo khoảng.**
   - Chỗ duy nhất in r dạng điểm là CLI `dcf_valuation._print_report`. Đã grep: `format_dcf_check`, `dcf_line`, `lag_dd_pack`, `due_diligence`, `sector_valuation_lens`, `dcf_refresh_gate` không in r. Riêng `alt_valuation_lens` có COE 13% cố định, nhưng đó là Gordon P/B cho nhóm ngân hàng, không thuộc khung này, nên không đụng.
   - Vá: dưới v2, ngay dưới dòng r có thêm `[domestic_v2: diem mo hinh beta1 = rf 6.75 + ERP 5.5; ERP KHONG ben 5,22-6,15 => Ke KHOANG 12.5-13.5% o beta 1,1 — doc theo khoang, khong theo diem]`. Legacy không đổi.
   - Check [5]. Mutation [M5] làm note rỗng thì [5] đỏ.

## Kết quả chạy (đo trong phiên này)

- `dcf_rate_frame_selfcheck.py` (`DCF_RF_OPS_HEALTH=<worktree mike>/bin/ops_health_check.sh`): **30/30 PASS** ở cả TZ=Asia/Ho_Chi_Minh, TZ=Pacific/Kiritimati và `env -u TZ`. Log: `logs/tay_rf_{ict,kir,notz}.log`.
  - (a) legacy trùng byte main, md5 `4c0cf6e6ee6b267937c793c7dfda9a44`.
  - (b0) không env thì trùng byte domestic_v2, md5 `360b99e7154893a3740e4b16a496eea7`.
  - (b) khớp mô phỏng nghiên cứu: 145/145 mã, lệch 0.
  - (c) DGC 21407/32925/41779/29817.
- Quét rộng theo §23 (`dcf_valuation`/`strategies` là lõi), mỗi múi giờ một lượt. Đuôi log: `logs/sweep_tails.txt`.
  - Repo ngoài (worktree): `dcf_rate_frame`, `cctg_deposit_wiring`, `cctg_tier2_series`, `cpi_vn_tier15`, `dcf_check`, `dcf_selector`, `deposit_fallback_direction`, `tz_asof_ict_dd_dcf` đều rc 0 ×3.
  - mike/bin (worktree mike): `ops_health_check_selfcheck`, `_rejected`, `_lossbrake`, `_autofix_dryrun`, `lag_dd_gate_selfcheck`, `sector_valuation_lens_selfcheck`, `lag_plan_consistency_check_selfcheck`, `send_plan_report_park_jit_selfcheck` đều rc 0 ×3.
  - `test_trading_bot.py` **rc 1 trong worktree ×3**: `main paper: expected gap_adaptive_enabled=True, got False`. Nguyên nhân là môi trường. `trading_bot/config.py:18` đọc `secrets/trading_bot_accounts.json` (gitignored), file này không có trong worktree. Code `trading_bot/` của nhánh trùng main (0 dòng diff). Chạy cùng lệnh ở main thì rc 0.
  - Lưu ý: các selfcheck trong mike/bin import `trading_bot.strategies` của **main**, nên chúng chỉ chứng minh mục 16 ops_health không phá gì. Việc kiểm consumer chạy với `dcf_valuation` mới nằm ở dòng dưới.
- Smoke đường consumer thật (`smoke_consumer_path.py`, nạp `dcf_valuation` cùng `trading_bot` của worktree): 37 mã live/plan ngày 29/10. v2 so với legacy: 0 lật status, 0 lật robust, 0 `dcf_error`. Phân bố NOT_COMPUTED 23 / CHEAP 12 / RICH 2 ở cả hai frame. 23 NOT_COMPUTED là nhóm tài chính và FCFE âm, có sẵn trước khi vá.

## Hệ quả cần biết khi merge

- Từ lúc merge, mọi DCF production chạy domestic_v2: r = 12,25 cố định, g_T tối đa 5,5. `dcf_refresh_gate` (ngày 11 hằng tháng) vẫn kích hoạt theo lãi huy động, nhưng lần recompute đó không còn đổi r (no-op vô hại).
- `data/dcf_lens_history.csv` không có cột frame. Các dòng ghi sau merge là v2, trước merge là legacy. Muốn đánh giá về sau thì cắt theo ngày merge.
- Nghiên cứu cũ muốn tái lập số đã pin (`dcf_backtest`, `dcf_rate_robustness`, `dcf_earning_power_test`, `dcf_fv_sens_cache`, `custom_basket` overlay) phải chạy với `DCF_RATE_FRAME=legacy`. Với các mode khác cap_rf, dưới v2 sẽ raise có chủ ý. Lệnh này sẽ in dòng override, đó là điều mong muốn.
- ops_health mục 16 phải merge cùng lượt. Nếu merge trước `dcf_valuation`, nó im lặng: cây chưa có knob thì không WARN.
