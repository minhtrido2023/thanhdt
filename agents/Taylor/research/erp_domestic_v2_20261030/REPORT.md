# ERP nội địa vòng 2 + đo ảnh hưởng nếu đổi quy ước DCF của fleet
Job `Taylor_20261030_041731` · 30/10/2026 · chỉ nghiên cứu + patch ở nhánh riêng (KHÔNG merge, KHÔNG sửa main, KHÔNG đặt lệnh).
PREREG v2 `2e67a6de7` (11:21:54 ICT, trước mọi số v2) · patch `f3f756256` nhánh `session/erp-domestic-dcf-20261030`
(worktree `/home/trido/thanhdt/wt-erp-domestic-dcf-20261030`). Tái lập 2 múi giờ: `SELFCHECK.md`.
Nhãn: [BQ] đo trong phiên từ BigQuery/cache · [SRC] có nguồn · [UL] ước lượng. Số: `run_v2_stdout.txt`, `run_imp_stdout.txt`, `out_*.csv`.

## Kết luận trước

1. **ERP nội địa: điểm luật chính 5,42%, nhưng KHÔNG bền ⇒ báo dạng KHOẢNG 5,22–6,15%** (dải rộng D1–D4: 3,38–6,54).
   - Luật khai trước: C = ½·TB(D1, D2) + ½·TB(D3, D4); D3/D4 = TB của 3 cửa sổ cố định (2011→, 2014→, 2016-07→), mỗi cửa sổ tổng hợp hình học/số học theo Blume, T = 10 năm.
   - D1 3,38 (ngầm định value-driver) · D2 6,54 (E/P + π) · D3 6,32 (lịch sử, bỏ tái định giá) · D4 5,46 (lịch sử).
   - Không đạt tiêu chí bền ±0,5pp vì trục hình học/số học: thuần số học **+0,73**. Các trục còn lại đều trong ±0,5.
   - Ke tương ứng (rf 6,75):

     | β | Khoảng trung tâm | Điểm luật 5,42 | Giá trị code 5,5 | Dải D |
     |---|---|---|---|---|
     | 1,0 | 11,97–12,90 | 12,17 | **12,25** | 10,13–13,29 |
     | 1,1 | 12,49–13,52 | 12,72 | 12,80 | 10,46–13,95 |
     | 1,2 | 13,02–14,13 | 13,26 | 13,35 | 10,80–14,60 |

   - So với vòng 1 (5,05, Ke β1,1 12,3): trung tâm **lên khoảng 0,4pp**. Ba nguyên nhân: không còn chọn một cửa sổ, có thành phần số học, và họ ngầm định được tính vào trung tâm.
   - 15,8% (Damodaran) vẫn nằm trên đầu cao ⇒ giữ nhãn "góc nhìn nước ngoài".
2. **Đổi r và g_T CÙNG LÚC gần như trung tính về mức. Đổi riêng r thì không.** Khung `domestic_v2`: r = 6,75 + 5,5 = 12,25% (hằng), g_T = min(CPI + GDP, 5,5%). Rổ universe_pit 29/10, 145 mã tính được [BQ]:

   | Khung | FV trung vị so với hiện hành | % RẺ | Lật RẺ→ĐẮT / ĐẮT→RẺ | Cờ RICH SÂU (MoS < −100%) |
   |---|---|---|---|---|
   | Hiện hành (r 13,9 = lãi huy động 7,4 + 6,5; g_T 7,4) | — | 66,9 | — | 27 |
   | **domestic_v2, ERP 5,5** | **−1,4%** | 65,5 | 2 / 0 (CSV, CTR, MoS ≈ 0) | 27 (không đổi) |
   | domestic_v2, đầu dưới 5,22 | +2,9% | 68,3 | 0 / 2 | 26 |
   | domestic_v2, đầu trên 6,15 | −10,4% | 60,7 | 9 / 0 | 32 |
   | **CHỈ đổi r, g_T vẫn cap 7,4** | **+34,9%** | 75,2 | 0 / 12 | 21 |

   - Lý do trung tính: code hiện hành đã cap g_T ở đúng lãi huy động, nên r − g_T = ERP = 6,5pp. Khung mới có r − g_T = 6,75pp, gần như bằng.
   - Bội số Gordon đúng code, (1+g)/(r−g): 16,52× → 15,63× (−5,4%). Phần giảm này gần như bù hết phần tăng do chiết khấu giai đoạn 1 ở r thấp hơn.
3. **Thứ hạng, IC và custom30V không đổi.**
   - 51 quý 2014–2026: tương quan hạng MoS giữa khung cũ và mới **≥ 0,9999 ở mọi quý** (min 0,99989). IC 4 quý 0,059 (IS 0,047 / OOS 0,071) **giống nhau** ở cả 4 khung.
   - %RẺ TB lịch sử: 59,0 → 58,0 (domestic_v2), 54,5 (đầu trên).
   - `custom30_yield_labels.py` **không phụ thuộc** `dcf_valuation`: nó gọi thẳng `deposit_rate_vn.consumer_deposit_rate`, mà patch không đụng.
   - Overlay DCF trong `custom_basket.py` mặc định TẮT; grep không thấy nơi production nào đặt `BASKET_DCF_MODE`.
4. **Đường tiền ở ERP 5,5: 0 thay đổi hành vi** trên danh mục và plan live.
   - Phạm vi đo: 37 mã (nắm giữ SpaceX ∪ ZaloPay theo `dnse_raw` 29/10, lệnh mua trong plan 10/2026, rổ custom30V 05/08). 14 mã tính được DCF; 23 mã còn lại là tài chính hoặc FCFE ≤ 0.
   - Ở ERP 5,5 và ở đầu dưới: 0/14 lật status, 0 đổi robust. Cờ RICH SÂU chỉ có MCH, không đổi.
   - Ở đầu trên 6,15:
     - PNJ (custom30V) và VNM (plan mua) lật RẺ→ĐẮT, cả hai không robust (MoS −0,9% / −6,2%).
     - VGC (custom30V) sang RICH SÂU (−105%).
   - DCF không chặn lệnh cứng ở đâu cả. Nó đổi hành vi qua 2 cửa:
     - Cờ DD `DCF_RICH` của LAG (`lag_dd_pack.py`) cần ack.
     - Plan mua RICH SÂU + robust phải có `dcf_override_reason` (`strategies.py:148`, `plan.py:35`).
   - Mức rủi ro: thấp ở ERP 5,5 và đầu dưới; vừa ở đầu trên.
5. **g_T 5,5% là giả định HỘI TỤ dài hạn, lịch sử không đỡ cho nó. Dù vậy nó vẫn là hướng thận trọng đúng.**
   - Đạt: (i) 5,5 ≤ GDP danh nghĩa dài hạn 9,66 (CPI 5 năm 3,44 + GDP thực 15 năm 6,22, đúng hàm code dùng).
   - Không đỡ: (ii) EPS danh nghĩa trên 1 đơn vị VNINDEX tăng **8,7% / 10,3% / 12,3%/năm** (2011→ / 2014→ / 2016-07→) [BQ]. Lịch sử nghiêng về g cao hơn.
   - Đỡ: (iii) chỉ **39,4%** mã phi tài chính (42,1% vốn hoá) có ROE5Y ≥ r 12,25%; ROE5Y trung vị 9,75%. Với đa số mã, tăng trưởng thêm phá giá trị. FCFE của code không trừ tái đầu tư theo g_T (RONIC ngầm định = ∞), nên g_T thấp là chỉnh thận trọng.
   - **Không được giữ g_T 7,4 khi hạ r.** Đó là dòng "chỉ đổi r", FV +35%.
6. **Khuyến nghị:**
   - Patch sẵn sàng để user duyệt: knob `DCF_RATE_FRAME=domestic_v2`, mặc định `legacy` byte-identical.
   - Nếu duyệt: dùng ERP 5,5 (r 12,25) + g_T 5,5 **trong cùng một knob**.
   - Dải báo cáo Ke β1,1 là 12,5–13,5%, không phải một điểm.
   - **Không khẳng định 5,5 là "đúng" hơn 6,15.** Khác biệt giữa hai mức chính là trục hình học/số học, dữ liệu VN không phân xử được.
   - Cần quant-skeptic xét lại trước khi wire.

## Điểm yếu (hai chiều)

**Có thể làm ERP THẤP quá** (các trục đẩy LÊN, `out_v2_robustness.csv`):
- Thuần số học +0,73.
- Luật trung vị v1 +0,47.
- Blume T = 5: +0,40.
- D1 dùng ROE trọng số vốn chủ +0,22 (D1-ew = 4,26 so với 3,38). Nếu coi D1-ew là cặp nhất quán với E/P tổng hợp thì trung tâm khoảng 5,64.
- Bỏ cửa sổ 2011→ +0,21.
- Vấn đề peso: VN là thị trường "sống sót", và ERP đo được chỉ có 10–16 năm.

**Có thể làm ERP CAO quá** (đẩy XUỐNG):
- Thuần hình học −0,20. Bỏ 2014→ hoặc bỏ 2016-07→: −0,11.
- D2 giả định RONIC = Ke, trong khi ROE trung vị 9,75% < Ke, nên D2 6,54 lạc quan.
- Cả 3 cửa sổ đều bỏ 2008–2010: không có chân lãi huy động, và giai đoạn đó có ERP âm. Cửa sổ 2014→ và 2016-07→ là 10–13 năm EPS tăng 10–12%/năm.

**Bất định chung:**
- CI 90% bootstrap ERP số học là ±5pp (vòng 1).
- PREREG v2 **không mù**. Mọi số cấp cửa sổ đã có từ vòng 1, và tôi đã nhẩm trước rồi ghi vào PREREG §0: C ≈ 5,4, không bền. Kết quả thật là 5,424 và khoảng 5,22–6,15, khớp dự đoán.
- Cái được khoá trước là **luật**, không phải dữ liệu.

**Điểm yếu của phép đo ảnh hưởng:**
- Snapshot chỉ có 1 ngày (29/10).
- Giá dùng là `Price` BQ 29/10, không phải giá DNSE live.
- Danh sách live lấy từ log positions và plan tháng 10, không mô phỏng lại sinh plan.
- IC tính trên universe_pit phi tài chính, không phải rổ rating ≤ 3 của Study B đã pin. Mã mất dữ liệu kỳ sau bị loại, nên có survivorship nhẹ.
- Bản chụp `ticker_financial` dùng `time` = ngày công bố (PIT theo docstring code), không kiểm lại.

## 1. ERP v2 (`out_v2_implied.csv`, `out_v2_robustness.csv`)

**Cửa sổ lịch sử** (chân Big-4 12M; assert trùng byte `out_erp_history.csv` vòng 1):

| Cửa sổ | N năm | G | A | Tái định giá/năm | rf TB | Trọng số A (Blume T = 10) | D3 cửa sổ | D4 cửa sổ |
|---|---|---|---|---|---|---|---|---|
| 2011→ | 15,82 | 3,73 | 5,51 | −0,25 | 7,24 | 0,393 | 5,17 | 4,92 |
| 2014→ | 12,83 | 6,19 | 8,04 | −0,50 | 6,18 | 0,239 | 6,56 | 6,06 |
| 2016-07→ | 10,33 | 5,89 | 7,83 | −1,83 | 6,19 | 0,035 | 7,22 | 5,40 |
| **TB** | | | | | | | **6,32** | **5,46** |

**Độ nhạy** (mỗi dòng đổi một trục; C luật chính = 5,424):

| Biến thể | C | Lệch |
|---|---|---|
| R1 bỏ 2011→ | 5,64 | +0,21 |
| R2 bỏ 2014→ | 5,32 | −0,11 |
| R3 bỏ 2016-07→ | 5,32 | −0,11 |
| R4 thuần hình học | 5,22 | −0,20 |
| **R5 thuần số học** | **6,15** | **+0,73** |
| R6 Blume T = 5 | 5,83 | +0,40 |
| R7 D1 ROE trọng số vốn chủ | 5,64 | +0,22 |
| R8/R9 g của D1 4,25 / 6,75 | 5,37 / 5,46 | −0,05 / +0,03 |
| R10/R11 π của D2 4,0 / 4,5 | 5,36 / 5,49 | ±0,06 |
| R12 trung vị 4 số (luật v1) | 5,89 | +0,47 |
| R13 chỉ họ lịch sử (ngoài tiêu chí) | 5,89 | +0,47 |
| R14 chỉ họ ngầm định (ngoài tiêu chí) | 4,96 | −0,47 |
| V1 tái tạo đặc tả vòng 1 (ngoài tiêu chí) | 5,05 | −0,38 |

Kiểm Ke(β1) = 12,17 so với lãi cho vay TB 10,7 [SRC thứ cấp VNF]: đạt.

## 2. Sửa sai sót vòng 1 (theo quant-skeptic)

- **Bội số terminal:**
  - Vòng 1 ghi 15,4 / 19,8 / 15,9. Đó là 1/(r−g), lại ở r 11,8.
  - Đúng theo code (`_fv_per_share`, (1+g)/(r−g)), đều ở r 12,25 (`out_v2_terminal_multiple.csv`):

    | Khung | Bội số | So với hiện hành |
    |---|---|---|
    | Hiện hành | 16,52× | — |
    | Chỉ đổi r, g_T cap lãi huy động | 22,14× | +34,0% |
    | Chỉ đổi r, g_T cap rf_c 6,75 | 19,41× | +17,5% |
    | domestic_v2 đầu dưới | 16,30× | −1,4% |
    | domestic_v2 ERP 5,5 | 15,63× | −5,4% |
    | domestic_v2 đầu trên | 14,26× | −13,7% |
- **r nhất quán:** mọi bảng v2 dùng r = 6,75 + 5,50 = **12,25** (không còn cặp 11,75 / 11,8).
- **D1 với ROE trọng số vốn chủ:**
  - ROE trung vị 10,7% so với trọng số vốn chủ 12,6–14,8% tuỳ rổ.
  - D1-ew = **4,26**, ở dạng độ nhạy R7.
  - Skeptic báo 3,58 cho thay đổi này. Chênh nhau vì tôi áp ROE-ew cho cả 5 ước lượng (`out_v2_implied.csv`).
- **Lệch OShares, gửi data-ops (liệt kê, không sửa):**
  - Cách lọc: hệ số điều chỉnh giá 30/06→29/10 < 0,93, nhưng OShares tăng chưa tới 95% mức kỳ vọng. Ra **30 mã ứng viên** (`out_imp_oshares_flags.csv`).
  - Lưu ý: một số mã có thể là cổ tức tiền lớn, không phải chia tách. Cần data-ops xác minh.
  - Đáng chú ý:
    - **TCB** 0,667 / ×1,00 (kỳ vọng ×1,50).
    - **DGC** 0,829 / ×1,00 (kỳ vọng ×1,206).
    - **TV1** 0,928 / ×1,00 (đang nắm).
    - KSV ×1,50 (kỳ vọng ×1,58).
    - HUB ×1,05 (kỳ vọng ×1,135).
  - `ticker_financial.OShares` (nguồn `fair_value` dùng) cũng chưa đổi với DGC, TCB, TV1.
  - Nếu số cổ phần DGC thật sự ×1,206 thì MoS DGC 0,56 → **0,47** (tính tay), vẫn RẺ.

## 3. Đo ảnh hưởng (`impact_v2.py`; gọi chính `fair_value` + `classify_dcf`, đổi khung bằng monkeypatch trong tiến trình)

- **Snapshot 29/10:**
  - 336 mã universe_pit, 145 tính được.
  - NOT_COMPUTED: 72 CF_OA_3Y ≤ 0, 59 tài chính, 57 FCFE ≤ 0, 3 thiếu lịch sử.
  - Bảng ở mục Kết luận 2 (`out_imp_asof_summary.csv`, chi tiết từng mã ở `out_imp_asof_per_ticker.csv`).
  - Ở ERP 5,5, FV đổi **gần đồng đều**: p10–p90 từ −1,68% đến −1,42%.
- **Lịch sử 51 quý** (`out_imp_history_summary.csv`, `out_imp_history_quarterly.csv`):
  - %RẺ TB: hiện hành 59,0 · đầu dưới 59,4 · ERP 5,5 58,0 · đầu trên 54,5.
  - IC 1 quý 0,020 và IC 4 quý 0,059, giống nhau ở cả 4 khung. Chênh IC so với hiện hành = 0,000.
  - Tương quan hạng MoS ≥ 0,9999 mọi quý.
  - r hiện hành dao động 11,2–14,0% theo lãi huy động. r mới là hằng. Vì g_T cũ cũng chạy theo lãi huy động nên hai thứ bù nhau: %RẺ ở ERP 5,5 lệch 0 đến −3,8pp so với hiện hành ở mọi quý.
- **Live** (`out_imp_live.csv`): xem Kết luận 4.

**Bản đồ call-site** (grep `dcf_valuation|fair_value(|classify_dcf|discount_rate(` 30/10, bỏ worktree; xác nhận bằng grep, không chỉ srcwalk):

| Loại | File:dòng | Đổi hành vi ở ERP 5,5? |
|---|---|---|
| Đường tiền: cờ, không chặn cứng | `trading_bot/strategies.py:41-91` `_dcf_check_for_order` (fair_value + classify_dcf ⇒ `dcf_check` trong plan) | Status đổi ở 2/145 mã knife-edge; live 0 |
| Đường tiền | `trading_bot/strategies.py:148-152` + `plan.py:35`: RICH SÂU robust phải có lý do override | Universe 27→27; live 0 |
| Đường tiền | `mike/bin/lag_dd_pack.py:244-249,472-561`: cờ DD `DCF_RICH` khi MoS < −100% | Universe 27→27; live 0 |
| Audit | `trading_bot/executor.py:1281` bus `dcf-rich-fill` (chỉ log) | Theo status |
| Hiển thị | `send_plan_report.sh:900-1073`, `eod_trading_report.sh:442-467`, `trading_bot/due_diligence.py:1028-1036`, `alphalens_report.py:180`, `converge_report.py:200-207`, `sector_lens_monitor.py:513`, `mike/bin/sector_valuation_lens.py:119`, `dc_book_waterfall_paper.py:736-755` (paper) | Số MoS giảm khoảng 1,4% FV |
| Gián tiếp | `dcf_refresh_gate.py:101` (theo lãi huy động; dưới v2 thành recompute vô hại) | Không |
| Selfcheck sẽ hỏng nếu bật knob TOÀN CỤC | `cctg_deposit_wiring_selfcheck.py:200-265`, `cctg_tier2_series_selfcheck.py:510` (assert r theo lãi huy động) | Khi bật phải chạy chúng với `legacy` hoặc sửa assert |
| Nghiên cứu | `custom_basket.py:878-906` (overlay TẮT), `dcf_fv_sens_cache.py:26-44`, `dcf_backtest.py`, `dcf_rate_robustness.py` (monkeypatch r), `dcf_earning_power.py:53` (**rf = r − erp ⇒ sai nghĩa dưới v2: ra 5,75**), `dcf_earning_power_test.py:113`, `data/fscore_c30v_20260801/custom_basket_fsx.py`, `mike/agents/Taylor/exp_capit*/` | Không phải production |
| Không phụ thuộc | `custom30_yield_labels.py`, `rating_8l.py` (gọi `consumer_deposit_rate` trực tiếp) | Không đổi |

## 4. DGC tầng A (`out_v2_dgc.csv`; `model_ke.py` 29/10, β 1,11, g 3%)

Tái lập r7 ở Ke 14,9: **21.407 / 32.925 / 41.779, EV 29.817, lệch 0**.

| Ke | DCF nghịch / cơ sở / thuận | EV |
|---|---|---|
| 12,55 (đầu dưới) | 23.791 / 36.902 / 47.424 | 31.542 |
| **12,77 (luật chính)** | **23.516 / 36.442 / 46.772** | **31.343** |
| 12,86 (ERP 5,5) | 23.415 / 36.274 / 46.533 | 31.271 |
| 13,58 (đầu trên) | 22.619 / 34.946 / 44.648 | 30.695 |

Dải EV do Ke chỉ khoảng 850 đ/cp, nhỏ hơn nhiều so với bất định dự phòng R1/R2 (6.065). Ke không phải biến quyết định cho DGC.

## 5. Patch (nhánh `session/erp-domestic-dcf-20261030`, commit `f3f756256`, CHƯA merge)

`git diff --numstat main f3f756256`: `dcf_valuation.py` +26/−0, `dcf_rate_frame_selfcheck.py` +91 (mới).
```diff
+RATE_FRAMES = ("legacy", "domestic_v2")
+RATE_FRAME = os.environ.get("DCF_RATE_FRAME", "legacy")
+if RATE_FRAME not in RATE_FRAMES:
+    raise ValueError(...)
+RF_DOMESTIC = 6.75; ERP_DOMESTIC = 5.5; G_T_DOMESTIC = 0.055
 def discount_rate(asof, erp=ERP):
+    if RATE_FRAME == "domestic_v2":
+        return (RF_DOMESTIC + ERP_DOMESTIC + (erp - ERP)) / 100.0
 ...
+        elif mode == "cap_rf" and RATE_FRAME == "domestic_v2":
+            g = min(cpi + gdp, G_T_DOMESTIC)
```
- Một knob đổi r và g_T **cùng lúc**. Không có đường nào để đổi riêng r.
- Mặc định `legacy`. Lùi bằng cách bỏ biến env.
- Knob sai làm ValueError lúc import. Consumer đường tiền import trong try, nên rơi về NOT_COMPUTED.
- Selfcheck PASS ở UTC và Kiritimati:
  - (a) mặc định và `legacy` cho output trùng byte main (md5 `4c0cf6e6…`, 336 mã).
  - (b) `domestic_v2` khớp mô phỏng 145/145.
  - (c) DGC r7 tái lập 21.407 / 32.925 / 41.779 / 29.817.
  - (d) knob sai làm ValueError.
  - (c) không phải kiểm knob, vì `model_ke.py` không import `dcf_valuation`.
- **Trước khi bật cần:**
  - (1) user duyệt;
  - (2) quant-skeptic;
  - (3) xử lý 2 selfcheck CCTG và `dcf_earning_power.py:53`;
  - (4) cập nhật skill due-diligence dòng 30 (vùng Ke) và docstring `ERP`.

## Nguồn
- Cache vòng 1 `../erp_domestic_20261030/data/` (md5 trong SELFCHECK v1).
- `data/` v2 (`fetch_v2.py`): `close_qe.csv`, `oshares_check.csv` [BQ `tav2_bq.ticker`], `fin_snapshot.parquet` (từ `data/bq_cache/ticker_financial.parquet` md5 `03ee922e…`).
- Positions `data/execution_logs/dnse_raw_2026-10-29.jsonl` (lọc theo `account_no`), `data/trade_plans/plan_*_2026-10-*.json`, `data/custom30v_8l_publish.csv`.
- Lãi cho vay [SRC thứ cấp] VNF 21/09/2026.
