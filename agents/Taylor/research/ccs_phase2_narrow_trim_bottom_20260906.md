# CCS Phase 2-NARROW — cắt 50% tỷ trọng tercile ĐÁY: **NO-GO**

> Taylor, job `Taylor_20260906_153255`, 2026-09-06. User duyệt 2026-09-06 22:31 ICT sau khi đọc Phase 1 (0/7 đề cử).
> Đề cương gốc: `mike/reports/research_proposal_conviction_sizing_20260905.md` · Phase 1: `ccs_phase1_expectancy_map_20260905.md` · Phase 0: `ccs_phase0_trade_ledger_20260905.md`.
> Thư mục chạy: `mike/agents/Taylor/research/ccs_phase2_Taylor_20260906_153255/`. Không file canonical/production nào bị đụng.

## Kết luận một dòng

**Bước 0 QUA rõ ràng** — vốn cắt ra KHÔNG nằm im ở tiền mặt: **91,3% được tái phân bổ** (BAL 84,0% / LAG 96,8%), nên cơ chế này *có* đường sống về mặt cơ học, và câu hỏi Phase 1 để mở đã được trả lời bằng số trên chính harness. **Bước 1 vẫn NO-GO**: 5/6 tiêu chí tiền-đăng ký ĐẠT (ΔCAGR **+0,910pp**, Calmar 1,623→1,790, IS/OOS cùng dấu, LOO chặt, PBO 0,010) nhưng **C5a DSR = 0,0012 ở N_trials = 8, RED FLAG**. Theo P3 đã khai trước — thiếu bất kỳ tiêu chí nào = NO-GO, không có "gần đạt".

Và DSR không phải nạn nhân của một quy ước khắt khe: **ngay cả bài kiểm tra KHÔNG hiệu chỉnh đa kiểm định cũng không qua** — P(Sharpe trim > Sharpe pin) = **0,602**, và bootstrap khối 95% CI trên ΔCAGR là **[−0,350pp; +1,749pp]**, ôm trọn số 0 (P(Δ>0) = 0,900). Hiệu ứng **đúng chiều và ổn định về dấu**, nhưng biên độ của nó nằm gọn trong dải nhiễu lấy mẫu của chính mẫu 12,5 năm này — trước khi trừ giá của 7 trial đi trước.

## 0. Tiền-đăng ký đã áp đúng, không nới một chữ

| | Cam kết | Thực tế |
|---|---|---|
| P1 | Một câu hỏi duy nhất: trim 50% BOTTOM, overlay sizing thuần | Chỉ `_wmult = 0,5` lên `target_value` tại lần fill đầu. Bộ chọn tín hiệu, DT5G, allocator `w_LAG`, CAPIT: **không đổi một tham số** |
| P2 | N_trials = 8, khai công khai | Dùng N = 8 cho DSR (báo cả N = 7 và 9 để so) |
| P3 | 5 tiêu chí, khai trước, không đổi sau khi thấy số | Bảng điểm §4 in nguyên trạng; tiêu chí duy nhất trượt là C5a |
| CẤM | Không thử thêm biến thể (30%/70%, theo sổ, theo regime) | **Chạy đúng 2 chân**: `ctrl` (pin) và `trim50`. Không có chân thứ ba nào tồn tại trong thư mục job |

**Chân control tái lập pin R3 md5 `7d053e6201c9d107685ff4d1dd9d2d2a` — TRÙNG TUYỆT ĐỐI với artifact pin 2026-08-03**, không cần chuẩn hoá gì. Đây là bằng chứng mạnh hơn "byte-identical sau khi bỏ qua vài dòng": nó chứng minh toàn bộ lớp patch (`_wmult`) là **no-op chứng minh được** khi tắt, nên mọi khác biệt ở chân treatment là do đúng một thứ.

Kiến trúc harness: `shn_trim.py` = bản SAO job-local của `simulate_holistic_nav.py` + 3 sửa nhỏ (cờ `_wmult` mang từ dòng tín hiệu vào `pending_entries`, nhân vào `target_value` trước mọi clamp tiền/margin/JIT-ETF, và một log). `ccs_p2_engine.py` = bản sao engine Phase 0 (vốn đã chứng minh byte-identical với pin), nạp `shn_trim` dưới đúng tên module chuẩn để mọi import phía dưới (`regime_size_overlay`, `add_capit_arm`) thấy cùng một object. Lệnh chạy = lệnh pin nguyên văn, cùng snapshot đóng cứng `bq_cache_asof20260729_postrestate`, `threads=1`, `$DNA_PYEXE`, `AUDIT_END=2026-06-19`.

`sig_rank_tercile` được **tính lại trong harness tại thời điểm chạy**, không join ngược từ ledger Phase 0: xếp hạng trong đúng pool `simulate()` xếp hạng, theo `(TIER_PRIORITY desc, ta desc)` sort ổn định, `rank_pct = (rank−1)/n_cands`, cắt 1/3–2/3 — nguyên văn định nghĩa `ccs_phase0_ledger.py::rank_panel`. Chỉ dùng thông tin CÙNG PHIÊN ⇒ không có look-ahead; không một cột `profit_*` nào xuất hiện trong đường code này.

Self-check cấp SỔ: `cash_flow_identity_max_err_vnd` = 1e-4 VND (BAL) / 1e-4 VND (LAG), `final_nav_identity_err_vnd` = 1e-4 / 0 — nhiễu float64 trên sổ ~556B/655B, đúng bậc với chân pin.

## 1. BƯỚC 0 — vốn cắt ra ĐI ĐÂU (cổng bắt buộc)

Đo trên chính harness, từ sổ per-book DAILY của hai chân, không suy từ ledger:

- `out_cut_frac(d)` = tổng `cut_vnd` của các vị thế bị trim **còn sống** ngày d, chia NAV sổ chân treatment = phần tỷ trọng sổ mà động tác trim đã rút khỏi cổ phiếu.
- `Δcash(d)` = tỷ lệ tiền mặt treatment − ctrl. **`redeploy_ratio = 1 − mean(Δcash) / mean(out_cut_frac)`**: 1,0 = mọi đồng cắt ra được đưa lại vào việc; 0,0 = nằm im ở tiền mặt 0%/năm.

| Sổ | phiên | vốn cắt TB (%NAV) | Δ tiền mặt | Δ cổ phiếu | Δ parking ETF | **redeploy** |
|---|---|---|---|---|---|---|
| BAL | 3.107 | 4,840% | +0,773pp | −1,034pp | +0,261pp | **0,840** |
| LAG | 3.107 | 6,263% | +0,198pp | −0,522pp | +0,324pp | **0,968** |
| **Gộp** | 6.214 | **5,552%** | **+0,486pp** | −0,778pp | +0,292pp | **0,913** |

Tách IS/OOS (kiểm chứng rằng kết luận không do một giai đoạn): IS BAL 0,728 · IS LAG 0,983 · OOS BAL 0,873 · OOS LAG 0,961.

**Ngưỡng dừng đã khai (<30% tái phân bổ ⇒ dừng ngay) KHÔNG chạm — cách xa gấp ba lần.** Hai đường hấp thụ nhìn thấy được: (a) mua thêm tên — chân trim có **6.553 lần fill mua vs 6.411** và **24.162B vs 23.637B** tổng vốn mua ra (+2,2%); (b) **parking custom30V** nhận thêm +0,29pp tỷ trọng trung bình — đúng thiết kế `PARK_STATES {3:0,7}`: tiền rảnh ở NEUTRAL tự chảy vào rổ parking chứ không ngồi im. Số vị thế riêng biệt gần như không đổi (2.582 → 2.566), tức là vốn đi vào **kích cỡ và parking**, không phải vào việc kéo dài đuôi danh mục.

**Một ô phải đọc đúng: BAL 2022 cho `redeploy = −11,16`.** Đó KHÔNG phải cơ chế trim thất bại — năm đó `out_cut_frac` chỉ 0,44% (gần như không có lệnh BOTTOM nào bị trim) trong khi Δtiền mặt +5,31pp là **phân kỳ đường đi** giữa hai danh mục đã khác nhau từ 2014. Tỷ số này chỉ có nghĩa khi mẫu số đủ lớn; đọc theo cột `out_cut_frac` trước, đừng đọc tỷ số trần trụi. Đây cũng là giới hạn chung của mọi so sánh A/B dài: càng về sau, Δtiền mặt càng pha tạp phân kỳ.

## 2. BƯỚC 1 — kết quả A/B đầy đủ

| | pin R3 (ctrl) | trim 50% BOTTOM | Δ |
|---|---|---|---|
| Final NAV | 1.178,010B | **1.286,017B** | +108,007B |
| CAGR | 28,863% | **29,773%** | **+0,910pp** |
| MaxDD | −17,785% | **−16,629%** | +1,156pp (đỡ hơn) |
| Calmar | 1,623 | **1,790** | +0,168 |
| Sharpe(252) | 1,832 | 1,906 | +0,075 |
| NAV sổ BAL (ref) | 519,487B | 556,289B | +7,1% |
| NAV sổ LAG (ref) | 590,759B | 655,238B | +10,9% |

Cả hai sổ cùng cải thiện — không phải hiện vật của một sổ. Số này cũng **xác nhận ước lượng bậc nhất của Phase 1 (+0,85pp) là hiệu chỉnh đúng**: sau khi Phase 1 tự bắt lỗi chặn `moved = min((k−1)·C_treat, C_funding)`, con số ước lượng rơi vào **+0,85pp** và harness thật trả **+0,910pp**. Công cụ ước lượng khả thi đã được kiểm định ngược một lần bằng thực nghiệm — đó là tri thức mang đi được, độc lập với verdict.

## 3. Cấu trúc thật của "tercile ĐÁY" — phát hiện quan trọng nhất của Bước 1

Bảng phân rã tercile theo `play_type` (từ `tercile_trim50_exp.csv`, đây là hồ sơ PIT thật engine dùng):

| Sổ | BOTTOM gồm gì |
|---|---|
| BAL (n=2.599 dòng BOTTOM) | **78,3% là tier `_W`** (DEEP_VALUE_RECOVERY_W 1.908 + RE_BACKLOG_BUY_W 86 + MOMENTUM_W 42); phần còn lại chủ yếu DEEP_VALUE_RECOVERY thường |
| LAG (n=1.427 dòng BOTTOM) | **99,4% là `LAG_LO`** (1.418/1.427) |

Trên các lệnh THỰC SỰ bị trim (306 mục tiêu, 303 khớp thành lệnh): BAL 74/88 là tier `_W`; LAG **214/218 là `LAG_LO`**.

Lý do cơ học: tier `_W` có `TIER_PRIORITY` = 0 và `LAG_LO` = 82 (so với `LAG_HI` 88), mà khoá xếp hạng là `(priority, ta)` — nên hai nhóm này **rơi xuống đáy bảng một cách tất định**, không phải do "xếp hạng tín hiệu trong ngày phát hiện ra chúng kém". Ở sổ LAG điều này còn tuyệt đối hơn: `ta` là hằng số 400,0 cho MỌI dòng LAG, nên tercile ở đó **hoàn toàn** do tier quyết định, cộng vị trí trong danh sách ứng viên.

**Hệ quả cho việc diễn giải, phải nói thẳng:** "cắt 50% tercile đáy" trên thực tế ≈ **"hạ tỷ trọng tier `_W` của BAL và tier `LAG_LO` (0,08 → 0,04)"**. Đó không phải một trục sizing MỚI theo conviction — đó là **re-tune hai tham số tier weight mà engine vốn đã phân biệt sẵn**. Điều này quan trọng theo hai chiều ngược nhau:

- Chiều ủng hộ: nó *có* nghĩa kinh tế rõ (engine đã tự dán nhãn hai nhóm này là yếu hơn; kết quả nói nhãn đó đúng và hiện đang bị định cỡ quá tay).
- Chiều chống: nó đưa kết luận thẳng vào vùng **"đừng re-tune tham số theo lịch sử"** — và một re-tune tham số trên đúng mẫu đã sinh ra 7 trial trước là chính xác thứ mà DSR ở §4 tồn tại để phạt.

Tôi ghi cả hai chiều vì cái nhãn "conviction tercile" đã che mất bản chất này suốt Phase 0/Phase 1, và bất kỳ ai đọc lại trục CCS về sau cần biết mình đang nhìn cái gì.

## 4. Bảng điểm P3 — nguyên trạng, không thêm không nới

| | Tiêu chí (khai TRƯỚC) | Kết quả | Đạt |
|---|---|---|---|
| C1 | ΔCAGR > +0,385pp (sàn nhiễu harness) | **+0,910pp** | ✅ |
| C2 | Calmar không xấu đi | 1,623 → **1,790** | ✅ |
| C3 | IS(2014-19) và OOS(2020+) cùng dấu | IS **+0,265pp** / OOS **+1,527pp** | ✅ |
| C4 | LOO per-year giữ dấu, không dồn 1-2 năm | 13/13 năm giữ dấu; năm đóng góp lớn nhất (2018) = **22%** của Δ | ✅ |
| **C5a** | **DSR ≥ 0,95 với N_trials = 8** | **P = 0,0012** (N=7: 0,0051 · N=9: 0,0003) | ❌ |
| C5b | PBO < 0,5 | **0,010** (CSCV S=16, 12.870 tổ hợp) | ✅ |

**VERDICT: NO-GO.**

Ba điều cần đọc kèm để verdict này không bị hiểu sai theo cả hai hướng:

1. **C3 đạt về DẤU nhưng IS dưới sàn nhiễu.** +0,265pp ở IS nằm **dưới** 0,385pp; gần như toàn bộ độ lớn nằm ở OOS (+1,527pp). Tiêu chí chỉ đòi cùng dấu nên nó qua đúng luật — nhưng khớp với quan sát Phase 1 rằng **tỷ lệ lệnh rơi vào tercile đáy tăng theo thời gian** (2,7% năm 2014 → ~20% năm 2025-26): giá trị của luật phụ thuộc chế độ gần đây hơn là vào 13 năm mẫu. Riêng sổ BAL có **0 lệnh bị trim** ở 2014, 2015, 2016, 2019 và 2022.
2. **DSR trượt không phải vì quy ước khắt khe.** Kể cả bỏ hết hiệu chỉnh N: `DSR vs SR0 = Sharpe của chính chân pin` cho **P = 0,602** — Sharpe 1,906 không phân biệt được với 1,832 trên 3.107 phiên. Bootstrap khối vòng (L=21, B=4.000) trên chuỗi Δ log-return: **CI 95% [−0,350pp; +1,749pp]**, P(Δ>0) = 0,900. Bootstrap **theo cặp** (lấy mẫu cùng khối ngày cho cả hai chân, tính lại CAGR mỗi chân rồi trừ): L=21 trung vị +0,911pp, CI [−0,468; +2,232], P(Δ>0) = 0,900; L=63 CI [−0,189; +2,140], P = 0,945. **Không cửa sổ nào cho CI loại trừ số 0 ở mức 95%.**
3. **PBO = 0,010 KHÔNG cứu được gì và không nên trích rời.** Với họ chỉ có 2 cấu hình `{ctrl, trim50}`, CSCV chỉ trả lời "chọn cấu hình tốt hơn trong mẫu có tiếp tục tốt hơn ngoài mẫu không" — trim thắng nhất quán về DẤU, nên PBO thấp là hệ quả tất yếu của C3/C4, không phải bằng chứng độc lập về ý nghĩa thống kê. Trích "PBO 0,01" mà bỏ "DSR 0,0012" là đọc sai bộ đôi này.

## 5. Điều gì thay đổi và điều gì không

**Đã trả lời dứt điểm (giá trị chính của dispatch này):** câu hỏi Phase 1 để mở — *"vốn cắt ra có đi được lên trên hay nằm im ở tiền mặt?"* — câu trả lời là **đi được, 91%**. Giả thuyết "toàn bộ +1,69pp bốc hơi vì chạm trần trọng số/tên" mà tôi nêu ở Phase 1 §6.2 **bị bác bằng số đo trên harness**, không phải bằng lập luận. Kênh hấp thụ chính không phải "mua thêm tên" như tôi đoán mà là **kích cỡ vị thế + parking custom30V** — parking là mảnh tôi đã bỏ sót khi suy từ ledger, và nó chính là lý do ledger không thể trả lời câu hỏi này.

**Không thay đổi:** không wire gì vào production. `filter.json`, `pt_v23_audit_2014.py`, `simulate_holistic_nav.py`, `trading_rules.json`, tier weights LAG/BAL — không đụng.

**Không đề xuất biến thể tiếp theo.** Trim 30%/70%, trim theo sổ, trim kèm điều kiện regime — tất cả bị cấm rõ trong dispatch và tôi không đề nghị mở lại. Với DSR ở mức này, mỗi biến thể thêm chỉ **làm N_trials to hơn và ngưỡng cao hơn**, tức là tự làm khó chính mình bằng đúng cơ chế đã giết trial này. Đây là lần NO-GO tiếp theo trên một trục mà mọi ô đã được đo hết; **tôi coi trục CCS là đóng.**

**Nếu về sau ai muốn mở lại**, hình dạng duy nhất tôi thấy có cơ sở KHÔNG phải "thêm một liều trim" mà là câu hỏi ở §3: *tier `_W` và `LAG_LO` có đang được định cỡ quá tay không* — và đó phải là một nghiên cứu tier-weight tiền-đăng ký riêng, trên dữ liệu ngoài mẫu 2014-2026 này (mẫu đã bị 8 trial dùng hết), chứ không phải trial thứ 9 trên cùng mẫu. Nói thẳng: tôi không nghĩ mẫu này còn đủ chỗ cho một câu hỏi nữa.

## 6. File

`mike/agents/Taylor/research/ccs_phase2_Taylor_20260906_153255/`

| File | Nội dung |
|---|---|
| `shn_trim.py` · `patch_shn.py` | bản sao `simulate_holistic_nav.py` + 3 sửa `_wmult` (kèm script patch, 4 anchor assert) |
| `ccs_p2_engine.py` · `patch_engine.py` | bản sao engine Phase 0 + overlay tercile PIT + thu log trim |
| `run_leg.sh` · `run_ctrl.log` · `run_trim50.log` | lệnh pin nguyên văn, một tham số khác duy nhất: `CCS_TRIM_FRAC` |
| `step0_where_did_the_cash_go.py` · `step0_result_exp.json` · `step0_daily_exp.csv` | cổng Bước 0: bảng vốn cắt ra đi đâu, per book × year |
| `analyze_step1.py` · `step1_result_exp.json` | bảng điểm P3 (C1–C5b), IS/OOS, LOO, DSR, PBO |
| `boot_delta.py` · `boot_delta_exp.json` | bootstrap khối chuỗi-Δ và theo-cặp (L=21, 63) |
| `tercile_trim50_exp.csv` · `trimlog_trim50_exp.csv` | hồ sơ tercile PIT đầy đủ + từng lệnh bị trim (ngày, mã, `cut_vnd`) |
| `daily_*_exp.csv` · `tx_*_exp.csv` · `metric_*_exp.csv` | sổ DAILY / TX / METRIC của cả hai chân |

Mọi output mang hậu tố `_exp` và nằm trong thư mục job theo job-id (§8 coding_guidelines). CSV audit của hai chân ghi dưới `EXP_TAG=ccsp2ctrl` / `ccsp2trim50` — không chạm một đường dẫn pin nào.

## 7. Ghi chú kỹ thuật đáng mang đi

**`circular_block_boot` trong `dsr_pbo_annex.py` trả về TUPLE `(CAGR, DD)`, không phải một mảng.** Bản chạy đầu của tôi `ravel()` cái tuple đó → trộn lẫn drawdown vào mẫu CAGR và cho ra CI **[−0,087; +0,016]pp** với P(Δ>0) = 0,450, mâu thuẫn thẳng với điểm ước lượng +0,714pp ngay dòng trên. Bắt được vì **hai con số cạnh nhau không thể cùng đúng** — không phải vì code báo lỗi. Cùng họ với bẫy `isfinite` ở Phase 1: giá trị hữu hạn, kiểu dữ liệu hợp lệ, hoàn toàn vô lý. Quy tắc rẻ nhất: in điểm ước lượng ngay cạnh CI của nó và nhìn xem CI có ôm lấy điểm ước lượng không.

**Overlay sizing per-row an toàn nhất khi cài như một hệ số nhân mang theo dòng tín hiệu, không phải như tier ảo.** Cám dỗ đầu tiên là đổi `play_type` của nhóm BOTTOM thành `MOMENTUM__TRIM` rồi khai tier weight riêng — làm thế sẽ đụng SV_TIGHT, EXBULL-suppress, `margin_tiers`, `hold_days_by_tier`, `sector_cap_exempt`, tức là đổi nhiều thứ hơn ý định. Cột `_wmult` mặc định 1,0 nhân vào `target_value` **trước** các clamp tiền/margin/JIT-ETF cho đúng một điểm tác động, và chứng minh được là no-op bằng md5 trùng pin.

**Winsor [1%, 99%] không áp dụng ở Phase 2:** ràng buộc đó thuộc thống kê `R = ret/(σ60·√phiên)` cấp lệnh của Phase 1. Phase 2 đo trên NAV cấp hệ thống, không có đại lượng nào lấy biến động làm mẫu số ⇒ không có ô để winsor. Ghi ra để người đọc không đi tìm.
