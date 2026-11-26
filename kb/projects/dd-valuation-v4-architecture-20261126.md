# Kiến trúc DD & Mô hình Định giá v4 (Spec khoá từ `/grill-me`, 2026-11-26)

> Tài liệu thiết kế đã chốt qua 9 nhánh phỏng vấn `/grill-me` (ngày 26/11/2026). Đây là đặc tả kiến trúc chuẩn cho Phase 0 (công cụ & sửa lỗi cơ học), Phase 1 (`PRELOCK` nghiên cứu định lượng `DS-RIM + 4-Factor r_i + V_mkt`), Phase 2 (kiểm toán `quant-skeptic` & hợp nhất DD/Engine) và Phase 3 (nâng cấp production).

---

## 1. Bối cảnh & Chẩn đoán vấn đề hiện tại

- **Sổ DD sống (`kb/dd_price_zones.json`, 26/11/2026)**: 181 dòng / 36 mã; **31/36 (86,1%) đang `REFUTED_OPEN`**, chỉ **5/36 (13,9%) `CONFIRMED`**; `price_ref/center` trung vị `1,097` (61,1% mã có giá trên tâm). Nhiều ca phản biện đúng về khoảng trống công bố của doanh nghiệp nhưng chặn dây chuyền nâng cấp `LAG_DD_REQUIRE_CONFIRMED = True`.
- **Khoảng cách giá ↔ tâm mô hình định lượng (`S1-D0` & `c_models2.py`)**: ~51% phương sai `Var(ln(P/V))` trong `D0` là hiệu ứng cố định bền vững theo mã gồm:
  1. **Dirty-surplus & vốn hoá cổ phần**: trích quỹ KTPL (5–15% LNST), phát hành tăng vốn pha loãng (`FLC/HAI/ART/KSA`), chi phí `XDCB` kéo ROE vận hành xuống giả tạo.
  2. **Lệch cấu trúc chi phí vốn cross-sectional**: chiết khấu phẳng `r = 12,25%/13,5%` phạt quá nặng nhóm compounder trả tiền đều (`VCB/FPT/PAT/BMP/NT2`) so với lãi huy động và mức độ rủi ro thực.
  3. **Lỗi bucket trong `c_models2.py`**: `MULT/HEDf/META` đang gom theo `fa_ratings_8l.route` khiến **1.026/1.306 mã (78,5%) rơi vào chung một rổ `COMPOUNDER`**.
  4. **Mispricing đảo chiều thật (signal alpha)**: phần sai lệch còn lại cần giữ nguyên, không được "kéo tâm về giá bằng residual" kiểu `G1/REL` (vốn làm tăng tỉ lệ cắt nhau lên ~85% nhưng làm sụt CAGR từ `15,0% → 8,7%/năm`).

---

## 2. 9 Quyết định Thiết kế đã Khoá

| Nhánh | Lựa chọn chốt | Nội dung đặc tả |
|---|---|---|
| **1. Bản chất của Tâm** | **`[1] + [3]`** | Trụ cột chính là **Giá trị Cân bằng Cấu trúc VN (`V*`)** — mù giá của chính mã $i$, dùng $r_{i,t}$ 4 nhân tố và điều chỉnh dirty-surplus (`DS-RIM`) + hai túi tiền cổ tức/lợi nhuận giữ lại. Đi kèm **Giá thị trường hàm ý (`V_mkt`)** — mô hình hedonic & bội số cross-sectional theo `ICB3/4` để phân rã `P/V* = (V_mkt/V*) × (P/V_mkt)`. |
| **2. Tiêu chuẩn hội tụ 3–5 năm** | **`[1]`** | `V*` được nghiệm thu bằng **Tam giác Hội tụ Kinh tế (Economic Convergence Triad)** thay vì đếm chạm giá đơn thuần; `V_mkt` được đánh giá riêng theo độ khớp thị trường ở khung 1–3 năm. |
| **3. Chi phí vốn $r_{i,t}$** | **`[1]`** | Hợp nhất Engine & DD dưới công thức `r_{i,t} = Deposit-Rate Anchor + 4-Factor Structural Spread`, ước lượng Leave-One-Ticker-Out trên IS embargo và khoá thành dải điểm minh bạch `~[10,0% – 15,5%]`. **Cấm cộng thanh khoản vào $r_i$** (thanh khoản giữ riêng ở luật V3). DD giữ `V1 = 13,5%` cho tới khi Phase 1 qua `quant-skeptic CONFIRMED`. |
| **4. Dữ liệu `DS-RIM`** | **`[3]`** | **Pipeline định lượng chỉ dùng dữ liệu chuẩn hoá sẵn trong kho local** (`bq_cache`, `fiinprox_bank_ratios_quarterly`, `fiinprox_oshares_pit`, `forensic_flags`, `corp_actions`, `research_frozen/dcf_v31_inputs/out`) — không phụ thuộc API bên thứ 3. Các mục Thông tư 200 đọc sâu PDF (`CIP 242`, `HTM 123`, `KTPL 353` chính xác, room ngoại live) thuộc tầng **DD từng mã**. |
| **5. Tầng Catalyst & Timing** | **`[1]`** | Tách rời hoàn toàn khỏi `V*`. Ban đầu hiển thị song song (`P/V*`, `P/V_mkt`, `accS/hi52`/COD dự án) + chấm điểm giấy (`paper scorecard`) trước khi xem xét cổng cứng. |
| **6. Nút thắt Skeptic & `REFUTED_OPEN`** | **`[1]`** | Tách `fundamental-skeptic` chế độ `DD_GENERAL` thành 2 trục độc lập: `model_integrity` (`CONFIRMED|REFUTED`) vs `disclosure_gap_tier` (`LOW|MEDIUM|HIGH` + `disclosure_gap_items[]`). Gộp điều chỉnh Bậc A/B vào kịch bản trọng số `model.py`; cho phép `zone_low_eff` dịch hai chiều có kiểm soát cho riêng mục Bậc A (`center_adj_tier_a_up=true`). |
| **7. Tinh gọn báo cáo & Cổng cơ học** | **`[1]`** | Tóm tắt đầu báo cáo chỉ còn **3 Trụ cột + Trạng thái Catalyst**; đẩy các dòng gây nhiễu (`C4`, `D2`, `V_dài` FCFE, `E16 KHÔNG CHẮC`) xuống log JSON nội bộ. Bật ngay 3 cổng cơ học Phase 0 (`dd_skeptic_run.py`, `dd_blind_valuer_run.py`, `dd_accounting_reconcile.py` + `holding_sotp`). |
| **8. Phễu DD & Trần ngành** | **`[1]`** | **Phễu DD 2 làn**: *Lane A* (chuẩn bị sẵn 25–30 Compounder/Moat hàng đầu định kỳ hàng năm trước khi có hoảng loạn) + *Lane B* (sàng lọc sau BCTC bằng `V*`, `V_mkt`, `accS/hi52`). Thêm **cảnh báo tập trung ngành 8–10% NAV** theo nhóm `ICB4` hẹp trong `dd_price_zone_watch.py`. |
| **9. Phạm vi triển khai ngay** | **`[1]`** | Khoá spec này + hoàn tất Phase 0 (code + 3-TZ selfcheck + `.proposed/.diff` chưa ghi đè file live) + tạo `PRELOCK.md` & `DATA_SPEC.md` cho Phase 1 (chưa chạy backtest). |

---

## 3. Chi tiết Kỹ thuật Cốt lõi

### 3.1. Mô hình Song trụ (`V*` + `V_mkt`) & Tam giác Hội tụ Kinh tế (3–5Y)

$$
\frac{P_{i,t}}{V^*_{i,t}} = \underbrace{\frac{V_{\text{mkt}, i, t}}{V^*_{i,t}}}_{\text{kỳ vọng thị trường / định giá cơ bản}} \times \underbrace{\frac{P_{i,t}}{V_{\text{mkt}, i, t}}}_{\text{sai lệch nội ngành ngắn-trung hạn}}
$$

1. **Tiêu chuẩn nghiệm thu `V*` (3–5 năm, bắt buộc đạt đồng thời 4 chỉ tiêu trên OOS)**:
   - **Total-Return Convergence**: tỷ lệ `(P_{t+h} + CumDiv_{t..t+h}) / V*_t` đi vào vùng `[0,90; 1,10]` trong `h ∈ [36, 60]` tháng tăng rõ rệt so với baseline `D0`.
   - **Price-Led Convergence (chống target drift)**: tỷ trọng đóng gap đến từ **giá $P$ di chuyển về $V^*_0$ đạt `≥ 70%`**, và `Corr(Δln V*, Δln P) < 0,25` (giá hội tụ vì thị trường định giá lại, không phải mô hình chạy theo giá).
   - **Giảm phương sai cố định theo mã**: tỷ trọng `Var_ticker(ln(P/V*))` giảm từ mức nền **`51%` (`D0`) xuống `< 30%`**.
   - **Bảo toàn Alpha đầu tư**: `OOS CAGR ≥ S1-D0 (~14,5%+/năm)` với kiểm định year-block bootstrap (`B = 2000`, PIT sạch).
2. **Tiêu chuẩn `V_mkt` (hiện đại hoá từ `c_models2.py`)**: thay nhóm `fa_ratings_8l.route` bằng phân cấp **ICB4 → ICB3 → ICB2** (hồi quy co rút/shrinkage theo cỡ mẫu tối thiểu), đo độ khớp cross-sectional R² và cắt giá 1–3 năm.

### 3.2. Chi phí vốn cấu trúc 4 nhân tố (`r_{i,t}`)

$$
r_{i,t} = r_{\text{anchor}}(\text{deposit\_rate}_t) + \sum_{k=1}^{4} w_k \, \tilde{x}_{i,t}^{(k)}, \quad \text{bị chặn trong } [10{,}0\%; 15{,}5\%]
$$

- **4 nhân tố khoá trước (CHỈ từ kho dữ liệu local)**:
  1. **Ổn định dòng tiền cổ tức tiền mặt** (`Dividend_Min3Y`, chuỗi chi trả tiền mặt thực): cổ tức tiền ổn định ⇒ $r$ thấp hơn.
  2. **Chu kỳ ROE & Rủi ro sụt giảm** (`ROE_Min3Y/5Y`, độ biến động biên LN, downside beta trên IS).
  3. **Sức mạnh bảng cân đối / Moat tài chính** (`NetCash/Equity` cho phi tài chính; `CASA`, `LLR`, `NPL nhóm 3-5` từ `fiinprox_bank_ratios_quarterly` cho ngân hàng).
  4. **Độ khan hiếm / quy mô cấu trúc** (proxy quy mô & cơ cấu sở hữu ổn định có sẵn cục bộ — **KHÔNG dùng thanh khoản ADV/Amihud trong $r_i$** để tránh đếm hai lần với V3).
- Trọng số $w_k$ bị ràng buộc dấu (`monotone ridge`, ước lượng Leave-One-Ticker-Out trên IS 2014–2020), không bao giờ fit theo giá mục tiêu của từng mã.

### 3.3. Tầng Catalyst & Quy mô vị thế tư vấn (Advisory Tranches)

| Trạng thái định giá (`V*`, `V_mkt`) | Catalyst (`accS` / `hi52` / COD) | Khuyến nghị kích thước tư vấn (không auto-order) |
|---|---|---|
| `P ≤ 0,85 × V*` & `model_integrity = CONFIRMED` | Chưa kích hoạt | Thăm dò **`~1% NAV`** (hoặc chờ tại Bậc 1 nếu thanh khoản đủ) |
| `P ≤ 0,85 × V*` & `model_integrity = CONFIRMED` | Kích hoạt (`accS` cải thiện / vượt điểm bẻ dòng tiền / COD) | Giải ngân chuẩn **`2–4% NAV`** theo luật V8 (đơn vị tham chiếu `POS_PCT = 0,03`) |
| `P > V*` nhưng `P < V_mkt` | Bất kỳ | Cờ **"Bong bóng định giá theo bội số ngành"** — không mở mới |

### 3.4. Chuẩn hoá báo cáo DD mới (**3 Trụ cột + Catalyst**)

Bản tóm tắt đầu báo cáo DD chuẩn hoá còn 4 dòng/khối ngắn:
1. **Trụ cột 1 — `V*` & Bảng điều kiện đổi số**: tâm trọng số kịch bản + vùng + độ nhạy dải `r_i` + bảng mốc dữ kiện sắp tới làm dịch tâm.
2. **Trụ cột 2 — Sàn bảo vệ (Cổ tức tiền mặt / Tài sản thanh lý ròng)**.
3. **Trụ cột 3 — Tham chiếu thị trường (`V_mkt` cùng `ICB3/4` + Reverse-DCF kỳ vọng đang ẩn trong giá)**.
4. **Trụ cột 4 — Trạng thái Catalyst & Cổng giải ngân (`accS`, `hi52`, COD dự án, Bậc 1/2, cảnh báo ngành)**.
*(Các dòng `C4`, `D2`, `V_dài` FCFE và `E16 KHÔNG CHẮC` chuyển xuống log JSON nội bộ phục vụ audit nghiên cứu, không bày ở đầu báo cáo NĐT/user).*

---

## 4. Lộ trình 4 Pha & Vị trí File Triển khai

| Pha | Hạng mục chính | Đường dẫn trọng yếu | Trạng thái |
|---|---|---|---|
| **Phase 0 (Ngay)** | Spec kiến trúc; patch `dd_skeptic_run.py`, `dd_price_zone_watch.py`; tạo `dd_blind_valuer_run.py`, `dd_accounting_reconcile.py`; mở rộng `dd_assumptions_v1.json` (`holding_sotp`); `.proposed/.diff` cho skill & agent; `PRELOCK.md` & `DATA_SPEC.md` | `bin/dd_*`, `kb/schemas/dd_assumptions_v1.json`, `agents/Mike/proposals_20261126/`, `agents/Taylor/research/dcf_vn_v4_dsrim_20261126/` | Đang thực thi trong gói này |
| **Phase 1 (Nghiên cứu)** | Chạy `DS-RIM + 4-Factor r_i + V_mkt` trên IS (2014–2020) và đánh giá OOS (2021–2026) đúng theo `PRELOCK.md` | `agents/Taylor/research/dcf_vn_v4_dsrim_20261126/` | Chưa chạy (đợi sau Phase 0) |
| **Phase 2 (Phản biện & Thử nghiệm)** | Kiểm toán `quant-skeptic` (mục tiêu `CONFIRMED`), rà soát lại 31 mã `REFUTED_OPEN` bằng quy trình 2 trục + gộp kịch bản Tier A/B | `kb/dd_price_zones.json`, `dd_*` | Sau Phase 1 `CONFIRMED` |
| **Phase 3 (Nâng cấp Live)** | Sau khi user duyệt `.diff` và `quant-skeptic CONFIRMED`: áp `SKILL.md` / `fundamental-skeptic.md`, chuyển `V1` sang dải 4-Factor `r_i`, kích hoạt `DD_ASSUMPTIONS_LINT_ENFORCE_FROM` và cân nhắc bật `LAG_DD_REQUIRE_CONFIRMED = True` | `~/.claude/...`, `bin/dd_assumptions_lint.py`, `trading_bot/plan.py` | Chờ duyệt riêng từ user |
