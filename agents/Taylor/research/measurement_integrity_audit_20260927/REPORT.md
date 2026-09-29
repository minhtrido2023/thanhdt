# Audit "lỗi đo cơ bản" — toàn bộ chuỗi RETURN / LEVEL / NAV / WEIGHT / ADV

job=Taylor_20260927_043544 · 2026-09-27 · Taylor · **ĐỌC-CHỈ, paper-only, KHÔNG sửa code**
PREREG: `PREREG.md` (viết trước khi đọc kết quả) · Trả lời câu hỏi user: *"còn sai sót cơ bản về
cách tính nào còn tồn tại không?"*

---

## 0. Kết luận cấu trúc — cái quan trọng hơn danh sách FAIL

**`self-check 0 VND` là một ĐỊNH THỨC TIỀN MẶT, nên nó MÙ HOÀN TOÀN với chính lớp bug vừa xảy ra.**
`simulate_holistic_nav.py` reconcile dòng tiền vào/ra mỗi phiên (`:878`, `:1457`, `:947`). Một chuỗi
GIÁ/LEVEL sai (custom30V nhân thêm OShares) vẫn reconcile 0 VND tuyệt đối — vì mọi giao dịch được
định giá bằng CHÍNH cái chuỗi sai đó, hai bên của định thức lệch cùng chiều và triệt tiêu.

Hệ quả: cổng chất lượng số 1 của fleet không hề canh chuỗi giá. Mọi phát hiện dưới đây đều thuộc
loại mà `self-check 0 VND` không bao giờ bắt được — và cũng không có selfcheck nào khác canh.

**Một sự thật làm giảm phạm vi lo ngại (đã kiểm chứng bằng code, không phải giả định):**
sổ VND của engine **BẤT BIẾN theo hệ quy chiếu giá**. `simulate_holistic_nav.py:569` `gross =
pos["shares"] * open_px` — `shares` được sinh ra từ `amount_vnd / px` cùng hệ, nên
`shares_adj × px_adj ≡ shares_raw × px_raw`. Vì vậy chuỗi NAV BAL/LAG/park **không** mắc lớp bug
custom30V, và mọi so sánh %ADV (VND vs VND) cũng đúng. Bug custom30V đặc biệt vì nó đưa một số
lượng (`OShares`) vào chuỗi **RETURN**, chỗ duy nhất mà tính bất biến đó bị phá.

---

## 1. Bảng chuỗi × bất biến

Ký hiệu: **(a)** return chỉ từ giá adj · **(b)** hệ quy chiếu adj-vs-thô · **(c)** không đếm 2 lần
corp-action · **(d)** số CP đúng ngày · **(e)** không look-ahead · **(f)** đơn vị/tần suất.
`—` = không áp dụng.

| # | Chuỗi | (a) | (b) | (c) | (d) | (e) | (f) | Dòng code chốt |
|---|---|---|---|---|---|---|---|---|
| 1 | `custom_basket` RETURN (sau fix) | **PASS** | — | PASS | — | PASS | PASS | `custom_basket.py:261-262`, `:1174-1176`, `:1205-1208` |
| 2 | `custom_basket` WEIGHT / mcapw | — | **PASS** | — | **FAIL-B** | **FAIL-A** | PASS | `:257`/`:1168` (`pxw*OShares` = thô×thô ✓); `:255`/`:1166` `.bfill()` |
| 3 | `custom_basket` member-selection liq | — | PASS | — | — | PASS | PASS | `:234`, `:336` (`Volume_3M_P50*pxw_sql()` thô×thô) |
| 4 | `custom_basket` ey/cfy/ps (1/PE…) | — | PASS | — | — | PASS | — | `:426-440` (PEADJ mặc định OFF — đúng, có bằng chứng 1,4M dòng) |
| 5 | `custom_basket.build_pit` vs `build` | — | — | — | — | PASS | — | `:336` dùng quý ĐÃ HOÀN TẤT |
| 6 | Ledger BAL (`SIGNAL_V11`+SHN) | PASS | PASS | PASS | — | PASS | PASS | `signal_v11_sql.py:95` (`Volume_3M_P50*COALESCE(Price,Close)` thô×thô) |
| 7 | Ledger LAG | PASS | PASS | PASS | — | **FAIL-C** | PASS | `pt_v23:1332` liq thô×thô ✓; `:2057-2059`+`:2062-2066` cổng w_LAG |
| 8 | Park leg (xe custom30V) | PASS | PASS | **FAIL-D** | — | PASS | PASS | `simulate_holistic_nav.py:427-437`, `:888-890` |
| 9 | Gated-overflow / recovery-park | — | — | — | — | PASS | PASS | `pt_v23:1742-1748` (`_pe_pct_asof`, `_pbz_asof`, accel "causal T-1") |
| 10 | NAV tổng + self-check 0 VND | PASS | PASS | PASS | — | PASS | PASS | định thức đúng — **nhưng xem §0: nó không canh giá** |
| 11 | ADV / cap size (BAL+LAG) | — | PASS | — | — | PASS | PASS | `pt_v23:280` `LAG_ADV_BASIS="price"` mặc định (đã vá 08-02) |
| 12 | ADV nhánh `ETF_LIQ=creation` | — | **FAIL-E** | — | — | **FAIL-E** | PASS | `pt_v23:894-895` |
| 13 | `bootstrap_nav.py` | — | — | — | — | PASS | **FAIL-F** | `:51` `yrs = N/252.0`, `:53` `sqrt(252)` |
| 14 | `dsr_pbo_annex.py` | — | — | — | — | PASS | **FAIL-F** | `:142` `yrs = len(logp)/ANN`, `:21` `ANN=252.0` |
| 15 | `regime_size_overlay.py` | — | — | — | — | PASS* | — | `:96` `merge_asof(direction="backward")` trên `eff_date` |
| 16 | `edge_health_monitor` IC lens | PASS | PASS | — | — | PASS | PASS | `:64-66` `LEAD(Close,60)/Close`; `liq` thô×thô |
| 17 | `edge_health_monitor.lag_edge_health` | PASS | — | — | — | **FAIL-C (gốc)** | PASS | `:163-167` nhãn `entry` cho return forward 25 phiên |
| 18 | `rating_8l_history.py` | — | — | — | — | **FAIL-G** | — | `:102-110` không có cột giá nào; `:116-117` `ANY_VALUE(ICB_Code)` |
| 19 | `dividend_adjusted_return.py` | — | PASS | **PASS** | PASS* | PASS | PASS | `:1137` `end_price=Price` thô; `:255-290`; `:754` `qty_entitled` |
| 20 | `nav_period_returns.py` | — | — | **FAIL-H** | — | PASS | **FAIL-H** | `:107`, `:133` `nav1/nav0 - 1` |
| 21 | `compute_active_nav.py` | — | PASS-gate | PASS | PASS | PASS | — | `:28-42` §exdate_frame rc=6; `:381-388` rc=7; `:263` `Close` chỉ nhánh quá khứ |
| 22 | `daily_nav_snapshot.py` | — | PASS | PASS | PASS | PASS | — | `:15-18` dùng `Price` THÔ có chủ đích + `classify_qty_residual:427` |
| 23 | `backtest_recovery_alloc{,_2011}.py` | — | — | — | — | — | — | **CHƯA QUÉT** (xem §4) |

`PASS*` = pass nhưng có dư lượng, ghi trong §3.

---

## 2. FAIL xếp theo MỨC ẢNH HƯỞNG

### FAIL-H — `nav_period_returns.py`: tỉ suất công bố KHÔNG có số hạng dòng tiền vào/ra
**Mức: CAO NHẤT (tiền thật, số user đọc).** ĐÃ XÁC NHẬN, chưa nổ.

`nav_period_returns.py:107` và `:133`:
```python
"return_pct": round((nav1 / nav0 - 1) * 100, 3),
```
Đây là nguồn chuẩn tắc DUY NHẤT cho bảng "Hiệu suất lũy kế" của báo cáo SpaceX weekly/monthly
(coding_guidelines §31 bắt buộc). Nó là tỉ số NAV thuần — **không trừ tiền nạp, không cộng lại tiền
rút**. Và `data/execution_logs/nav_history_{SpaceX,ZaloPay}.csv` **không có cột dòng tiền nào**:
schema thật = `date,nav,mtm_stock,cash,margin_debt,offbook_assets,egg_assets,balance_ts,cum_dividend_excl,nav_is_estimate,nav_source`.
`grep -niE "net_flow|deposit_vnd|withdraw|capital_flow"` trên cả `daily_nav_snapshot.py` +
`nav_period_returns.py` + `compute_active_nav.py` + CSV → **0 hit**.

Hệ quả cơ học: user nạp thêm 200tr vào SpaceX → báo cáo tuần đó công bố "+20% lợi nhuận". Rút
100tr → "−10%". Không có cảnh báo, không có gate, rc=0.

Vì sao CHƯA nổ: tới 2026-09-25 cả hai TK đều `offbook_assets=0` và chưa có lần nạp/rút nào sau
inception. `egg_assets` (Trứng vàng) là túi TRONG NAV nên transfer nội bộ tự triệt tiêu ở NAV
TỔNG — đúng bài học Taylor đã ghi 2026-09-26. Rủi ro là lần nạp/rút ĐẦU TIÊN.

Ghép với memory `project-dnse-trung-vang-offbook-assets` (*"MUST update `manual_offbook_assets_vnd`
on every withdrawal or NAV double-counts"*): hôm nay việc đó chỉ được giữ bằng KỶ LUẬT của người
vận hành, **không có cơ chế nào cưỡng chế**, và nếu quên thì hệ quả không phải "misreport NAV" mà
là "công bố một khoản LỖ không hề tồn tại".

**Đo:** không cần backtest — lỗi 1-ăn-1 với mọi VND dòng tiền. Sai số = `flow / nav0`.

---

### FAIL-C — cổng `w_LAG` của production đọc một chuỗi look-ahead 25 phiên
**Mức: CAO (chạm số pin R3 + logic phân bổ live).** ĐÃ XÁC NHẬN + ĐÃ ĐO.

`edge_health_monitor.py:163-167` xây `data/lag_edge_health.csv`:
```python
pos = idx.searchsorted(r["Release_Date"], side="right") - 1 + 5   # entry T+5
p0, p1 = pxc.iloc[pos][tk], pxc.iloc[pos + 25][tk]
rows.append({"entry": idx[pos], "ret": (p1 / p0 - 1) * 100})
```
`ret` là return **forward 25 phiên**, nhưng dòng được **dán nhãn theo `entry`**. `mean12` ở dòng i
(`:173`) gộp mọi `ret` có `entry` trong 365 ngày *tới và gồm* `entry[i]` — tức gồm cả return của
chính sự kiện i, thứ chỉ biết được 25 phiên SAU `entry[i]`.

Engine đọc đúng nhãn đó rồi ffill lên lịch ngày — `pt_v23_audit_2014.py:2057-2059`:
```python
_eh = pd.read_csv(.../"lag_edge_health.csv", parse_dates=["entry"]).drop_duplicates("entry").set_index("entry")...
_edge_m12 = _eh.reindex(common, method="ffill")
```
rồi `:2062-2066` `w_lag_target()` → `0.65 if m >= EDGE_THR(4.0) else 0.50`. `pt_v22_dt5g.py:777`
đọc y hệt.

Docstring `:124-125` tự khai *"Series inherently lags ~5 weeks"* — điều đó đúng cho **LIVE** (dòng
mới nhất chỉ xuất hiện khi sự kiện đã hoàn tất ⇒ live là BẢO THỦ, không có lỗi). Nhưng trong
**BACKTEST**, nhãn ngày là `entry`, nên engine đọc được thông tin sớm 25 phiên.

**ĐO THẬT** (`data/lag_edge_health.csv`, 583 dòng, 2012-05-09→2026-08-14; so as-is vs bản dịch
nhãn +25 phiên giao dịch, trên 3.654 ngày so sánh được):

| | ngày |
|---|---|
| Cổng bật `0.65` khác nhau | **317 (8,7%)** |
| as-is `0.65` / causal `0.50` (**peek CÓ LỢI**) | 159 |
| as-is `0.50` / causal `0.65` (peek BẤT LỢI) | 158 |
| as-is bật 0.65 | 1.711 (46,8%) |
| causal bật 0.65 | 1.710 (46,8%) |

Look-ahead là THẬT và cơ học, nhưng **gần như đối xứng** — nó là một phép DỊCH THỜI GIAN, không
phải một cú nhìn trộm có hướng. Vì vậy nó khác hẳn ca custom30V (đơn hướng, +4,48pp). Không có cơ
sở để dự đoán dấu của tác động lên NAV.

**Tác động lên CAGR R3: chưa đo — cần job riêng** (phải chạy lại full engine với CSV đã dịch nhãn;
1 leg ≈ vài giờ). KHÔNG ước lượng bằng trực giác.

---

### FAIL-F — `bootstrap_nav.py` + `dsr_pbo_annex.py` annualize theo PHIÊN, registry theo LỊCH
**Mức: TRUNG BÌNH (số pin trong KB).** ĐÃ XÁC NHẬN + ĐÃ ĐO.

`bootstrap_nav.py:51` `yrs = N / 252.0` · `dsr_pbo_annex.py:142` `yrs = len(logp)/ANN` (`ANN=252.0`).
Nhưng `simulate_holistic_nav.py:1567-1569` — nguồn của mọi con số registry — dùng LỊCH:
`n_yrs = n_days / 365.25`, đúng CLAUDE.md §Backtest (*"Metric tính trên thời gian lịch, không phải
số phiên"*).

**ĐO THẬT** trên CHÍNH 2 CSV R3 (đồng thời tái lập đúng cả 2 số pin ⇒ phép đo của tôi khớp engine):

| CSV | N_ret | ngày lịch | yrs lịch | yrs /252 | CAGR lịch | CAGR /252 | thiên lệch |
|---|---|---|---|---|---|---|---|
| R3 POST-FIX (`_exp_pin_retleg_flat_univpit`) | 3.106 | 4.551 | 12,460 | 12,325 | **24,3775%** | 24,6740% | **+0,297pp** |
| R3 PRE-FIX (`_exp_ctrl_retleg_legacy_univpit`) | 3.106 | 4.551 | 12,460 | 12,325 | **28,8627%** | 29,2199% | **+0,357pp** |

⇒ Cột CAGR của bootstrap/DSR annex **KHÔNG so sánh được** với cột CAGR của registry; nó cao giả
~+0,3pp một cách hệ thống. Con số KB **"Bootstrap 5th-pct: CAGR 18,6%"** vì vậy cao giả ~+0,3pp
(đúng ~18,3%). Sharpe cũng lệch cùng lớp: `sqrt(252)` vs `sqrt(3106/12,460)=sqrt(249,3)`, tức
+0,54% (1,90 → ~1,89) — không đáng kể nhưng CÙNG một lỗi.

Lưu ý: FAIL này **độc lập** với việc re-pin sau merge. Khi chạy lại bootstrap+DSR theo
`viec_con_lai_sau_merge`, nếu không sửa `yrs` thì số mới vẫn cao giả +0,3pp.

---

### FAIL-D — chân park tính cổ tức GỘP: thiếu thuế TNCN 5% + phí tái đầu tư
**Mức: TRUNG BÌNH (một chiều, bất lợi cho độ tin cậy của +7,4pp parking).** XÁC NHẬN, đo sơ bộ.

Chuỗi level custom30V dùng `Close` **đã điều chỉnh** ⇒ theo định nghĩa đây là *total return với cổ
tức tái đầu tư tức thì, GỘP, không phí*. Trong thực tế đây là rổ 30 cổ phiếu **tự quản** (`PARK_TICKER
= "CUSTOM_VN30G"`): cổ tức tiền về tài khoản, bị **thuế TNCN 5%**, rồi mới mua lại (có phí + slippage).
`simulate_holistic_nav.py:888-890` chỉ trừ `etf_mgmt_fee_annual`/`etf_tracking_drag_annual`, và cả
hai **= 0** cho nhánh basket tự quản (đúng: không có phí quản lý quỹ) — nên **không có gì thay chỗ
thuế cổ tức + phí tái đầu tư**.

**Đo sơ bộ (BQ, `tav2_bq.ticker` ∩ `fa_ratings_8l` rating≤3, 2015→2026-06-15, DY∈(0;0,5), n=1.558.938):**
DY p50 = **6,25%**, trung bình 7,23%. Lọc `DY>0` nên đây là chặn TRÊN (bỏ tên không trả cổ tức).
Với DY hiệu dụng của rổ 4-6% ⇒ thuế 5% ≈ **0,20-0,30pp/năm** mà chân park đang thừa. Với một xe
được giữ NHIỀU NĂM ở NEUTRAL, đây là hiệu ứng năm-tròn — khác BAL/LAG (hold 45/25 phiên) nơi chỉ
cổ tức rơi trong cửa sổ mới tính.

Một phần đã nằm trong quy ước chung *"CAGR thật ≈ CAGR backtest − 1,5%"* (CLAUDE.md), nhưng
quy ước đó là haircut TỔNG, không phải mô hình — và nó KHÔNG được áp khi so **chân park vs chân
không-park** (chính là cách +7,4pp được đo). **Chưa đo chính xác — cần DY theo trọng số thành
viên thật của từng kỳ rebal.**

---

### FAIL-A / FAIL-B — chân WEIGHT của `custom_basket`: `.bfill()` + OShares theo QUÝ không theo ex-date
**Mức: THẤP (bậc hai — chỉ đổi trọng số, không đổi return từng tên).** XÁC NHẬN, chưa đo.

`custom_basket.py:255` và `:1166` (hai bản, `build` và `build_pit`):
```python
bx["OShares"] = bx.groupby("ticker")["OShares"].ffill().bfill()
```
- **FAIL-A (e)**: `.bfill()` lấp các ngày TRƯỚC dòng financial đầu tiên bằng giá trị TƯƠNG LAI đầu
  tiên. Đó là look-ahead cơ học. Phạm vi hẹp: chỉ prefix trước báo cáo đầu tiên của mỗi tên (cửa sổ
  mồi 200 ngày ở `build`, 10 ngày ở `build_pit`).
- **FAIL-B (d)**: `OShares` bước theo **ranh giới QUÝ** (join theo `fin.ftime`), không theo
  **ex-date**. Ở ngày ex của một đợt CP thưởng/tách, `pxw` (giá THÔ) tụt ngay trong khi `OShares`
  chưa tăng tới hết quý ⇒ `mcapw` của tên đó bị hụt tới ~10-30% trong tối đa một quý ⇒ trọng số bị
  lệch. Đây là **cùng một lớp bug** với FAIL-E và với ca VPB/exdate của `compute_active_nav`, chỉ
  khác là ở đây nó rơi vào chân WEIGHT nên tác động là bậc hai.

Cả hai đều KHÔNG chạm chân RETURN (đã gỡ `OShares` ở `1b89881b`). **Chưa đo, cần job riêng** (1 leg
engine với `OShares` join theo ex-date).

---

### FAIL-E — nhánh `ETF_LIQ="creation"`: hệ quy chiếu sai + 2 look-ahead
**Mức: THẤP (NGOÀI đường pin R3).** XÁC NHẬN.

`pt_v23_audit_2014.py:894-895`:
```sql
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*t.Close) DESC LIMIT 30
```
Ba lỗi trong hai dòng: **(b)** `Volume_3M_P50` (SL thô) × `Close` (đã điều chỉnh) — vi phạm chính
luật mà file này tự viết ở `:275-278` và đã tự vá cho `LAG_ADV_BASIS` ngày 2026-08-02; **(e)** cửa
sổ chọn top-30 **hardcode `2020-01-01..2025-01-01`** rồi áp cho toàn backtest từ 2014 = hindsight
membership; **(e)** `IN (SELECT DISTINCT ticker FROM ticker_prune)` không có điều kiện `time` =
đúng anti-pattern coding_guidelines §9b.

R3 chạy `ETF_LIQ=custompitg` nên nhánh này KHÔNG trên đường pin. `custom_basket.py:234`/`:336` đã
dùng `pxw_sql()` đúng. Đây là nợ cũ sót lại của một lần vá không quét hết call-site.

---

### FAIL-G — `rating_8l_history.py`: route gán theo ICB_Code CỦA HÔM NAY
**Mức: THẤP.** XÁC NHẬN.

`:116-117`:
```sql
SELECT t.ticker, ANY_VALUE(t.ICB_Code) AS ICB_Code
FROM tav2_bq.ticker AS t
```
Không có điều kiện `time`, và `ANY_VALUE` chọn không tất định. Toàn bộ panel rating lịch sử được
gán **route** (COMPOUNDER/CYCLICAL/BANK/…) bằng phân ngành *của hôm nay*, áp hồi tố về 2014. Tên
nào bị tái phân ngành sẽ được chấm bằng thang của ngành MỚI ở những quý mà nó chưa thuộc ngành đó.

Điểm tốt: `:102-110` cho thấy module này **không đọc cột giá nào** (chỉ ROE/ROIC/FSCORE/NP/GPM/
Revenue) ⇒ (a)(b)(d) miễn nhiễm hoàn toàn với lớp bug custom30V; `eff_date = Release_Date` ⇒ (e)
đúng ở trục thời gian tài chính. Chỉ trục PHÂN NGÀNH là không-PIT.

---

## 3. PASS có dư lượng (không phải FAIL, nhưng phải nói)

1. **`dividend_adjusted_return.py` (#19) — PASS, thiết kế tốt.** Khung THÔ suốt: `:1137` `end_price
   = t.Price` (thô), `cost_per_share` = giá vốn broker (thô), cổ tức tiền **cộng riêng** rồi trừ
   thuế (`:266-272`). Không có chỗ nào cộng cổ tức lên giá ĐÃ điều chỉnh ⇒ test "holder tổng hợp"
   (c) PASS. Cổ phiếu thưởng/tách hạ về `UNVERIFIED` và **CẤM** vào báo cáo (`:112`, `:1076`,
   `:1105`) = fail-closed đúng.
   *Dư lượng:* `PositionReturn.dividend_total_gross` (`:262`) = **một** `qty` vô hướng × TỔNG cổ
   tức/CP của MỌI ex-date. Nếu vị thế đổi kích cỡ GIỮA hai ex-date (không đúng ngày cum), số sẽ
   sai. Đường báo cáo thật dùng `resolve_dividends()`/`qty_entitled()` (`:754`) — có KL đúng từng
   ex-date, nên an toàn; rủi ro chỉ ở đường CLI một-mã (`:1927`). `:1318` cho thấy mua thêm đúng
   ngày cum bị hạ `STOCK_SUSPECTED` ⇒ đã fail-closed một phần.
2. **`compute_active_nav.py` (#21) — PASS-CÓ-GATE.** §exdate_frame (`:28-42`) chặn đúng lớp bug
   "KL và giá khác hệ quy chiếu" bằng **rc=6 KHÔNG ghi file**, và rc=7 (`:381-388`) bịt lối vòng
   `--asof` quá khứ. *Dư lượng:* `:263` nhánh `--asof` quá khứ vẫn lấy `Close` (đã điều chỉnh) nhân
   với vị thế **LIVE** — rc=7 chỉ từ chối GHI, nó vẫn **IN** con số lệch hệ ra cho người vận hành
   "đối chiếu/khảo sát". Một con số sai vẫn được in ra là một con số có thể bị chép lại.
3. **`daily_nav_snapshot.py` (#22) vs `compute_active_nav.py` (#21) dùng HAI cơ sở giá khác nhau**
   cho cùng câu hỏi "vị thế này trị giá bao nhiêu": snapshot dùng `Price` THÔ có chủ đích (`:15-18`,
   đo thật VHM 21/07 Close 68.200 vs broker 136.900), active_nav dùng `Close` ở nhánh quá khứ. Cả
   hai đều tự biện luận được, nhưng đây là hai hệ quy chiếu cùng tồn tại — chính là điều kiện sinh
   ra lớp bug này.
4. **`regime_size_overlay.py` (#15) — PASS.** `:96` `merge_asof(direction="backward")` theo
   `eff_date`. *Dư lượng:* `tav2_bq.fa_ratings_8l` là snapshot dựng LẠI hôm nay; nếu tài chính bị
   **restate**, dòng ở `eff_date` cũ mang giá trị đã restate ⇒ look-ahead restatement. Lớp này áp
   cho MỌI consumer của `fa_ratings_8l`, không riêng file này, và không rẻ để sửa.
5. **Lãi vay tính `r/252` mỗi PHIÊN** (`simulate_holistic_nav.py:883`) trong khi lãi margin thực tế
   chạy theo ngày LỊCH (365). VN có ~248-250 phiên/năm ⇒ tổng tích luỹ ≈ đúng (sai số <1% của chi
   phí lãi). Không phải FAIL, nhưng không phải "theo lịch" như §Backtest yêu cầu.

---

## 4. Cái gì CHƯA quét — nói thẳng

- **`backtest_recovery_alloc.py` + `backtest_recovery_alloc_2011.py`** (#23): 2 file `backtest_*.py`
  DUY NHẤT còn được `data/results_registry.md` trích. **Chưa mở.** Hết ngân sách lượt này.
- **44 file `backtest_*.py` còn lại** — CỐ Ý không quét (registry không trích ⇒ không ai đọc số).
  Nhưng chúng vẫn là mẫu để chép: nếu ai copy một chuỗi return từ đó, lỗi tái sinh.
- **~20 worktree `wt-*/`** chứa bản sao `simulate_holistic_nav.py`/`dividend_adjusted_return.py`
  (`grep` thấy ở `mike/.claude/worktrees/*`, `wt-1540947310874198108/`…). Không quét. Mọi fix ở
  canonical KHÔNG tự lan tới đó.
- **`trading_bot/`** (đường thực thi live, thuộc Mafee) và **`webui/`** — ngoài phạm vi dispatch.
- **`custom30v_hybrid.py`**, `pt_v23_lagqual_research.py`, `c1_shadow_paper.py`,
  `lag_liq_ledger.py` — đều đọc `lag_edge_health.csv` hoặc dựng lại rổ; **cùng phơi nhiễm FAIL-C**
  mà tôi chưa xác minh từng file.
- **Chưa đo lượng** cho FAIL-C (tác động CAGR), FAIL-A, FAIL-B, FAIL-D (chính xác). Ba cái đều cần
  1 leg engine ⇒ job riêng.
- **Không kiểm** được (e) cho `fa_ratings_8l`/`universe_pit` ở tầng dữ liệu: cả hai là snapshot
  dựng lại, không có bản lưu theo vintage để so.

---

## 5. Bất biến CHƯA có selfcheck cưỡng chế → đề xuất cụ thể

Hiện trạng: **không có selfcheck nào** canh 6 bất biến này. Cái duy nhất tồn tại
(`basket_return_leg_oshares_selfcheck.py`, `basket_price_basis_selfcheck.py`) chỉ phủ đúng chuỗi
vừa bị vá, tức luật này chỉ được cưỡng chế ở nơi nó đã cắn.

| Bất biến | Selfcheck đề xuất | Assertion |
|---|---|---|
| (f) annualize | `bin/annualization_basis_selfcheck.py` | AST-scan mọi `.py` tính CAGR: **cấm** `yrs = N/252` khi N là số dòng return; ép `(t_last − t_first).days/365.25`. Ratchet baseline như `tz_anchor_gate.py`. Fire ĐÚNG `bootstrap_nav.py:51` + `dsr_pbo_annex.py:142` ở HEAD. |
| (c) dòng tiền | `bin/nav_flow_term_selfcheck.py` | `nav_history_{acct}.csv` phải CÓ cột `net_flow_vnd`; `nav_period_returns.compute_period_returns` phải trừ nó; assert: inject flow=+200tr giữa kỳ ⇒ `return_pct` KHÔNG đổi. **Chặn được FAIL-H trước lần nạp/rút đầu.** |
| (e) chuỗi as-of | `bin/asof_label_selfcheck.py` | Với mọi CSV production dán nhãn ngày mà giá trị là hàm của tương lai: assert `label_date ≥ ngày cuối của dữ liệu tạo ra giá trị đó`. Fire đúng `lag_edge_health.csv` (nhãn `entry` vs `entry+25`). |
| (b) adj-vs-thô | mở rộng `basket_price_basis_selfcheck.py` | Grep-gate toàn repo: **cấm** `Volume*Close`, `Volume_3M_P50*Close`, `Close*OShares` trong biểu thức TIỀN/ADV/mcap-weight. Fire đúng `pt_v23:895`. |
| (d) số CP đúng ngày | `bin/oshares_exdate_join_selfcheck.py` | Assert join `OShares` theo ex-date, không theo `fin.ftime`; **cấm `.bfill()`** trên cột số lượng PIT. Fire đúng `custom_basket.py:255`/`:1166`. |
| (a) — **lỗ hổng gốc** | `bin/level_series_invariant_selfcheck.py` | Với mọi chuỗi LEVEL nạp vào engine: assert `level_t/level_{t-1}` không có bước nhảy trùng ranh giới quý ở >k tên (dấu vân tay chính xác của bug custom30V). **Đây là selfcheck mà `self-check 0 VND` không bao giờ thay được (§0).** |

**Khuyến nghị thứ tự:** (1) `nav_flow_term_selfcheck` — duy nhất chạm tiền thật và chặn được lỗi
TRƯỚC khi nó nổ; (2) `annualization_basis_selfcheck` — rẻ nhất, cơ học tuyệt đối, sửa được số pin
KB ngay; (3) `asof_label_selfcheck` — bắt FAIL-C và cả lớp của nó.

---

## 6. Môi trường & khả năng tái lập

- Repo `WorkingClaude` @ `a808a613` (main, sau merge custom30V), đọc-chỉ, không sửa file nào.
- Phép đo CAGR + gate-flip: `$DNA_PYEXE` = `/home/trido/thanhdt/wc_venv/bin/python`.
- CSV đo: `data/v23_..._exp_pin_retleg_flat_univpit.csv` (post-fix) và `..._exp_ctrl_retleg_legacy_univpit.csv`
  (pre-fix). Phép tính của tôi tái lập ĐÚNG cả hai số pin (24,3775% / 28,8627%) ⇒ khớp engine.
- Đo DY: `bq query --use_legacy_sql=false`, project `lithe-record-440915-m9`. (Query đầu tiên hỏng
  đúng bẫy CLAUDE.md #2 — tên bảng `ticker` trùng tên cột `ticker`; phải alias.)
- Phạm vi bằng chứng: **điều hướng cấu trúc + 4 phép đo số**. KHÔNG có leg engine nào được chạy lại
  ⇒ mọi tác động CAGR của FAIL-A/B/C/D là **chưa đo**, không phải "nhỏ".
